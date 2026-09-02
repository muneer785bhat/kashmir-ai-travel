from flask import Flask, render_template, request, jsonify
import requests
import sqlite3
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from api.weather import get_weather
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# ==========================================
# DATABASE CONNECTION
# ==========================================
app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "dev-secret-change-this"
)


DATABASE = os.path.join(
    os.path.dirname(__file__),
    "database",
    "kashmir.db"
)
app.config["UPLOAD_FOLDER"] = os.path.join(
    os.path.dirname(__file__),
    "static",
    "images"
)

os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)


def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


# ==========================================
# BASIC PAGES
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/explore")
def explore():
    return render_template("explore.html")


@app.route("/planner")
def planner():
    return render_template("planner.html")

@app.route("/destinations")
def destinations():

    connection = get_db_connection()

    destinations_data = connection.execute(
        "SELECT * FROM destinations"
    ).fetchall()
    

    connection.close()

    return render_template(
        "destinations.html",
        destinations=destinations_data
    )
@app.route("/destination/<destination_name>")
def destination_detail(destination_name):

    connection = get_db_connection()

    destination = connection.execute(
        """
        SELECT *
        FROM destinations
        WHERE LOWER(name) = LOWER(?)
        """,
        (destination_name,)
    ).fetchone()

    if destination is None:

        connection.close()

        return "Destination not found", 404


    activities = connection.execute(
        """
        SELECT *
        FROM activities
        WHERE destination_id = ?
        """,
        (destination["id"],)
    ).fetchall()


    connection.close()


    return render_template(
        "destination_detail.html",
        destination=destination,
        activities=activities
    )

@app.route("/stays")
def stays():

    connection = get_db_connection()

    stays_data = connection.execute(
        """
        SELECT *
        FROM stays
        ORDER BY destination, name
        """
    ).fetchall()

    connection.close()

    return render_template(
        "stays.html",
        stays=stays_data
    )
# ==========================================
# ADMIN LOGIN
# ==========================================
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Local development credentials
        admin_username = "admin"
        admin_password = "KashmirAI@2026"

        if username == admin_username and password == admin_password:

            session["admin_logged_in"] = True

            return redirect(url_for("admin"))

        return render_template(
            "admin_login.html",
            error="Invalid username or password."
        )

    return render_template("admin_login.html")
# ADMIN LOGOUT
# ==========================================

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin_logged_in", None)

    return redirect(
        url_for("admin_login")
    )


# ==========================================
# ADMIN DASHBOARD
# ==========================================

@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    destination_count = connection.execute(
        "SELECT COUNT(*) FROM destinations"
    ).fetchone()[0]

    activity_count = connection.execute(
        "SELECT COUNT(*) FROM activities"
    ).fetchone()[0]

    stay_count = connection.execute(
        "SELECT COUNT(*) FROM stays"
    ).fetchone()[0]

    itinerary_count = connection.execute(
        "SELECT COUNT(*) FROM itineraries"
    ).fetchone()[0]

    destinations_data = connection.execute(
        """
        SELECT *
        FROM destinations
        ORDER BY name
        """
    ).fetchall()

    activities_data = connection.execute(
        """
        SELECT
            activities.*,
            destinations.name AS destination_name
        FROM activities
        LEFT JOIN destinations
            ON activities.destination_id = destinations.id
        ORDER BY destinations.name, activities.name
        """
    ).fetchall()

    stays_data = connection.execute(
        """
        SELECT *
        FROM stays
        ORDER BY destination, name
        """
    ).fetchall()

    connection.close()

    return render_template(
        "admin.html",
        destination_count=destination_count,
        activity_count=activity_count,
        stay_count=stay_count,
        itinerary_count=itinerary_count,
        destinations=destinations_data,
        activities=activities_data,
        stays=stays_data
    )

    # ==========================================

# ==========================================
# ADD DESTINATION
# ==========================================

