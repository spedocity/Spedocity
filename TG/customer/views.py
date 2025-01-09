import logging
from django.db.models import Sum, Count
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from vparnter.models import DriverNotification, LoadPricing, Partner, VehicleCategory
from .models import Feedback, Notification, Order, SliderImage, ViaLocation

def home(request):
    # Query the number of completed trips (orders with 'completed' status)
    completed_trips = Order.objects.filter(status='completed').count()

    # Query the overall distance traveled from completed trips
    total_distance = Order.objects.filter(status='completed').aggregate(Sum('distance'))['distance__sum']

    # Ensure that total_distance is a number, default to 0 if None or invalid
    if total_distance is None:
        total_distance = 0

    # Get the total number of customers and partners
    total_customers = Customer.objects.count()
    total_partners = Partner.objects.count()

    slider_images = SliderImage.objects.all()

    # Merge the statistics into context
    context = {
        'completed_trips': completed_trips,
        'total_distance': total_distance,
        'total_customers': total_customers,
        'total_partners': total_partners,
        'slider_images': slider_images,
    }

    return render(request, 'home.html', context)

def privacy_policy(request):
    return render(request, 'privacy_poli.html')

def terms_of_service(request):
    return render(request, 'terms_of_service.html')



from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from .models import Customer
import json
from decimal import Decimal

