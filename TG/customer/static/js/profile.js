function enableEditing(event) {
    event.stopPropagation(); // Prevent triggering the profile picture click
    console.log("Edit button clicked!");

    var inputs = document.querySelectorAll('.profile-form input, .profile-form textarea');

    // Loop through all input fields and make them editable, except phone number and email
    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].name !== 'phone_number' && inputs[i].name !== 'email') {
            inputs[i].removeAttribute('readonly'); // Enable editing
            console.log(inputs[i].name + " is now editable.");

            // Show the .location-info element related to this field (if present)
            var formRow = inputs[i].closest('.form-row');
            if (formRow) {
                var locationInfo = formRow.querySelector('.location-info');
                if (locationInfo) {
                    locationInfo.style.display = 'block'; // Show the location button
                    console.log("Location button displayed for " + inputs[i].name);
                }
            }
        }
    }

    // Show the save button after enabling editing
    document.querySelector('.save-button').style.display = 'inline-block';

    // Hide the edit profile button to prevent duplicate editing attempts
    document.querySelector('.edit-profile-button').style.display = 'none';
}
// Function to preview the uploaded profile image
function previewImage(event) {
    var reader = new FileReader();
    reader.onload = function () {
        var output = document.getElementById('profileImage');
        output.src = reader.result; // Set the image src to the uploaded file
    };
    reader.readAsDataURL(event.target.files[0]); // Read the uploaded image file
}

// Function to get the user's current location and set it in the respective field
function getLocation(fieldId) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var latitude = position.coords.latitude;
            var longitude = position.coords.longitude;

            // Use the Google Maps API to reverse geocode the coordinates into an address
            var apiKey = 'AIzaSyD2aKVzC3za4z7PzGuiHh0evvFdx4agki0'; // Replace with your actual Google Maps API key
            var apiUrl = `https://maps.googleapis.com/maps/api/geocode/json?latlng=${latitude},${longitude}&key=${apiKey}`;

            // Fetch the location data from Google Maps API
            fetch(apiUrl)
                .then(response => response.json())
                .then(data => {
                    if (data.status === "OK") {
                        var address = data.results[0].formatted_address; // Get the formatted address
                        document.getElementById(fieldId).value = address; // Set the field value to the address
                    } else {
                        alert("Unable to retrieve location.");
                    }
                })
                .catch(error => {
                    console.error("Error fetching location:", error);
                    alert("An error occurred while retrieving the location.");
                });
        }, function() {
            alert("Geolocation service failed.");
        });
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}