@app.route("/admin/destinations/add", methods=["GET", "POST"])
def add_destination():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        best_time = request.form.get("best_time", "").strip()

        image = request.files.get("image")

        if not name:
            return render_template(
                "add_destination.html",
                error="Destination name is required."
            )

        image_filename = ""

        if image and image.filename:

            filename = secure_filename(
                image.filename
            )

            base, extension = os.path.splitext(
                filename
            )

            image_filename = (
                base.lower().replace(" ", "-")
                + extension.lower()
            )

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    image_filename
                )
            )

        connection = get_db_connection()

        connection.execute(
            """
            INSERT INTO destinations
            (
                name,
                location,
                category,
                description,
                best_time,
                image
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                location,
                category,
                description,
                best_time,
                image_filename
            )
        )

        connection.commit()
        connection.close()

        return redirect(
            url_for("admin")
        )

    return render_template(
        "add_destination.html"
    )
    
@app.route("/admin/destinations/edit/<int:destination_id>", methods=["GET", "POST"])
def edit_destination(destination_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    destination = connection.execute(
        "SELECT * FROM destinations WHERE id = ?",
        (destination_id,)
    ).fetchone()

    if destination is None:
        connection.close()
        return "Destination not found", 404

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        best_time = request.form.get("best_time", "").strip()

        image = request.files.get("image")

        image_filename = destination["image"]

        if image and image.filename:
            filename = secure_filename(image.filename)

            base, extension = os.path.splitext(filename)

            image_filename = (
                base.lower().replace(" ", "-")
                + extension.lower()
            )

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    image_filename
                )
            )

        connection.execute(
            """
            UPDATE destinations
            SET name = ?,
                location = ?,
                category = ?,
                description = ?,
                image = ?,
                best_time = ?
            WHERE id = ?
            """,
            (
                name,
                location,
                category,
                description,
                image_filename,
                best_time,
                destination_id
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("admin"))

    connection.close()

    return render_template(
        "edit_destination.html",
        destination=destination
    )
@app.route("/admin/activities/add", methods=["GET", "POST"])
def add_activity():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    destinations = connection.execute(
        """
        SELECT id, name
        FROM destinations
        ORDER BY name
        """
    ).fetchall()

    if request.method == "POST":

        destination_id = request.form.get("destination_id")
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        season = request.form.get("season", "").strip()

        if not destination_id or not name:
            connection.close()

            return render_template(
                "add_activity.html",
                destinations=destinations,
                error="Destination and activity name are required."
            )

        connection.execute(
            """
            INSERT INTO activities
            (destination_id, name, category, description, season)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                destination_id,
                name,
                category,
                description,
                season
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("admin"))

    connection.close()

    return render_template(
        "add_activity.html",
        destinations=destinations
    )
