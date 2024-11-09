let map, directionsService, directionsRenderer, stepIndex = 0;

        // Initialize Google Maps API and Autocomplete
        function initMap() {
            directionsService = new google.maps.DirectionsService();
            directionsRenderer = new google.maps.DirectionsRenderer();

            map = new google.maps.Map(document.getElementById('map'), {
                center: { lat: 20.5937, lng: 78.9629 }, // Center of India
                zoom: 6
            });

            directionsRenderer.setMap(map);

            initAutocomplete();
        }

        function initAutocomplete() {
            const fromInput = document.getElementById('from-location');
            const toInput = document.getElementById('to-location');
            const viaInput1 = document.getElementById('via-location-1');

            new google.maps.places.Autocomplete(fromInput);
            new google.maps.places.Autocomplete(toInput);
            new google.maps.places.Autocomplete(viaInput1);
        }

        google.maps.event.addDomListener(window, 'load', initMap);

        function nextStep() {
            if (stepIndex === 0) {
                const fromLocation = document.getElementById('from-location').value;
                const toLocation = document.getElementById('to-location').value;
                if (!fromLocation || !toLocation) {
                    alert('Please enter both From and To locations.');
                    return;
                }
                updateBookingSummary();
            } else if (stepIndex === 2) {
                if (!validateStep3()) {
                    return;
                }
                // Call the AJAX function to submit the booking details
                submitBooking();
                return;
            }
            stepIndex++;
            updateStepVisibility();
        }

        function prevStep() {
            if (stepIndex > 0) {
                stepIndex--;
                updateStepVisibility();
            }
        }

        function updateStepVisibility() {
            const steps = document.querySelectorAll('.step');
            steps.forEach((step, index) => {
                step.classList.toggle('active', index === stepIndex);
            });
        }

        function addViaField() {
            const viaContainer = document.getElementById('via-container');
            const newViaIndex = viaContainer.querySelectorAll('.via-input').length + 1;
            const viaInputHTML = `
                <div class="via-input">
                    <input type="text" id="via-location-${newViaIndex}" name="via-location" placeholder="Enter via location">
                    <span class="remove-via" onclick="removeViaField(this)">X</span>
                </div>`;
            viaContainer.insertAdjacentHTML('beforeend', viaInputHTML);

            new google.maps.places.Autocomplete(document.getElementById(`via-location-${newViaIndex}`));
        }

        function removeViaField(element) {
            element.parentNode.remove();
        }

                function updateBookingSummary() {
            const fromLocation = document.getElementById('from-location').value;
            const toLocation = document.getElementById('to-location').value;
            const viaContainer = document.getElementById('via-summary-container');
            viaContainer.innerHTML = ''; // Clear previous via locations summary

            document.getElementById('summary-from').textContent = fromLocation;
            document.getElementById('summary-to').textContent = toLocation;

            // Handle via locations and show in summary if available
            const viaLocations = document.querySelectorAll('#via-container .via-input input');
            if (viaLocations.length > 0) {
                viaLocations.forEach((input, index) => {
                    if (input.value) {
                        const viaSummaryHTML = `
                            <div class="summary-details">
                                <span class="label">Via ${index + 1}:</span> <span class="info">${input.value}</span>
                            </div>`;
                        viaContainer.insertAdjacentHTML('beforeend', viaSummaryHTML);
                    }
                });
            }

            calculateRoute();
        }
        function calculateRoute() {
            const fromLocation = document.getElementById('from-location').value;
            const toLocation = document.getElementById('to-location').value;
        
            const waypoints = [];
            const viaLocations = document.querySelectorAll('#via-container .via-input input');
            viaLocations.forEach(input => {
                if (input.value) {
                    waypoints.push({ location: input.value, stopover: true });
                }
            });
        
            const request = {
                origin: fromLocation,
                destination: toLocation,
                waypoints: waypoints,
                travelMode: 'DRIVING'
            };
        
            directionsService.route(request, function(result, status) {
                if (status === 'OK') {
                    directionsRenderer.setDirections(result);
        
                    const route = result.routes[0].legs;
                    let totalDistance = 0, totalDuration = 0;
        
                    route.forEach(leg => {
                        totalDistance += leg.distance.value;
                        totalDuration += leg.duration.value;
                    });
        
                    // Log distance and duration to check values
                    console.log('Total Distance:', totalDistance); // Log distance in meters
                    document.getElementById('distance').textContent = (totalDistance / 1000).toFixed(2) + ' km'; // Convert to km
                    document.getElementById('duration').textContent = (totalDuration / 60).toFixed(2) + ' mins'; // Convert to minutes
                } else {
                    alert('Directions request failed due to ' + status);
                }
            });
        }
        function validateStep3() {
            const itemType = document.getElementById('item-type').value;
            const itemWeight = document.getElementById('item-weight').value;
            const itemImage = document.getElementById('itemImage').files.length;
            const laborYes = document.getElementById('laborYes').checked;
            const laborNo = document.getElementById('laborNo').checked;
            const laborCount = document.getElementById('laborCount').value;

            if (!itemType) {
                document.getElementById('nameError').style.display = 'inline';
                return false;
            }
            if (!itemWeight || itemWeight <= 0) {
                document.getElementById('loadError').style.display = 'inline';
                return false;
            }
            if (!itemImage) {
                document.getElementById('imageError').style.display = 'inline';
                return false;
            }
            if (!laborYes && !laborNo) {
                document.getElementById('laborError').style.display = 'inline';
                return false;
            }
            if (laborYes && !laborCount) {
                document.getElementById('laborCountError').style.display = 'inline';
                return false;
            }
            return true;
        }
        function getCurrentLocation(type) {
            if (navigator.geolocation) {
                // Set high accuracy options
                const options = {
                    enableHighAccuracy: true,   // Get more accurate results
                    timeout: 10000,             // Wait up to 10 seconds
                    maximumAge: 0               // No cached location
                };
        
                navigator.geolocation.getCurrentPosition(function(position) {
                    const latlng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
                    const geocoder = new google.maps.Geocoder();
        
                    geocoder.geocode({ 'location': latlng }, function(results, status) {
                        if (status === 'OK') {
                            const formattedAddress = results[0].formatted_address;
                            document.getElementById(`current-location-display-${type}`).textContent = 'Current location: ' + formattedAddress;
                            document.getElementById(`${type}-location`).value = formattedAddress;
                        } else {
                            alert('Geocode was not successful for the following reason: ' + status);
                        }
                    });
        
                }, function(error) {
                    // Handle errors
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
                }, options);
        
            } else {
                alert("Geolocation is not supported by this browser.");
            }
        }
        
        // Show/Hide labor count and message based on labor selection
