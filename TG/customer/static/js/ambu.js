let map, marker, autocomplete, geocoder;

function initMap() {
    const defaultLocation = { lat: 12.9716, lng: 77.5946 }; // Bangalore as fallback

    // Initialize the map
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 15,
        center: defaultLocation
    });

    // Initialize the marker
    marker = new google.maps.Marker({
        map: map,
        position: defaultLocation
    });

    // Initialize the geocoder
    geocoder = new google.maps.Geocoder();

    // Initialize the autocomplete for the accident-spot input
    autocomplete = new google.maps.places.Autocomplete(
        document.getElementById('accident-spot'),
        { types: ['geocode'] } // restrict to geolocation suggestions
    );

    // When a place is selected from the suggestions, update the map
    autocomplete.addListener('place_changed', function() {
        const place = autocomplete.getPlace();
        if (place.geometry) {
            const pos = {
                lat: place.geometry.location.lat(),
                lng: place.geometry.location.lng()
            };
            map.setCenter(pos);
            marker.setPosition(pos);
        } else {
            alert("No details available for the selected location.");
        }
    });

    // Event listener for 'Use Current Location' button
    document.getElementById('use-current-location').addEventListener('click', function () {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function (position) {
                const pos = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                map.setCenter(pos);
                marker.setPosition(pos);

                // Reverse geocode the current position to get the address
                geocoder.geocode({ location: pos }, function(results, status) {
                    if (status === "OK") {
                        if (results[0]) {
                            // Set the accident spot input field to the formatted address
                            document.getElementById('accident-spot').value = results[0].formatted_address;
                        } else {
                            alert("No results found");
                        }
                    } else {
                        alert("Geocoder failed due to: " + status);
                    }
                });
            }, function(error) {
                // Handle errors based on the error code
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        alert("User denied the request for Geolocation.");
                        break;
                    case error.POSITION_UNAVAILABLE:
                        alert("Location information is unavailable.");
                        break;
                    case error.TIMEOUT:
                        alert("The request to get user location timed out.");
                        break;
                    case error.UNKNOWN_ERROR:
                        alert("An unknown error occurred.");
                        break;
                }
            });
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('location-form').addEventListener('submit', function(event) {
        event.preventDefault();  // Prevent default form submission

        const location = document.getElementById('accident-spot').value;  // Get the value from the input
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;  // Get the CSRF token

        // Check if location is empty
        if (!location) {
            alert('Please enter a valid location.');
            return;  // Stop the submission if the location is empty
        }

        fetch('/submit-booking/', {  // Adjust this URL if needed
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken  // Include the CSRF token in the headers
            },
            body: JSON.stringify({
                'location': location
            })
        })
        .then(response => {
            if (response.ok) {
                return response.text();  // Parse the response as text (HTML)
            }
            throw new Error('Network response was not ok.');
        })
        .then(html => {
            // Directly write the response HTML to the document
            document.open();
            document.write(html);
            document.close();
        })
        .catch(error => {
            alert('Failed to submit the booking: ' + error.message);
            console.error('There was a problem with the fetch operation:', error);
        });
    });
});