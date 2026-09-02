import sqlite3
import os


# ==========================================
# DATABASE PATH
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DB_PATH = os.path.join(
    BASE_DIR,
    "kashmir.db"
)


# ==========================================
# CONNECT
# ==========================================

connection = sqlite3.connect(DB_PATH)

cursor = connection.cursor()


# ==========================================
# DESTINATIONS
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS destinations (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    location TEXT,

    category TEXT,

    description TEXT,

    image TEXT,

    best_time TEXT

)
""")


# ==========================================
# ACTIVITIES
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS activities (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    destination_id INTEGER,

    name TEXT NOT NULL,

    category TEXT,

    description TEXT,

    season TEXT,

    FOREIGN KEY (
        destination_id
    )
    REFERENCES destinations(id)

)
""")


# ==========================================
# STAYS
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS stays (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    destination TEXT,

    type TEXT,

    category TEXT,

    description TEXT,

    image TEXT

)
""")


# ==========================================
# ITINERARIES
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS itineraries (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    days INTEGER,

    budget INTEGER,

    travelers INTEGER,

    starting_point TEXT,

    travel_style TEXT,

    interests TEXT,

    itinerary TEXT,

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP

)
""")


# ==========================================
# DESTINATION DATA
# ==========================================

destinations = [

    (
        "Srinagar",
        "Central Kashmir",
        "nature,culture",
        "The heart of Kashmir, famous for Dal Lake, gardens, houseboats and local culture.",
        "srinagar.jpg",
        "March to November"
    ),

    (
        "Gulmarg",
        "Baramulla",
        "nature,adventure",
        "A spectacular mountain destination known for snow, skiing and the Gulmarg Gondola.",
        "gulmarg.jpg",
        "December to March"
    ),

    (
        "Pahalgam",
        "Anantnag",
        "nature,adventure",
        "A peaceful valley surrounded by mountains, rivers and beautiful meadows.",
        "pahalgam.jpg",
        "April to October"
    ),

    (
        "Sonamarg",
        "Ganderbal",
        "nature,adventure",
        "A dramatic alpine destination surrounded by mountains, glaciers and trekking routes.",
        "sonamarg.jpg",
        "April to October"
    ),

    (
        "Doodhpathri",
        "Budgam",
        "nature,offbeat",
        "A peaceful meadow destination known for green landscapes and flowing streams.",
        "doodhpathri.jpg",
        "April to October"
    ),

    (
        "Gurez Valley",
        "Bandipora",
        "nature,offbeat,adventure",
        "A remote Himalayan valley surrounded by dramatic mountains and traditional villages.",
        "gurez.jpg",
        "May to October"
    )

]


cursor.executemany("""
INSERT OR IGNORE INTO destinations
(
    name,
    location,
    category,
    description,
    image,
    best_time
)
VALUES (?, ?, ?, ?, ?, ?)
""", destinations)


# ==========================================
# ACTIVITIES
# ==========================================

activities = [

    (1, "Shikara Ride", "culture", "Enjoy a traditional Shikara ride on Dal Lake.", "March-November"),

    (1, "Mughal Gardens", "culture", "Explore Kashmir's historic Mughal gardens.", "March-November"),

    (1, "Houseboat Stay", "culture", "Experience traditional accommodation on Dal Lake.", "March-November"),

    (2, "Gulmarg Gondola", "adventure", "Ride one of the world's highest cable cars.", "Year-round"),

    (2, "Skiing", "adventure", "Enjoy skiing during the winter season.", "December-March"),

    (2, "Snow Activities", "adventure", "Experience snow-covered mountain landscapes.", "December-March"),

    (3, "Betaab Valley", "nature", "Visit the beautiful Betaab Valley.", "April-October"),

    (3, "Aru Valley", "nature", "Explore the scenic Aru Valley.", "April-October"),

    (3, "River Activities", "adventure", "Enjoy activities around the Lidder River.", "April-October"),

    (4, "Mountain Walks", "nature", "Explore Sonamarg's alpine scenery.", "April-October"),

    (4, "Trekking", "adventure", "Explore mountain trails around Sonamarg.", "May-October"),

    (5, "Meadow Picnic", "nature", "Relax in the peaceful Doodhpathri meadows.", "April-October"),

    (6, "Village Exploration", "culture", "Experience traditional villages of Gurez.", "May-October"),

    (6, "Mountain Hiking", "adventure", "Explore the Himalayan landscape around Gurez.", "May-October")

]


cursor.executemany("""
INSERT OR IGNORE INTO activities
(
    destination_id,
    name,
    category,
    description,
    season
)
VALUES (?, ?, ?, ?, ?)
""", activities)


# ==========================================
# STAYS
# ==========================================

stays = [

    (
        "Dal Lake Houseboat",
        "Srinagar",
        "Houseboat",
        "luxury",
        "Traditional Kashmiri houseboat experience on Dal Lake.",
        "dal-lake.jpg"
    ),

    (
        "Gulmarg Mountain Stay",
        "Gulmarg",
        "Hotel",
        "luxury",
        "Mountain accommodation suitable for exploring Gulmarg.",
        "gulmarg.jpg"
    ),

    (
        "Pahalgam Homestay",
        "Pahalgam",
        "Homestay",
        "budget",
        "Comfortable local-style accommodation in Pahalgam.",
        "pahalgam.jpg"
    ),

    (
        "Srinagar City Stay",
        "Srinagar",
        "Hotel",
        "budget",
        "Convenient accommodation for exploring Srinagar.",
        "srinagar.jpg"
    ),

    (
        "Sonamarg Alpine Stay",
        "Sonamarg",
        "Hotel",
        "luxury",
        "Scenic accommodation near the Sonamarg landscape.",
        "sonamarg.jpg"
    ),

    (
        "Gurez Homestay",
        "Gurez Valley",
        "Homestay",
        "budget",
        "Local-style mountain accommodation in Gurez.",
        "gurez.jpg"
    )

]


cursor.executemany("""
INSERT OR IGNORE INTO stays
(
    name,
    destination,
    type,
    category,
    description,
    image
)
VALUES (?, ?, ?, ?, ?, ?)
""", stays)


# ==========================================
# SAVE
# ==========================================

connection.commit()

connection.close()


print("================================")
print("Kashmir AI database initialized!")
print("Database:", DB_PATH)
print("================================")