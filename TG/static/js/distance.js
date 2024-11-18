let map, directionsService, directionsRenderer;

function initMap() {
    let input1 = document.getElementById('from');
    let input2 = document.getElementById('to');

    let autocomplete1 = new google.maps.places.Autocomplete(input1);
    let autocomplete2 = new google.maps.places.Autocomplete(input2);

    let myLatLng = { lat: 13.345578148460678, lng:77.10429898214421 };

    let mapOptions = {
        center: myLatLng,
        zoom: 7,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
    };

    map = new google.maps.Map(document.getElementById('googleMap'), mapOptions);

    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer();
    directionsRenderer.setMap(map);
}

function CalcRoute() {
    let request = {
        origin: document.getElementById('from').value,
        destination: document.getElementById('to').value,
        travelMode: google.maps.TravelMode.DRIVING,
        unitSystem: google.maps.UnitSystem.IMPERIAL
    };

    directionsService.route(request, function (result, status) {
        const output = document.querySelector("#output");

        if (status === google.maps.DirectionsStatus.OK) {
            // Convert miles to kilometers
            const distanceInMiles = result.routes[0].legs[0].distance.value / 1609.34; // convert meters to miles
            const distanceInKm = (distanceInMiles * 1.60934).toFixed(2); // miles to km

            output.innerHTML =
                "<div class='alert alert-info'>From: " +
                document.getElementById("from").value +
                ". <br/> To: " +
                document.getElementById("to").value +
                ".<br/> Driving Distance: <i class='fas fa-road'></i> " +
                distanceInKm +
                " km.<br/> Duration: <i class='fas fa-hourglass-start'></i> " +
                result.routes[0].legs[0].duration.text +
                ".</div>";
            directionsRenderer.setDirections(result);
        } else {
            console.error("Directions request failed due to " + status);
            output.innerHTML =
                "<div class='alert alert-danger'><i class='fas fa-exclamation-triangle'></i> Could not retrieve directions. Error: " + status + "</div>";
        }
    });
}