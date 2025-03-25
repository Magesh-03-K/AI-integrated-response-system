function showFirstAidInstructions() {
    let emergencyType = document.getElementById("emergencySelect").value;
    let instructionsText = document.getElementById("instructionsText");

    let instructions = {
        "bleeding": "Apply direct pressure to stop bleeding. Use a clean cloth.",
        "burn": "Cool the burn under cold running water for 10 minutes.",
        "choking": "Perform abdominal thrusts (Heimlich maneuver).",
        "heartAttack": "Call emergency services immediately. Keep the person calm.",
        "fracture": "Immobilize the injured limb and seek medical help."
    };

    instructionsText.innerText = instructions[emergencyType] || "Please select an emergency.";
}

// Initialize Google Map
function initMap() {
    let map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: -34.397, lng: 150.644 },  // Default location
        zoom: 12
    });

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((position) => {
            let userLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            map.setCenter(userLocation);
        });
    }
}

// Find Nearby Emergency Services
function findNearbyServices() {
    let serviceType = document.getElementById("serviceType").value;

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((position) => {
            let userLocation = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);

            let map = new google.maps.Map(document.getElementById("map"), {
                center: userLocation,
                zoom: 14
            });

            let request = {
                location: userLocation,
                radius: '5000',  // Search in 5km range
                type: [serviceType]
            };

            let service = new google.maps.places.PlacesService(map);
            service.nearbySearch(request, (results, status) => {
                if (status === google.maps.places.PlacesServiceStatus.OK) {
                    results.forEach((place) => {
                        let marker = new google.maps.Marker({
                            position: place.geometry.location,
                            map: map,
                            title: place.name
                        });

                        let infoWindow = new google.maps.InfoWindow({
                            content: `<strong>${place.name}</strong><br>${place.vicinity}`
                        });

                        marker.addListener("click", () => {
                            infoWindow.open(map, marker);
                        });
                    });
                }
            });
        });
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

// Initialize the map when the window loads
window.onload = initMap;