def signup(request):
    if request.method == 'POST': 
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        phone_number = request.POST.get('phonenumber')
        email = request.POST.get('email')
        state = request.POST.get('state')  # Get the state from the form
        district = request.POST.get('district')  # Get the district from the form
        city = request.POST.get('city')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        profile_pic = request.FILES.get('photo')  # Get the uploaded profile picture

        # Check if passwords match
        if password != confirm_password:
            return JsonResponse({'error': 'Passwords do not match.'}, status=400)

        # Check if phone number or email already exists
        if Customer.objects.filter(phone_number=phone_number).exists():
            return JsonResponse({'error': 'Phone number already registered.'}, status=400)

        if Customer.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already registered.'}, status=400)

        # Save the Customer instance
        try:
            customer = Customer(
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                email=email,
                state=state,  # Save state
                district=district,  # Save district
                city=city,
                profile_pic=profile_pic,  # Save the profile picture
                password=make_password(password)  # Hashing the password
            )
            customer.save()
            return JsonResponse({'success': 'Registration successful! You can now log in.'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'GET':
        return render(request, 'signup.html')

    return JsonResponse({'error': 'Invalid request method.'}, status=405)



def distance_calculator(request):
    return render(request, 'distance.html')

from django.contrib.auth.hashers import check_password
def login(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone')
        password = request.POST.get('password')

        # Check if customer with the given phone number exists
        try:
            customer = Customer.objects.get(phone_number=phone_number)
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Phone number not registered.'}, status=400)

        # Check if the password matches
        if not check_password(password, customer.password):
            return JsonResponse({'error': 'Invalid password.'}, status=400)

        # If authentication is successful, log in the customer
        request.session['customer_id'] = customer.id  # Storing customer ID in session
        request.session['first_name'] = customer.first_name  # Storing first name in session
        request.session['phone_number'] = customer.phone_number  # Storing phone number in session

        return JsonResponse({'success': 'Login successful! Redirecting to home page...'}, status=200)

    return render(request, 'login.html')  # Render the login page for GET requests

def list(request):
    search_results = [
        {
            'photo_url': 'https://via.placeholder.com/300x200',  # Placeholder image URL
            'vehicle_name': 'Toyota Camry',
            'vehicle_no': 'XYZ 1234',
            'price': 55.00,
            'away': 12.5,
            'rating': 4.8
        },
        {
            'photo_url': 'https://via.placeholder.com/300x200',  # Placeholder image URL
            'vehicle_name': 'Honda Accord',
            'vehicle_no': 'ABC 5678',
            'price': 60.00,
            'away': 8.2,
            'rating': 4.6
        },
        {
            'photo_url': 'https://via.placeholder.com/300x200',  # Placeholder image URL
            'vehicle_name': 'Ford Mustang',
            'vehicle_no': 'DEF 9012',
            'price': 80.00,
            'away': 15.0,
            'rating': 4.9
        },
    ]
    return render(request, 'list.html', {'search_results': search_results})

def vehicle_details_view(request):
    # Sample vehicle data
    vehicle = {
        'name': 'Toyota Camry',
        'photo_url': 'https://via.placeholder.com/800x400',  # Placeholder image URL
        'description': 'A comfortable mid-sized car with great fuel efficiency.',
        'price': 55.00,
        'rating': 4.8
    }

    # Sample feedback data
    feedbacks = [
        {
            'description': 'Great car, very comfortable!',
            'rating': 5
        },
        {
            'description': 'Fuel efficiency is fantastic.',
            'rating': 4.5
        },
        {
            'description': 'Smooth ride and spacious interior.',
            'rating': 4.7
        }
    ]

    return render(request, 'details.html', {'vehicle': vehicle, 'feedbacks': feedbacks})


def profile_view(request):
    user = request.user
    return render(request, 'profile.html', {'user': user})


def order_history_view(request):
    # Get the customer ID from the session
    customer_id = request.session.get('customer_id')
 
    if not customer_id:
        return redirect('login')
    # Fetch the customer object
    customer = get_object_or_404(Customer, id=customer_id)

    # Fetch the orders for the customer
    orders = Order.objects.filter(customer=customer).order_by('-date')  # Fetch orders and sort by date (newest first)
    
    # Prepare the data for each order
    rides = []
    for order in orders:
        rides.append({
            'order_id': order.order_id,
            'from_location': order.from_location,
            'to_location': order.to_location,
            'status': order.status,
            'date': order.date.strftime('%a, %d %b'),  # Format the date
            'time': order.date.strftime('%I:%M %p'),  # Format the time
            'from_address': order.from_location[:30] + '...' if len(order.from_location) > 30 else order.from_location,
            'to_address': order.to_location[:30] + '...' if len(order.to_location) > 30 else order.to_location,
        })

    return render(request, 'order_history.html', {'rides': rides})

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def feedback_view(request, order_id):
    if request.method == 'POST':
        # Handle feedback submission
        rating = request.POST['rating']
        description = request.POST['description']
        # Save feedback to the database (implement this logic)
        return redirect('order_history')  # Redirect to order history after submission
    return render(request, 'feedback.html', {'order_id': order_id})

def notifications_view(request):
    # Retrieve customer_id from the session
    customer_id = request.session.get('customer_id')
    
    if not customer_id:
        return redirect('login')
    # Ensure the customer exists or return a 404 error
    customer = get_object_or_404(Customer, id=customer_id)

    # Fetch notifications associated with the customer
    notifications = Notification.objects.filter(customer=customer)

    return render(request, 'notifications.html', {'notifications': notifications})

from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('home')

from django.shortcuts import render, get_object_or_404
from django.core.files.storage import FileSystemStorage

def customer_profile(request):
    customer_id = request.session.get('customer_id')  # Get customer_id from session

    if not customer_id:
        return redirect('login')  # Redirect to login if not authenticated

    # Retrieve the customer's data or redirect to login if it doesn't exist
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return redirect('login')  # Redirect if the customer does not exist

    # Handle POST request: this occurs when the customer submits the form to update their profile
    if request.method == 'POST':
        # Retrieve form data from POST request
        customer.first_name = request.POST.get('first_name')
        customer.last_name = request.POST.get('last_name')
        customer.state = request.POST.get('state')
        customer.district = request.POST.get('district')
        customer.city = request.POST.get('city')
        customer.work_place = request.POST.get('work_place')
        customer.home_place = request.POST.get('home_place')

        # Handle profile picture update if a new picture is uploaded
        if 'profile_pic' in request.FILES:
            profile_pic = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(profile_pic.name, profile_pic)
            customer.profile_pic = filename  # Save the new profile picture path

        # Save the updated customer object to the database
        customer.save()

        # Redirect back to the profile page to show the updated data
        return redirect('customer_profile')

    # Handle GET request: just display the profile page with the customer's current data
    return render(request, 'profile.html', {'customer': customer})

def auto_booking(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')
    return render(request,'p_auto_bo.html')

def logi_booking(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')
    return render(request,'logi_booking.html')

def vision(request):
    return render(request,'vision.html')

def about(request):
    return render(request,'about.html')


@csrf_exempt  # Disable CSRF for testing; consider adding CSRF protection for production
def calculate_price(request):
    if request.method == 'POST':
        # Get data from the request
        item_weight = request.POST.get('item-weight')
        labor_needed = request.POST.get('labor')  # 'yes' or 'no'
        labor_count = request.POST.get('laborCount') if labor_needed == 'yes' else 0
        distance = request.POST.get('distance')  # Distance in kilometers

        # Validate inputs
        if item_weight is None or not item_weight.isdigit():
            return JsonResponse({'success': False, 'message': 'Valid item weight is required.'})

        if distance is None or not distance.replace('.', '', 1).isdigit():  # Handle float inputs
            return JsonResponse({'success': False, 'message': 'Valid distance is required.'})

        # Convert item weight and distance to appropriate types
        item_weight = float(item_weight)
        distance = float(distance)

        # Define weight category thresholds
        weight_categories = {
            1: 100,
            2: 250,
            3: 650,
            4: 1000,
            5: 1500,
            6: 2000,
        }

        # Determine eligible categories based on item weight
        eligible_category_ids = [category_id for category_id, weight_limit in weight_categories.items() if item_weight <= weight_limit]

        # Fetch all vehicle categories that can bear the user's load, excluding the passenger category
        eligible_categories = VehicleCategory.objects.exclude(weight_category=7).filter(
            weight_category__in=eligible_category_ids
        )

        total_prices = []
        for category in eligible_categories:
            base_km_charge = float(category.base_price_per_km)  # Ensure it's a float
            load_pricing = LoadPricing.objects.filter(vehicle_category=category).first()

            if load_pricing:
                load_charge = float(load_pricing.price_per_km)  # Ensure it's a float
            else:
                load_charge = 0  # Handle case where no load pricing is found

            # Calculate the total price for this category
            total_price = (base_km_charge + load_charge) * distance  # Multiply by distance
            total_price += 0.40 * total_price + 0.35 * total_price + 20  # Adding additional charges

            total_prices.append({
                'category': category.get_weight_category_display(),
                'total_price': round(total_price, 2),  # Round to 2 decimal places
                'image': category.image.url if category.image else None  # Get image URL
            })

        # Return the total prices and eligible categories
        return JsonResponse({'success': True, 'eligible_categories': total_prices})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


def show_categories(request):
    categories_data = request.GET.get('data')
    categories = json.loads(categories_data)

    return render(request, 'show_categories.html', {'categories': categories})

@csrf_exempt  # Disable CSRF for testing; consider adding CSRF protection for production
def calprice(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            distance = float(data.get('distance', 0))
            category_id = data.get('category')

            print(f"Received data: distance={distance}, category_id={category_id}")

            if not distance or not category_id:
                return JsonResponse({'error': 'Invalid data provided'}, status=400)

            # Fetch the VehicleCategory based on the provided category ID
            category = VehicleCategory.objects.get(weight_category=category_id)

            # Convert the distance to a Decimal for consistency
            distance_decimal = Decimal(str(distance))

            base_price = category.base_price_per_km * distance_decimal

            # Add 6 rupees processing fee only if the distance is greater than 3 km
            if distance > 3:
                price = base_price + Decimal('6.00') 
            else:
                price = base_price

            return JsonResponse({
                'price': f'{price:.2f}',
                'category': category.get_weight_category_display(),
                'image': category.image.url if category.image else None
            })
        
        except VehicleCategory.DoesNotExist:
            print("Category not found")
            return JsonResponse({'error': 'Category not found'}, status=404)
        except Exception as e:
            print(f"Error occurred: {e}")
            return JsonResponse({'error': 'An error occurred while calculating the price'}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


from django.http import JsonResponse
from vparnter.models import Vehicle, VehicleCategory
import requests

def get_distance(from_location, vehicle_location):
    """Calculate distance using Google Maps API."""
    import requests
    api_key = 'AIzaSyD2aKVzC3za4z7PzGuiHh0evvFdx4agki0'  # Replace with your API key

    # Use Google Maps Distance Matrix API
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={from_location}&destinations={vehicle_location}&key={api_key}"
    
    response = requests.get(url)
    distance_data = response.json()

    if distance_data['status'] == 'OK' and distance_data['rows'][0]['elements'][0]['status'] == 'OK':
        distance = distance_data['rows'][0]['elements'][0]['distance']['value']  # Distance in meters
        return distance
    return float('inf')  # Return a large distance if there's an error

from django.core.files.storage import default_storage
from django.shortcuts import render, get_object_or_404
from .models import Order, Customer, Vehicle, ViaLocation
from django.db import transaction
# Refactored function to save the order and driver notification
def confirm_booking(request):
    if request.method == 'POST':
        # Extract data from the request
        from_location = request.POST.get('from-location')
        to_location = request.POST.get('to-location')
        via_locations = request.POST.get('via-location').split(',')  # Assuming this is a comma-separated string
        item_type = request.POST.get('item-type')
        item_weight = request.POST.get('item-weight')
        labor = request.POST.get('labor')
        labor_count = request.POST.get('laborCount')
        distance = request.POST.get('distance')
        duration = request.POST.get('duration')
        price = float(request.POST.get('selected-category-price'))  # Convert to float
        selected_category_name = request.POST.get('selected-category-name')
        item_image = request.FILES.get('itemImage')
        
        # Prepare labor info as JSON
        labor_info = {
            'is_required': labor.lower() == 'yes',  # Convert 'yes'/'no' to boolean
            'count': int(labor_count) if labor_count.isdigit() else 0  # Convert to int, default to 0 if invalid
        }

        # Check for customer in session
        customer_id = request.session.get('customer_id')
        if not customer_id:
            return JsonResponse({'success': False, 'message': 'Customer not authenticated.'}, status=401)

        # Mapping category names to their integer values
        WEIGHT_CATEGORY_MAP = {
            '0 to 100 kg': 1,
            '0 to 250 kg': 2,
            '0 to 650 kg': 3,
            '0 to 1000 kg': 4,
            '0 to 1500 kg': 5,
            '0 to 2000 kg': 6,
            'Passenger': 7
        }

        # Get the integer value for the selected category name
        selected_category_value = WEIGHT_CATEGORY_MAP.get(selected_category_name)
        if not selected_category_value:
            return JsonResponse({'success': False, 'message': 'Invalid vehicle category selected.'}, status=400)

        # Retrieve customer details
        customer = get_object_or_404(Customer, id=customer_id)

        try:
            def find_nearest_vehicle():
                vehicles = Vehicle.objects.select_for_update().filter(
                    vehicle_category__weight_category=selected_category_value,
                    status='active',
                    vehicle_status='standing'
                )

                nearest_vehicle = None
                min_distance = float('inf')

                for vehicle in vehicles:
                    vehicle_location = vehicle.location
                    distance_to_vehicle = get_distance(from_location, vehicle_location)

                    if distance_to_vehicle < min_distance:
                        min_distance = distance_to_vehicle
                        nearest_vehicle = vehicle

                return nearest_vehicle

            with transaction.atomic():
                assigned_vehicle = find_nearest_vehicle()

                if assigned_vehicle:
                    # Assign the vehicle
                    driver_info = assigned_vehicle.driver  # PartnerInfo instance
                    driver_name = f"{driver_info.partner.firstname} {driver_info.partner.lastname}"
                    driver_id = driver_info.driver_id
                    vehicle_id = assigned_vehicle.vehicle_id
                    vehicle_image_url = assigned_vehicle.vehicle_category.image.url
                    vehicle_location = assigned_vehicle.location
                    otp = customer.otp

                    # Adjust the price and processing fee
                    processing_fee = 20
                    adjusted_price = price - processing_fee

                    # Save the order
                    order = Order.objects.create(
                        customer=customer,
                        customer_phone_number=customer.phone_number,
                        driver=driver_info,
                        vehicle=assigned_vehicle,
                        from_location=from_location,
                        to_location=to_location,
                        purpose='logistics',
                        item_name=item_type,
                        load_kg=item_weight,
                        distance=distance,
                        price=adjusted_price,
                        processing_fee=processing_fee,
                        services='transport',
                        status='booking',
                        otp=otp,
                        load_image=item_image,
                        labor_info=labor_info  # Assign labor info as JSON
                    )

                    # Save via locations
                    for location in via_locations:
                        ViaLocation.objects.create(order=order, location=location)

                    # Update the vehicle status to 'running'
                    assigned_vehicle.vehicle_status = 'running'
                    assigned_vehicle.save()  # Save the updated vehicle status

                    # Notify the driver
                    message = f'You have been assigned a new order. Order ID: {order.id}, From: {from_location}, To: {to_location}.'
                    DriverNotification.objects.create(
                        driver=driver_info,
                        order=order,
                        message=message
                    )
                     # Create a notification for the customer
                    notification_title = 'Order Confirmed'
                    notification_message = f'Your order with has been successfully created and is being processed.'
                    Notification.objects.create(
                        customer=customer,
                        title=notification_title,
                        message=notification_message,
                        notification_type='order_update'
                    )

                    return JsonResponse({
                        'success': True,
                        'order_id': order.id,
                        'driver_id': driver_id,
                        'vehicle_image_url': vehicle_image_url,
                        'vehicle_id': vehicle_id,
                        'otp': otp,
                        'driver_name': driver_name,
                        'vehicle_location': vehicle_location,
                        'distance': distance,
                        'price': price
                    })
                else:
                    return JsonResponse({'success': False, 'message': 'No available vehicles found.'}, status=404)

        except Exception as e:
            return JsonResponse({'success': False, 'message': 'An error occurred while processing your request.'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

def reassign_vehicle(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')

        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(id=order_id)

                # Find a new vehicle to reassign
                def find_nearest_vehicle():
                    vehicles = Vehicle.objects.filter(
                        vehicle_category__weight_category=order.vehicle.vehicle_category.weight_category,
                        status='active',
                        vehicle_status='standing'
                    ).exclude(id=order.vehicle.id)  # Exclude the current vehicle

                    nearest_vehicle = None
                    min_distance = float('inf')

                    for vehicle in vehicles:
                        vehicle_location = vehicle.location
                        distance_to_vehicle = get_distance(order.from_location, vehicle_location)

                        if distance_to_vehicle < min_distance:
                            min_distance = distance_to_vehicle
                            nearest_vehicle = vehicle

                    return nearest_vehicle

                reassigned_vehicle = find_nearest_vehicle()

                if reassigned_vehicle:
                    # Reassign the new vehicle to the order
                    order.vehicle = reassigned_vehicle
                    order.driver = reassigned_vehicle.driver
                    order.save()

                    # Notify the new driver
                    message = f'You have been reassigned to a new order. Order ID: {order.id}, From: {order.from_location}, To: {order.to_location}.'
                    DriverNotification.objects.create(
                        driver=reassigned_vehicle.driver,
                        order=order,
                        message=message
                    )

                    return JsonResponse({'success': True, 'message': 'Vehicle reassigned successfully.'})
                else:
                    return JsonResponse({'success': False, 'message': 'No available vehicles for reassignment.'}, status=404)

        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found.'}, status=404)

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error during reassignment: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

def check_driver_status(request, order_id):
    try:
        # Log the order_id being checked
        logger.info(f"Checking driver notification for order ID: {order_id}")
        
        # Retrieve the order using the 'id' from customer_order
        order = Order.objects.get(id=order_id)

        # Log the order details
        logger.info(f"Order found: {order}")

        # Retrieve the latest driver notification for the given order
        driver_notification = DriverNotification.objects.filter(order=order).last()

        if driver_notification:
            # Log the driver notification status
            logger.info(f"Driver notification found with status: {driver_notification.status}")

            if driver_notification.status == 'accepted':
                # If accepted, send a success response
                return JsonResponse({'success': True, 'status': 'accepted'})

            elif driver_notification.status == 'rejected':
                # If rejected, send the status as rejected
                return JsonResponse({'success': True, 'status': 'rejected'})

            else:
                # If still pending, send the status as pending
                return JsonResponse({'success': True, 'status': 'pending'})
        else:
            # If there are no notifications for the order
            logger.warning(f"No driver notifications found for order ID: {order_id}")
            return JsonResponse({'success': True, 'status': 'no_notification'})

    except Order.DoesNotExist:
        # Log when order does not exist
        logger.error(f"Order with ID {order_id} does not exist.")
        return JsonResponse({'success': False, 'message': 'Order not found'}, status=404)

    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Error occurred while checking driver status for order ID: {order_id}: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

def render_success_page(request, order_id):
    try:
        # Retrieve the order using the 'id' from customer_order
        order = Order.objects.get(id=order_id)

        # Prepare context for the success page
        context = {
            'vehicle_image_url': order.vehicle.vehicle_category.image.url,
            'vehicle_id': order.vehicle.vehicle_id,
            'order_id':order.order_id,
            'driver_id':order.driver.driver_id,
            'otp': order.otp,
            'driver_name': f"{order.driver.partner.firstname} {order.driver.partner.lastname}",
            'vehicle_location': order.vehicle.location,
            'distance': order.distance,
            'price': order.price+order.processing_fee,
        }

        # Return the success page with the provided context
        return render(request, 'success.html', context)

    except Order.DoesNotExist:
        logger.error(f"Order with ID {order_id} does not exist.")
        return HttpResponseNotFound("Order not found")
    
    except Exception as e:
        logger.error(f"Error rendering success page for order ID: {order_id}: {str(e)}")
        return HttpResponseServerError("An error occurred")

import logging
import re
logger = logging.getLogger(__name__)

def receive_booking_confirmation(request):
    logger.info("Function receive_booking_confirmation called")
    if request.method == 'POST':
        try:
            logger.info("Receiving booking confirmation request.")
            
            # Extracting booking data from request.POST
            from_location = request.POST.get('from-location')
            to_location = request.POST.get('to-location')
            distance_str = request.POST.get('distance')
            price_str = request.POST.get('selected-category-price')
            duration = request.POST.get('duration')

            # Extract via locations from POST data
            via_locations = []
            for key, value in request.POST.items():
                if key.startswith('via-location'):
                    via_locations.append(value)

            # Log extracted data
            logger.debug(f"Extracted - From location: {from_location}, To location: {to_location}, Distance: {distance_str}, Price: {price_str}, Duration: {duration}, Via locations: {via_locations}")

            # Validate that required fields are present and not empty
            if not all([from_location, to_location, distance_str, price_str]):
                logger.error("Missing required fields.")
                return JsonResponse({'success': False, 'message': 'Missing required fields.'}, status=400)

            # Remove ' km' from distance and convert to float
            try:
                distance = float(distance_str.replace(' km', '').strip())

                # Clean the price string by removing any prefixes or currency symbols
                price_cleaned = price_str.replace('Price:', '').replace('₹', '').replace(',', '').strip()
                price = float(price_cleaned)
                
                logger.debug(f"Converted - Distance: {distance}, Price: {price}")
            except ValueError as ve:
                logger.error(f"Conversion error for distance/price: {ve}")
                return JsonResponse({'success': False, 'message': 'Invalid distance or price value.'}, status=400)

            # Check for customer in session
            customer_id = request.session.get('customer_id')
            if not customer_id:
                logger.error("Customer not authenticated.")
                return JsonResponse({'success': False, 'message': 'Customer not authenticated.'}, status=401)

            customer = get_object_or_404(Customer, id=customer_id)
            logger.info(f"Customer ID: {customer_id}, Customer Name: {customer.first_name} {customer.last_name}")

            # Mapping category names to their integer values
            WEIGHT_CATEGORY_MAP = {
                '0 to 100 kg': 1,
                '0 to 250 kg': 2,
                '0 to 650 kg': 3,
                '0 to 1000 kg': 4,
                '0 to 1500 kg': 5,
                '0 to 2000 kg': 6,
                'Passenger': 7
            }

            selected_category_value = WEIGHT_CATEGORY_MAP.get('Passenger')
            if not selected_category_value:
                logger.error("Invalid vehicle category selected.")
                return JsonResponse({'success': False, 'message': 'Invalid vehicle category selected.'}, status=400)

            vehicles = Vehicle.objects.filter(
                vehicle_category__weight_category=selected_category_value,
                status='active',
                vehicle_status='standing'
            )
            logger.info(f"Number of active standing vehicles found: {vehicles.count()}")

            assigned_vehicle = None
            min_distance = float('inf')

            for vehicle in vehicles:
                distance_to_vehicle = get_distance(from_location, vehicle.location)
                logger.debug(f"Vehicle {vehicle.vehicle_id} is {distance_to_vehicle} km away from {from_location}")

                if distance_to_vehicle < min_distance:
                    min_distance = distance_to_vehicle
                    assigned_vehicle = vehicle

           

            if assigned_vehicle:
                driver_info = assigned_vehicle.driver
                vehicle_image_url = assigned_vehicle.vehicle_category.image.url
                logger.debug(f"Assigned Vehicle ID: {assigned_vehicle.vehicle_id}, Driver: {driver_info.partner.firstname} {driver_info.partner.lastname}")

                processing_fee = 6 if distance > 3 else 0
                adjusted_price = price - processing_fee
                logger.debug(f"Adjusted price: {adjusted_price}, Processing fee: {processing_fee}")

                order = Order.objects.create(
                    customer=customer,
                    customer_phone_number=customer.phone_number,
                    driver=driver_info,
                    vehicle=assigned_vehicle,
                    from_location=from_location,
                    to_location=to_location,
                    purpose='Passenger',
                    distance=distance,
                    price=adjusted_price,
                    processing_fee=processing_fee,
                    services='Passenger',
                    status='booking',
                    otp=customer.otp
                )
                logger.info(f"Order created successfully with ID: {order.id}")

                for location in via_locations:
                    ViaLocation.objects.create(order=order, location=location)
                    logger.debug(f"Via location added: {location}")

                message = f'You have been assigned a new order. Order ID: {order.id}, From: {from_location}, To: {to_location}.'
                DriverNotification.objects.create(
                    driver=driver_info,
                    order=order,
                    message=message
                )


                context = {
                    'vehicle_image_url': vehicle_image_url,
                    'vehicle_id': assigned_vehicle.vehicle_id,
                    'otp': customer.otp,
                    'driver_name': f"{driver_info.partner.firstname} {driver_info.partner.lastname}",
                    'driver_id': driver_info.driver_id,
                    'vehicle_location': assigned_vehicle.location,
                    'distance': distance,
                    'price': price,
                }
                logger.info("Rendering success page")
                return render(request, 'success.html', context)

            else:
                logger.error("No available vehicles found.")
                return JsonResponse({'success': False, 'message': 'No available vehicles found.'}, status=404)

        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=True)
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    logger.error("Invalid request method.")
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@csrf_exempt  # This is required since you're making a POST request with fetch
def cancel_order(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request
            data = json.loads(request.body)
            order_id = data.get('order_id')
            
            # Find the order and check its status
            order = Order.objects.get(order_id=order_id)
            if order.status not in ['booking', 'confirmed']:
                # If status is not 'booking' or 'confirmed', do not allow cancellation
                return JsonResponse({
                    'success': False, 
                    'message': 'Order cannot be canceled as it is not in a cancellable state.'
                })
            
            # Update the order status to 'cancelled'
            order.status = 'cancelled'
            order.save()

            # Return a success response
            return JsonResponse({'success': True, 'message': 'Order cancelled successfully.'})
        
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    # Handle non-POST requests
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})
    

def order_detail(request):
    order_id = request.GET.get('order_id')
    order = get_object_or_404(Order, order_id=order_id)  # Fetch order by order_id

    # Get feedback for the order
    feedback = Feedback.objects.filter(order=order).first()  # Assuming there's a Feedback model linked to Order

    # Get associated waiting times and calculate total waiting time price
    waiting_times = order.waiting_times.all()
    total_waiting_time_price = sum(waiting_time.waiting_time_price for waiting_time in waiting_times)
    

    # Return the partial HTML for order details
    return render(request, 'his_odr_detail.html', {
        'order': order,
        'rating_range': range(1, 6),  # Star rating range
        'feedback': feedback,  # Pass feedback to template
        'waiting_times': waiting_times,  # Pass waiting times to template
        'total_waiting_time_price': total_waiting_time_price  # Total price of waiting times
    })

from django.views.decorators.http import require_POST


@csrf_exempt
def submit_feedback(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        driver_id = request.POST.get('driver_id')
        order_id = request.POST.get('order_id')
        rating = request.POST.get('rating')
        description = request.POST.get('description', '')  # Default to empty string if not provided

        customer_id = request.session.get('customer_id')
        customer = Customer.objects.filter(id=customer_id).first() if customer_id else None

        # Debugging statements
        print(f"Customer ID: {customer_id}, Driver ID: {driver_id}, Order ID: {order_id}, Rating: {rating}, Description: {description}")

        # Validation checks
        if not customer:
            return JsonResponse({'status': 'error', 'message': 'Customer not found in session.'})
        if not driver_id or not order_id or not rating:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields.'})

        # Validate order ID
        order = Order.objects.filter(order_id=order_id).first()
        if not order:
            return JsonResponse({'status': 'error', 'message': 'Invalid order ID.'})

        # Create and save Feedback instance
        feedback = Feedback(
            customer=customer,
            driver_id=driver_id,
            order=order,
            rating=rating,
            description=description
        )

        try:
            feedback.save()
            return JsonResponse({'status': 'success', 'message': 'Feedback submitted successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def ambu_booking(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')
    return render(request,'ambu_booking.html')


logger = logging.getLogger(__name__)

@csrf_exempt  # Use CSRF exemption only for testing; ensure proper CSRF handling in production
def submit_booking(request):
    logger.info("Function submit_booking called")
    if request.method == 'POST':
        try:
            logger.info("Receiving booking request for ambulance.")

            # Extracting booking data from request body
            data = json.loads(request.body)
            from_location = data.get('location')  # Assuming location is passed as 'location'

            logger.debug(f"Extracted From location: {from_location}")

            # Validate that required fields are present and not empty
            if not from_location:
                logger.error("Missing required field: location.")
                return JsonResponse({'success': False, 'message': 'Missing required field: location.'}, status=400)

            # Check for customer in session
            customer_id = request.session.get('customer_id')
            if not customer_id:
                logger.error("Customer not authenticated.")
                return JsonResponse({'success': False, 'message': 'Customer not authenticated.'}, status=401)

            customer = get_object_or_404(Customer, id=customer_id)
            logger.info(f"Customer ID: {customer_id}, Customer Name: {customer.first_name} {customer.last_name}")

            # Mapping category names to their integer values
            WEIGHT_CATEGORY_MAP = {
                'Ambulance': 8  # 8th category for Ambulance
            }

            selected_category_value = WEIGHT_CATEGORY_MAP.get('Ambulance')
            if not selected_category_value:
                logger.error("Invalid vehicle category selected.")
                return JsonResponse({'success': False, 'message': 'Invalid vehicle category selected.'}, status=400)

            vehicles = Vehicle.objects.filter(
                vehicle_category__weight_category=selected_category_value,
                status='active',
                vehicle_status='standing'
            )
            logger.info(f"Number of active standing vehicles found: {vehicles.count()}")

            assigned_vehicle = None
            min_distance = float('inf')

            for vehicle in vehicles:
                distance_to_vehicle = get_distance(from_location, vehicle.location)
                logger.debug(f"Vehicle {vehicle.vehicle_id} is {distance_to_vehicle} km away from {from_location}")

                if distance_to_vehicle < min_distance:
                    min_distance = distance_to_vehicle
                    assigned_vehicle = vehicle

            if assigned_vehicle:
                driver_info = assigned_vehicle.driver
                vehicle_image_url = assigned_vehicle.vehicle_category.image.url
                logger.debug(f"Assigned Vehicle ID: {assigned_vehicle.vehicle_id}, Driver: {driver_info.partner.firstname} {driver_info.partner.lastname}")

                # Set price, processing fee, distance to 0 as per your requirement
                processing_fee = 0
                adjusted_price = 0
                distance = 0
                
                order = Order.objects.create(
                    customer=customer,
                    customer_phone_number=customer.phone_number,
                    driver=driver_info,
                    vehicle=assigned_vehicle,
                    from_location=from_location,
                    to_location='Hospital',  # Set to Hospital as per your requirement
                    purpose='Ambulance',  # Set purpose as Ambulance
                    distance=distance,
                    price=adjusted_price,
                    processing_fee=processing_fee,
                    services='Ambulance',
                    status='booking',
                    otp=customer.otp
                )
                logger.info(f"Order created successfully with ID: {order.id}")

                message = f'You have been assigned a new ambulance order. Order ID: {order.id}, From: {from_location}, To: Hospital.'
                DriverNotification.objects.create(
                    driver=driver_info,
                    order=order,
                    message=message
                )

                context = {
                    'vehicle_image_url': vehicle_image_url,
                    'vehicle_id': assigned_vehicle.vehicle_id,
                    'otp': customer.otp,
                    'driver_name': f"{driver_info.partner.firstname} {driver_info.partner.lastname}",
                    'driver_id': driver_info.driver_id,
                    'vehicle_location': assigned_vehicle.location,
                    'distance': distance,
                    'price': adjusted_price,
                }
                logger.info("Rendering success page")
                return render(request, 'success.html', context)

            else:
                logger.error("No available vehicles found.")
                return JsonResponse({'success': False, 'message': 'No available vehicles found.'}, status=404)

        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=True)
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    logger.error("Invalid request method.")
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)