@app.route("/admin/activities/edit/<int:activity_id>", methods=["GET", "POST"])
def edit_activity(activity_id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    activity = connection.execute(
        """
        SELECT *
        FROM activities
        WHERE id = ?
        """,
        (activity_id,)
    ).fetchone()

    if activity is None:
        connection.close()
        return "Activity not found", 404

    destinations = connection.execute(
        """
        SELECT id, name
        FROM destinations
        ORDER BY name
        """
    ).fetchall()

    if request.method == "POST":

        destination_id = request.form.get("destination_id")
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        season = request.form.get("season", "").strip()

        connection.execute(
            """
            UPDATE activities
            SET destination_id = ?,
                name = ?,
                category = ?,
                description = ?,
                season = ?
            WHERE id = ?
            """,
            (
                destination_id,
                name,
                category,
                description,
                season,
                activity_id
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("admin"))

    connection.close()

    return render_template(
        "edit_activity.html",
        activity=activity,
        destinations=destinations
    )


@app.route("/admin/activities/delete/<int:activity_id>", methods=["POST"])
def delete_activity(activity_id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM activities
        WHERE id = ?
        """,
        (activity_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("admin"))

@app.route("/admin/destinations/delete/<int:destination_id>", methods=["POST"])
def delete_destination(destination_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    destination = connection.execute(
        "SELECT * FROM destinations WHERE id = ?",
        (destination_id,)
    ).fetchone()

    if destination is None:
        connection.close()
        return "Destination not found", 404

    connection.execute(
        "DELETE FROM destinations WHERE id = ?",
        (destination_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("admin"))    

@app.route("/assistant")
def assistant():
    return render_template("assistant.html")


@app.route("/weather")
def weather_page():
    return render_template("weather.html")

@app.route("/admin/stays/add", methods=["GET", "POST"])
def add_stay():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    destinations = connection.execute(
        """
        SELECT id, name
        FROM destinations
        ORDER BY name
        """
    ).fetchall()

    if request.method == "POST":

        destination = request.form.get("destination", "").strip()
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        price = request.form.get("price", "").strip()

        website_url = request.form.get("website_url", "").strip()
        booking_url = request.form.get("booking_url", "").strip()
        maps_url = request.form.get("maps_url", "").strip()

        if not destination or not name:
            connection.close()

            return render_template(
                "add_stay.html",
                destinations=destinations,
                error="Destination and stay name are required."
            )

        connection.execute(
            """
            INSERT INTO stays
            (
                destination,
                name,
                category,
                description,
                price,
                website_url,
                booking_url,
                maps_url
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                destination,
                name,
                category,
                description,
                price,
                website_url,
                booking_url,
                maps_url
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("admin"))

    connection.close()

    return render_template(
        "add_stay.html",
        destinations=destinations
    )
@app.route("/admin/stays/edit/<int:stay_id>", methods=["GET", "POST"])
def edit_stay(stay_id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    stay = connection.execute(
        """
        SELECT *
        FROM stays
        WHERE id = ?
        """,
        (stay_id,)
    ).fetchone()

    if stay is None:
        connection.close()
        return "Stay not found", 404

    destinations = connection.execute(
        """
        SELECT id, name
        FROM destinations
        ORDER BY name
        """
    ).fetchall()

    if request.method == "POST":

        destination = request.form.get("destination", "").strip()
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        price = request.form.get("price", "").strip()

        website_url = request.form.get("website_url", "").strip()
        booking_url = request.form.get("booking_url", "").strip()
        maps_url = request.form.get("maps_url", "").strip()

        if not destination or not name:
            connection.close()

            return render_template(
                "edit_stay.html",
                stay=stay,
                destinations=destinations,
                error="Destination and stay name are required."
            )

        connection.execute(
            """
            UPDATE stays
            SET destination = ?,
                name = ?,
                category = ?,
                description = ?,
                price = ?,
                website_url = ?,
                booking_url = ?,
                maps_url = ?
            WHERE id = ?
            """,
            (
                destination,
                name,
                category,
                description,
                price,
                website_url,
                booking_url,
                maps_url,
                stay_id
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("admin"))

    connection.close()

    return render_template(
        "edit_stay.html",
        stay=stay,
        destinations=destinations
    )
@app.route("/admin/stays/delete/<int:stay_id>", methods=["POST"])
def delete_stay(stay_id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM stays
        WHERE id = ?
        """,
        (stay_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("admin"))
# ==========================================
# LIVE WEATHER API
# ==========================================

@app.route("/api/weather/<city>")
def weather(city):

    try:

        weather_data = get_weather(city)

        return jsonify({
            "success": True,
            "data": weather_data
        })

    except Exception as e:

        print("Weather error:", e)

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==========================================
# AI TRIP PLANNER
# ==========================================
@app.route("/generate-itinerary", methods=["POST"])
def generate_itinerary():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "No trip information received."
        }), 400

    days = data.get("days", 5)
    budget = data.get("budget", 30000)
    travelers = data.get("travelers", 2)

    starting_point = data.get(
        "startingPoint",
        "Srinagar"
    )

    travel_style = data.get(
        "travelStyle",
        "Balanced"
    )

    interests = data.get(
        "interests",
        []
    )


    # ==========================================
    # READ DESTINATIONS FROM DATABASE
    # ==========================================

    connection = get_db_connection()

    destinations_data = connection.execute(
        """
        SELECT *
        FROM destinations
        """
    ).fetchall()


    # ==========================================
    # READ ACTIVITIES FROM DATABASE
    # ==========================================

    activities_data = connection.execute(
        """
        SELECT
            activities.*,
            destinations.name AS destination_name
        FROM activities

        JOIN destinations
        ON activities.destination_id = destinations.id
        """
    ).fetchall()


    connection.close()


    # ==========================================
    # FORMAT DATABASE INFORMATION
    # ==========================================

    destination_text = "\n".join(

        [
            f"""
Destination:
{destination['name']}

Location:
{destination['location']}

Category:
{destination['category']}

Description:
{destination['description']}

Best Time:
{destination['best_time']}
"""
            for destination in destinations_data
        ]

    )


    activity_text = "\n".join(

        [
            f"""
Destination:
{activity['destination_name']}

Activity:
{activity['name']}

Category:
{activity['category']}

Description:
{activity['description']}

Season:
{activity['season']}
"""
            for activity in activities_data
        ]

    )


    # ==========================================
    # GET LIVE WEATHER
    # ==========================================

    weather_cities = [
        "srinagar",
        "gulmarg",
        "pahalgam",
        "sonamarg",
        "doodhpathri",
        "gurez"
    ]


    weather_information = []


    for city in weather_cities:

        try:

            weather = get_weather(city)

            weather_information.append({

                "destination":
                    weather["city"],

                "temperature":
                    weather["temperature"],

                "condition":
                    weather["condition"],

                "description":
                    weather["description"],

                "humidity":
                    weather["humidity"],

                "wind":
                    weather["wind_speed"]

            })

        except Exception as e:

            print(
                f"Weather unavailable for {city}: {e}"
            )


    # ==========================================
    # WEATHER TEXT
    # ==========================================

    if weather_information:

        weather_text = "\n".join(

            [
                f"""
Destination:
{item['destination']}

Temperature:
{item['temperature']}°C

Condition:
{item['condition']}

Description:
{item['description']}

Humidity:
{item['humidity']}%

Wind:
{item['wind']} km/h
"""
                for item in weather_information
            ]

        )

    else:

        weather_text = (
            "Live weather is currently unavailable."
        )


    # ==========================================
    # OLLAMA PROMPT
    # ==========================================

    prompt = f"""
You are Kashmir AI, an expert travel planner
specializing in Jammu & Kashmir.

Create a realistic, personalized,
database-aware and weather-aware itinerary.


USER TRIP DETAILS

Duration:
{days} days

Budget:
₹{budget}

Travelers:
{travelers}

Starting Point:
{starting_point}

Travel Style:
{travel_style}

Interests:
{", ".join(interests)}


AVAILABLE KASHMIR DESTINATIONS

{destination_text}


AVAILABLE ACTIVITIES FROM OUR DATABASE

{activity_text}


LIVE WEATHER

{weather_text}


IMPORTANT RULES

1. Only recommend destinations from
   the available destination database.

2. Only recommend activities that appear
   in the available activities database.

3. Use the live weather information.

4. If weather is unsuitable for an outdoor
   activity, suggest another available activity.

5. Consider realistic travel time.

6. Do not put too many destinations
   into one day.

7. Respect the user's budget.

8. Prioritize the user's interests.

9. Consider activity season information.

10. Do not invent hotels, prices,
    phone numbers or booking availability.

11. Give approximate costs.

12. Make the itinerary practical.


OUTPUT FORMAT


# Your Kashmir Adventure

Give a short overview.


## Day 1 — Destination

### Morning
Activity

### Afternoon
Activity

### Evening
Activity

### Stay
Suggested accommodation area/type.

### Estimated Cost
Approximate cost.


Continue for every day.


## Weather Notes

Explain how weather affects the itinerary.


## Estimated Budget

- Accommodation
- Transport
- Food
- Activities
- Miscellaneous


## Travel Tips

Give practical travel advice.

Be friendly and helpful.
"""


    # ==========================================
    # CALL OLLAMA
    # ==========================================

    try:

        response = requests.post(

            "http://localhost:11434/api/generate",

            json={

                "model": "openai/gpt-oss-20b",

                "prompt": prompt,

                "stream": False

            },

            timeout=180

        )


        if response.status_code != 200:

            print(
                "Ollama error:",
                response.text
            )

            return jsonify({

                "success": False,

                "error":
                    "Ollama returned an error."

            }), 500


        result = response.json()


        itinerary = result.get(
            "response",
            ""
        )


        # ======================================
        # SAVE ITINERARY TO DATABASE
        # ======================================

        connection = get_db_connection()

        connection.execute(
            """
            INSERT INTO itineraries
            (
                days,
                budget,
                travelers,
                starting_point,
                travel_style,
                interests,
                itinerary
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                days,
                budget,
                travelers,
                starting_point,
                travel_style,
                ", ".join(interests),
                itinerary
            )
        )

        connection.commit()

        connection.close()


        return jsonify({

            "success": True,

            "itinerary":
                itinerary,

            "weather":
                weather_information

        })


    except requests.exceptions.ConnectionError:

        return jsonify({

            "success": False,

            "error":
                "Ollama is not running. "
                "Please start Ollama."

        }), 500


    except Exception as e:

        print(
            "Itinerary error:",
            e
        )

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500
# ==========================================
# AI CHAT ASSISTANT
# ==========================================

# ==========================================
# AI CHAT ASSISTANT
# ==========================================



# ==========================================
# AI CHAT ASSISTANT
# ==========================================

from groq import Groq


@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No message received."
            }), 400

        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({
                "success": False,
                "error": "Please enter a message."
            }), 400


        # ==========================================
        # GROQ API KEY
        # ==========================================

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            return jsonify({
                "success": False,
                "error": "Groq API key is not configured."
            }), 500


        # ==========================================
        # KASHMIR AI PROMPT
        # ==========================================

        prompt = f"""
You are Kashmir AI, a helpful and friendly travel
assistant specializing in Jammu & Kashmir.

Answer the user's question clearly and practically.

User question:
{user_message}

You can help with:

- Best places to visit
- Kashmir destinations
- Things to do
- Gulmarg activities
- Pahalgam activities
- Srinagar attractions
- Kashmir itineraries
- Budget trips
- Food
- Culture
- Accommodation areas
- Routes
- Best seasons

Rules:

1. Focus on Jammu & Kashmir.
2. Give useful and realistic information.
3. Do not invent hotel prices, phone numbers,
   booking availability or exact live conditions.
4. If something can change, mention that it
   should be verified.
5. For trip plans, use a simple day-by-day format.
6. Keep the answer concise and easy to read.
7. Answer the actual question directly.

Now answer the user.
"""


        # ==========================================
        # CALL GROQ
        # ==========================================

        client = Groq(
            api_key=api_key
        )


        completion = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[
                {
                    "role": "system",
                    "content":
                        "You are Kashmir AI, "
                        "a helpful Kashmir travel assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.6,

            max_completion_tokens=800,

            reasoning_effort="low"

        )


        # ==========================================
        # GET RESPONSE
        # ==========================================

        ai_response = ""

        if completion.choices:

            message = completion.choices[0].message

            if message.content:
                ai_response = message.content.strip()


        # ==========================================
        # EMPTY RESPONSE CHECK
        # ==========================================

        if not ai_response:

            print(
                "GROQ EMPTY RESPONSE:",
                completion
            )

            return jsonify({
                "success": False,
                "error":
                    "AI returned an empty response. "
                    "Please try again."
            }), 500


        # ==========================================
        # SUCCESS
        # ==========================================

        return jsonify({
            "success": True,
            "response": ai_response
        })


    except Exception as e:

        print(
            "GROQ CHAT ERROR:",
            str(e)
        )

        return jsonify({
            "success": False,
            "error":
                "Unable to connect to the AI service."
        }), 500
@app.route("/admin/update-stays-table")
def update_stays_table():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    columns = connection.execute(
        "PRAGMA table_info(stays)"
    ).fetchall()

    existing_columns = [column["name"] for column in columns]

    if "website_url" not in existing_columns:
        connection.execute(
            "ALTER TABLE stays ADD COLUMN website_url TEXT"
        )

    if "booking_url" not in existing_columns:
        connection.execute(
            "ALTER TABLE stays ADD COLUMN booking_url TEXT"
        )

    if "maps_url" not in existing_columns:
        connection.execute(
            "ALTER TABLE stays ADD COLUMN maps_url TEXT"
        )

    connection.commit()
    connection.close()

    return "Stays table updated successfully! You can now remove this route."
# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )