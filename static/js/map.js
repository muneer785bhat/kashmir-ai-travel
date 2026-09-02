// =====================================
// KASHMIR INTERACTIVE MAP
// =====================================

const places = {

    srinagar: {
        name: "Srinagar",
        lat: 34.0837,
        lng: 74.7973,
        description: "The heart of Kashmir, famous for Dal Lake, gardens and houseboats.",
        category: "Lake • Gardens • Culture"
    },

    gulmarg: {
        name: "Gulmarg",
        lat: 34.0484,
        lng: 74.3805,
        description: "A beautiful mountain destination famous for snow, skiing and the Gondola.",
        category: "Snow • Skiing • Gondola"
    },

    pahalgam: {
        name: "Pahalgam",
        lat: 34.0161,
        lng: 75.3150,
        description: "A scenic valley surrounded by mountains, rivers and beautiful meadows.",
        category: "Valleys • Rivers • Trekking"
    },

    sonamarg: {
        name: "Sonamarg",
        lat: 34.3029,
        lng: 75.2931,
        description: "A spectacular mountain destination known for glaciers and alpine landscapes.",
        category: "Mountains • Glaciers • Adventure"
    },

    doodhpathri: {
        name: "Doodhpathri",
        lat: 33.8395,
        lng: 74.6590,
        description: "A peaceful meadow surrounded by green hills and flowing streams.",
        category: "Meadows • Streams • Nature"
    },

    gurez: {
        name: "Gurez Valley",
        lat: 34.6333,
        lng: 74.8333,
        description: "A remote Himalayan valley famous for dramatic mountains and traditional villages.",
        category: "Mountains • Villages • Offbeat"
    }

};


// =====================================
// CREATE MAP
// =====================================

const map = L.map("kashmirMap");


// OpenStreetMap tiles

L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        maxZoom: 18,
        attribution: "&copy; OpenStreetMap contributors"
    }
).addTo(map);


// Kashmir starting position

map.setView(
    [34.15, 74.85],
    8
);


// =====================================
// MARKERS
// =====================================

const markers = {};

Object.keys(places).forEach((id) => {

    const place = places[id];

    const marker = L.marker([
        place.lat,
        place.lng
    ]).addTo(map);


    marker.bindPopup(`
        <div class="map-popup">

            <h3>${place.name}</h3>

            <span>
                ${place.category}
            </span>

            <p>
                ${place.description}
            </p>

            <a href="/planner">
                Plan a trip →
            </a>

        </div>
    `);


    markers[id] = marker;

});


// =====================================
// DESTINATION LIST
// =====================================

const placeItems =
    document.querySelectorAll(".place-item");


placeItems.forEach((item) => {

    item.addEventListener("click", () => {

        const placeId =
            item.dataset.place;

        const place =
            places[placeId];

        if (!place) return;


        // Move map

        map.flyTo(
            [place.lat, place.lng],
            11,
            {
                duration: 1.2
            }
        );


        // Open popup

        markers[placeId].openPopup();


        // Highlight selected place

        placeItems.forEach((element) => {
            element.classList.remove("selected");
        });

        item.classList.add("selected");

    });

});


// =====================================
// SEARCH
// =====================================

const searchInput =
    document.getElementById("destinationSearch");

const searchBtn =
    document.getElementById("searchBtn");


function searchDestination() {

    const query =
        searchInput.value
        .trim()
        .toLowerCase();


    if (!query) return;


    const found =
        Object.keys(places).find((id) => {

            return (
                places[id].name
                .toLowerCase()
                .includes(query)
            );

        });


    if (found) {

        const place =
            places[found];


        map.flyTo(
            [place.lat, place.lng],
            11,
            {
                duration: 1.2
            }
        );


        markers[found].openPopup();

    } else {

        alert(
            "Destination not found. Try Srinagar, Gulmarg, Pahalgam, Sonamarg, Doodhpathri or Gurez."
        );

    }

}


searchBtn.addEventListener(
    "click",
    searchDestination
);


searchInput.addEventListener(
    "keydown",
    (event) => {

        if (event.key === "Enter") {

            searchDestination();

        }

    }
);