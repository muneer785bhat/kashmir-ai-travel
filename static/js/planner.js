// ==========================================
// KASHMIR AI TRIP PLANNER
// ==========================================


let days = 5;
let travelers = 2;
let travelStyle = "Balanced";


// ==========================================
// ELEMENTS
// ==========================================

const daysValue =
    document.getElementById("daysValue");

const travelersValue =
    document.getElementById("travelersValue");

const budgetInput =
    document.getElementById("budget");

const generateBtn =
    document.getElementById("generateBtn");

const itinerary =
    document.getElementById("itinerary");

const previewEmpty =
    document.getElementById("previewEmpty");

const dayList =
    document.getElementById("dayList");

const tripSummary =
    document.getElementById("tripSummary");

const resetBtn =
    document.getElementById("resetBtn");



// ==========================================
// DAYS CONTROLS
// ==========================================

document.getElementById("plusDays")
    .addEventListener("click", () => {

        if (days < 15) {
            days++;
            daysValue.textContent = days;
        }

    });


document.getElementById("minusDays")
    .addEventListener("click", () => {

        if (days > 1) {
            days--;
            daysValue.textContent = days;
        }

    });



// ==========================================
// TRAVELER CONTROLS
// ==========================================

document.getElementById("plusTravelers")
    .addEventListener("click", () => {

        if (travelers < 12) {
            travelers++;
            travelersValue.textContent = travelers;
        }

    });


document.getElementById("minusTravelers")
    .addEventListener("click", () => {

        if (travelers > 1) {
            travelers--;
            travelersValue.textContent = travelers;
        }

    });



// ==========================================
// TRAVEL STYLE
// ==========================================

const styleOptions =
    document.querySelectorAll(".style-option");


styleOptions.forEach(option => {

    option.addEventListener("click", () => {

        styleOptions.forEach(item => {
            item.classList.remove("active");
        });

        option.classList.add("active");

        travelStyle =
            option.dataset.style;

    });

});



// ==========================================
// DESTINATION DATA
// ==========================================

const destinations = [

    {
        name: "Srinagar",
        emoji: "🌊",
        description:
            "Explore Dal Lake, Shikara rides and the beautiful Mughal Gardens."
    },

    {
        name: "Gulmarg",
        emoji: "🏔️",
        description:
            "Enjoy breathtaking mountain views, snow activities and the famous Gondola."
    },

    {
        name: "Pahalgam",
        emoji: "🌲",
        description:
            "Discover peaceful valleys, rivers, meadows and scenic mountain trails."
    },

    {
        name: "Sonamarg",
        emoji: "🏔️",
        description:
            "Experience spectacular alpine landscapes, mountains and glacier views."
    },

    {
        name: "Doodhpathri",
        emoji: "🌿",
        description:
            "Relax among green meadows, streams and peaceful Himalayan scenery."
    },

    {
        name: "Gurez Valley",
        emoji: "🏡",
        description:
            "Discover remote mountain villages and dramatic Himalayan landscapes."
    }

];



// ==========================================
// GENERATE ITINERARY
// ==========================================

generateBtn.addEventListener(
    "click",
    generateItinerary
);


function generateItinerary() {

    const budget =
        Number(budgetInput.value) || 0;

    const startingPoint =
        document.getElementById(
            "startingPoint"
        ).value;


    const interests =
        Array.from(
            document.querySelectorAll(
                ".interest input:checked"
            )
        ).map(input => input.value);


    if (budget < 1000) {

        alert(
            "Please enter a valid budget."
        );

        return;
    }


    // Loading state

    generateBtn.disabled = true;

    generateBtn.innerHTML =
        `<span class="loading-spinner"></span>
         Creating your itinerary...`;


    setTimeout(() => {

        createItinerary(
            budget,
            startingPoint,
            interests
        );

        generateBtn.disabled = false;

        generateBtn.innerHTML =
            `<span>✦</span>
             Generate My Itinerary
             <span>→</span>`;

    }, 1200);

}



// ==========================================
// CREATE ITINERARY
// ==========================================

function createItinerary(
    budget,
    startingPoint,
    interests
) {

    previewEmpty.style.display =
        "none";

    itinerary.style.display =
        "block";


    // Summary

    tripSummary.innerHTML = `

        <div class="summary-item">

            <span>📅</span>

            <div>
                <small>Duration</small>
                <strong>${days} Days</strong>
            </div>

        </div>


        <div class="summary-item">

            <span>👥</span>

            <div>
                <small>Travelers</small>
                <strong>${travelers}</strong>
            </div>

        </div>


        <div class="summary-item">

            <span>💰</span>

            <div>
                <small>Budget</small>
                <strong>₹${budget.toLocaleString("en-IN")}</strong>
            </div>

        </div>


        <div class="summary-item">

            <span>🌿</span>

            <div>
                <small>Style</small>
                <strong>${travelStyle}</strong>
            </div>

        </div>

    `;


    // Choose destinations

    let route = [];

    if (startingPoint === "Jammu") {

        route.push(destinations[0]);

    } else {

        route.push(destinations[0]);

    }


    const remaining =
        destinations.slice(1);


    for (
        let i = 0;
        i < days - 1;
        i++
    ) {

        route.push(
            remaining[
                i % remaining.length
            ]
        );

    }


    // Build days

    dayList.innerHTML = "";


    route.forEach(
        (place, index) => {

            const dayNumber =
                index + 1;


            let activities =
                getActivities(
                    place.name,
                    interests
                );


            const dayCard =
                document.createElement(
                    "div"
                );

            dayCard.className =
                "day-card";


            dayCard.innerHTML = `

                <div class="day-number">

                    <span>DAY</span>

                    <strong>
                        ${dayNumber}
                    </strong>

                </div>


                <div class="day-content">

                    <div class="day-title">

                        <div>

                            <h3>
                                ${place.emoji}
                                ${place.name}
                            </h3>

                            <p>
                                ${place.description}
                            </p>

                        </div>

                    </div>


                    <div class="activities">

                        ${activities.map(
                            activity => `
                                <span>
                                    ${activity}
                                </span>
                            `
                        ).join("")}

                    </div>

                </div>

            `;


            dayList.appendChild(
                dayCard
            );

        }
    );


    // Scroll to itinerary

    setTimeout(() => {

        itinerary.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }, 200);

}



// ==========================================
// ACTIVITIES
// ==========================================

function getActivities(
    destination,
    interests
) {

    const activities = {


        Srinagar: [
            "🚤 Dal Lake Shikara",
            "🌳 Mughal Gardens",
            "🏠 Houseboat Experience"
        ],


        Gulmarg: [
            "🚠 Gondola Ride",
            "🏔️ Mountain Views",
            "🎿 Snow Adventure"
        ],


        Pahalgam: [
            "🌲 Valley Exploration",
            "🐎 Horse Riding",
            "🥾 Nature Walk"
        ],


        Sonamarg: [
            "🏔️ Mountain Views",
            "🥾 Scenic Walk",
            "📸 Photography"
        ],


        Doodhpathri: [
            "🌿 Meadow Walk",
            "💧 Stream Exploration",
            "📸 Photography"
        ],


        "Gurez Valley": [
            "🏡 Village Exploration",
            "🏔️ Himalayan Views",
            "📸 Photography"
        ]

    };


    return activities[
        destination
    ] || [
        "🌿 Explore",
        "📸 Photography",
        "🍽️ Local Food"
    ];

}



// ==========================================
// RESET
// ==========================================

resetBtn.addEventListener(
    "click",
    () => {

        itinerary.style.display =
            "none";

        previewEmpty.style.display =
            "flex";

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    }
);