document.getElementById('laborYes').addEventListener('change', function() {
    document.getElementById('laborCountGroup').style.display = 'block';
    document.getElementById('noLaborMessage').style.display = 'none';
});

document.getElementById('laborNo').addEventListener('change', function() {
    document.getElementById('laborCountGroup').style.display = 'none';
    document.getElementById('laborCount').value = ''; // Reset the labor count
    document.getElementById('noLaborMessage').style.display = 'block';
});

document.querySelector('button[type="submit"]').addEventListener('click', function(event) {
    event.preventDefault(); // Prevent the default form submission
    
    submitBooking(); // Call the AJAX function to submit the booking

});

function submitBooking() {
    const fromLocation = document.getElementById('from-location').value;
    const toLocation = document.getElementById('to-location').value;
    const itemWeight = document.getElementById('item-weight').value;
    const laborNeeded = document.querySelector('input[name="labor"]:checked')?.value;
    const laborCount = document.getElementById('laborCount').value || 0;
    const distance = document.getElementById('distance').textContent.split(' ')[0];

    const data = new FormData();
    data.append('from-location', fromLocation);
    data.append('to-location', toLocation);
    data.append('item-weight', itemWeight);
    data.append('labor', laborNeeded);
    data.append('laborCount', laborCount);
    data.append('distance', distance);

    fetch(calculatePriceUrl, {
        method: 'POST',
        body: data,
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            renderCategories(data.eligible_categories);
            stepIndex++;
            updateStepVisibility();
        } else {
            console.error(data.message);
            alert(data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}

function renderCategories(categories) {
    const container = document.getElementById('categories-container');
    container.innerHTML = ''; // Clear any existing content

    categories.forEach((category) => {
        const categoryHTML = `
            <div class="vehicle-item" data-category-id="${category.id}" data-category-name="${category.category}" data-total-price="${category.total_price}">
                <div class="image-container">
                    <img src="${category.image}" alt="${category.category}">
                </div>
                <div class="vehicle-info">
                    <span>${category.category}</span><br>
                    <span>Total Price: ₹${category.total_price.toFixed(2)}</span>
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', categoryHTML);
    });

    // Add click event listeners to each vehicle item for selection
    const vehicleItems = document.querySelectorAll('.vehicle-item');
    vehicleItems.forEach(item => {
        item.addEventListener('click', () => {
            // Remove 'selected' class from all items
            vehicleItems.forEach(i => i.classList.remove('selected'));
            // Add 'selected' class to the clicked item
            item.classList.add('selected');

            // Call printFormData after an item is selected
            printFormData();
        });
    });
}
function printFormData() {
    const selectedItem = document.querySelector('.vehicle-item.selected');
    const selectedCategoryId = selectedItem?.getAttribute('data-category-id');
    const selectedCategoryName = selectedItem?.getAttribute('data-category-name');
    const selectedCategoryPrice = selectedItem?.getAttribute('data-total-price');

    // You can now include these in the data to be sent on booking confirmation
    const bookingData = {
        fromLocation: document.getElementById('from-location').value,
        toLocation: document.getElementById('to-location').value,
        viaLocations: Array.from(document.querySelectorAll('.via-input input')).map(input => input.value).filter(Boolean),
        itemType: document.getElementById('item-type').value,
        itemWeight: document.getElementById('item-weight').value,
        labor: document.querySelector('input[name="labor"]:checked')?.value,
        laborCount: document.getElementById('laborCount').value,
        distance: document.getElementById('distance').textContent.split(' ')[0],
        duration: document.getElementById('duration').textContent,
        selectedCategoryId: selectedCategoryId,
        selectedCategoryName: selectedCategoryName,
        selectedCategoryPrice: selectedCategoryPrice // Capture the price
    };

    console.log("Booking Data:", bookingData);
    // You can then call the confirmBooking function or any other function to send this data
}
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function confirmBooking() {
    const fromLocation = document.getElementById('from-location').value;
    const toLocation = document.getElementById('to-location').value;
    const viaLocations = Array.from(document.querySelectorAll('input[name="via-location"]')).map(input => input.value);
    const itemType = document.getElementById('item-type').value;
    const itemWeight = document.getElementById('item-weight').value;
    const laborNeeded = document.querySelector('input[name="labor"]:checked')?.value || 'No';
    const laborCount = document.getElementById('laborCount').value || 0;
    const distance = document.getElementById('distance').textContent.split(' ')[0] || 0;
    const duration = document.getElementById('duration').textContent || 'Unknown';
    
    const selectedCategory = document.querySelector('.vehicle-item.selected');
    const selectedCategoryId = selectedCategory ? selectedCategory.getAttribute('data-category-id') : null;
    const selectedCategoryName = selectedCategory ? selectedCategory.querySelector('.vehicle-info span').textContent : 'Not Selected';
    const selectedCategoryPrice = selectedCategory ? selectedCategory.querySelector('.vehicle-info span:nth-of-type(2)').textContent.replace('Total Price: ₹', '') : 0;

    const itemImage = document.getElementById('itemImage').files[0];
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    if (!selectedCategoryId) {
        alert("Please select a vehicle category before confirming the booking.");
        return;
    }

    const data = new FormData();
    data.append('from-location', fromLocation);
    data.append('to-location', toLocation);
    data.append('via-location', JSON.stringify(viaLocations));
    data.append('item-type', itemType);
    data.append('item-weight', itemWeight);
    data.append('labor', laborNeeded);
    data.append('laborCount', laborCount);
    data.append('distance', distance);
    data.append('duration', duration);
    data.append('selected-category-id', selectedCategoryId);
    data.append('selected-category-name', selectedCategoryName);
    data.append('selected-category-price', selectedCategoryPrice);

    if (itemImage) {
        data.append('itemImage', itemImage);
    }

    fetch('/confirm-booking/', {
        method: 'POST',
        body: data,
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        if (result.success) {
            // Alert user and begin polling for driver response
            alert('Booking confirmed. Waiting for driver confirmation...');
            pollDriverStatus(result.order_id, csrftoken);  // Start polling for driver's response
        } else {
            alert(result.message);  // Handle failure message
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while processing the booking. Please try again.');
    });
}

function pollDriverStatus(orderId, csrftoken) {
    console.log("Polling started for order ID:", orderId);
    const url = `/check-driver-status/${orderId}/`;
    const pollingInterval = 5000;  // Poll every 5 seconds
    const maxPollingTime = 120000; // 2 minutes (in milliseconds)
    let elapsedTime = 0;  // Track the elapsed time
    let remainingTime = maxPollingTime / 1000;  // Initial time in seconds (120 seconds)

    // Show the loading spinner and start the timer
    document.getElementById('loading').style.display = 'block';

    // Function to update the timer display
    function updateTimer() {
        const minutes = Math.floor(remainingTime / 60);
        const seconds = remainingTime % 60;
        document.getElementById('timer').innerText = `Time remaining: ${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
        remainingTime--;
    }

    // Call updateTimer every second to update the countdown
    const timerInterval = setInterval(updateTimer, 1000);

    const interval = setInterval(() => {
        fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Driver response:', data);

            if (data.success) {
                if (data.status === 'accepted') {
                    clearInterval(interval);  // Stop polling
                    clearInterval(timerInterval);  // Stop the timer
                    document.getElementById('loading').style.display = 'none';  // Hide loading spinner
                    window.location.href = `/render-success-page/${orderId}/`;  // Redirect to success page
                } else if (data.status === 'rejected') {
                    clearInterval(interval);  // Stop polling
                    clearInterval(timerInterval);  // Stop the timer
                    document.getElementById('loading').style.display = 'none';  // Hide loading spinner

                    // Call the reassign vehicle function
                    reassignVehicle(orderId, csrftoken);
                } else {
                    console.log('Waiting for driver confirmation...');
                }
            } else {
                console.error('Error in response:', data.message);
            }
        })
        .catch(error => {
            console.error('Error during polling:', error);
            clearInterval(interval);
            clearInterval(timerInterval);  // Stop the timer
            document.getElementById('loading').style.display = 'none';  // Hide loading spinner
            alert('An error occurred while checking the driver response.');
        });

        // Increment the elapsed time by the polling interval
        elapsedTime += pollingInterval;

        // If the maximum polling time (2 minutes) has been reached
        if (elapsedTime >= maxPollingTime || remainingTime < 0) {
            clearInterval(interval);  // Stop polling after 2 minutes
            clearInterval(timerInterval);  // Stop the timer
            document.getElementById('loading').style.display = 'none';  // Hide loading spinner
            alert('No response from the driver. The booking has been rejected.');
        }
    }, pollingInterval);  // Poll every 5 seconds
}

function reassignVehicle(orderId, csrftoken) {
    const data = new FormData();
    data.append('order_id', orderId);

    fetch('/reassign-vehicle/', {
        method: 'POST',
        body: data,
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        if (result.success) {
            alert(result.message);  // Notify success
            // After successful reassignment, start polling for the new driver status
            pollDriverStatus(orderId, csrftoken);
        } else {
            alert(result.message);  // Notify failure
        }
    })
    .catch(error => {
        console.error('Error during vehicle reassignment:', error);
        alert('An error occurred while reassigning the vehicle. Please try again.');
    });
}