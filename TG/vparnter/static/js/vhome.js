let map;
let marker;

function initializeMap(latitude = 13.337779175436527, longitude = 77.11733714374941) {
    const mapContainer = document.getElementById('map');
    const mapOptions = {
        center: { lat: latitude, lng: longitude },
        zoom: 15
    };
    map = new google.maps.Map(mapContainer, mapOptions);
    marker = new google.maps.Marker({
        position: { lat: latitude, lng: longitude },
        map: map
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const vehicleImage = document.querySelector('.photo-container img');

    if (vehicleImage) {
        vehicleImage.addEventListener('click', () => {
            vehicleImage.classList.toggle('zoom-out');
        });
    }

    const activeRadio = document.getElementById('active');
    const inactiveRadio = document.getElementById('inactive');
    const additionalStatusDiv = document.getElementById('additional-status');

    if (activeRadio && inactiveRadio && additionalStatusDiv) {
        activeRadio.addEventListener('change', () => {
            additionalStatusDiv.style.display = activeRadio.checked ? 'block' : 'none';
        });
        inactiveRadio.addEventListener('change', () => {
            additionalStatusDiv.style.display = inactiveRadio.checked ? 'none' : 'block';
        });
    }

    const locationForm = document.getElementById('location-form');
    const locationInput = document.getElementById('location-input');
    const useCurrentLocationButton = document.getElementById('use-current-location');

    function setLocation(lat, lng, address) {
        locationInput.value = address;

        if (map) {
            map.setCenter({ lat, lng });
            marker.setPosition({ lat, lng });
        } else {
            initializeMap(lat, lng);
        }
    }

    if (locationForm) {
        locationForm.addEventListener('submit', (event) => {
            event.preventDefault();

            const formData = new FormData(locationForm);
            const newLocation = locationInput.value.trim();

            if (newLocation) {
                const geocoder = new google.maps.Geocoder();
                geocoder.geocode({ address: newLocation }, (results, status) => {
                    if (status === 'OK' && results[0]) {
                        const location = results[0].geometry.location;
                        setLocation(location.lat(), location.lng(), newLocation);

                        fetch(locationForm.action, {
                            method: 'POST',
                            body: formData,
                            headers: {
                                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                            }
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                alert('Location updated successfully!');
                                window.location.href = data.redirect_url;
                            } else {
                                alert('Failed to update location: ' + data.error);
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('There was an error updating the location.');
                        });
                    } else {
                        alert('Location not found');
                    }
                });

                locationInput.value = '';
            }
        });
    }

    if (useCurrentLocationButton) {
        useCurrentLocationButton.addEventListener('click', () => {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const lat = position.coords.latitude;
                        const lng = position.coords.longitude;
                        const geocoder = new google.maps.Geocoder();
                        geocoder.geocode({ location: { lat, lng } }, (results, status) => {
                            if (status === 'OK' && results[0]) {
                                const address = results[0].formatted_address;
                                setLocation(lat, lng, address);
                                locationInput.value = address;
                            } else {
                                alert('Unable to determine your location');
                            }
                        });
                    },
                    (error) => {
                        alert('Error getting your location: ' + error.message);
                    }
                );
            } else {
                alert('Geolocation is not supported by this browser.');
            }
        });
    }

    if (activeRadio && inactiveRadio && additionalStatusDiv) {
        additionalStatusDiv.style.display = activeRadio.checked ? 'block' : 'none';
    }
});
