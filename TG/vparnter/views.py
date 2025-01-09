from django.urls import reverse
from django.utils import timezone
from pyexpat.errors import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from customer.models import Feedback, Notification, Order
from vparnter.models import DriverNotification, Partner, PartnerInfo, Pocket, Transaction, Vehicle, WaitingTime
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth.decorators import login_required
from django.db.models import Sum,Avg

def vhome(request):
    partner_name = request.session.get('partner_name')
    partner_phone = request.session.get('partner_phone')
    if not partner_phone:
        return redirect('vlogin')
    print("Partner Name:", partner_name)
    print("Partner Phone:", partner_phone)

    daily_earnings = 0
    overall_earnings = 0
    daily_order_count = 0
    overall_order_count = 0
    average_rating = 0  # Initialize average rating

    if partner_name and partner_phone:
        # Split the partner_name by spaces and handle multiple parts
        name_parts = partner_name.split()
        firstname = name_parts[0]  # First part is the firstname
        lastname = ' '.join(name_parts[1:])  # Join the rest as lastname
        
        partner = Partner.objects.filter(
            firstname=firstname,
            lastname=lastname,
            phone_no=partner_phone
        ).first()

        if partner:
            partner_info = PartnerInfo.objects.filter(partner=partner).first()
            if partner_info:
                vehicle = Vehicle.objects.filter(driver=partner_info).first()
                if vehicle:
                    print("Vehicle found:", vehicle)
                else:
                    print("No vehicle found for the partner.")
                
                # Calculate earnings and order counts
                overall_earnings = Order.objects.filter(vehicle__driver=partner_info).aggregate(Sum('price'))['price__sum'] or 0
                overall_order_count = Order.objects.filter(vehicle__driver=partner_info).count()

                # Assuming daily earnings are calculated for the current day
                from django.utils import timezone
                today = timezone.now().date()
                daily_earnings = Order.objects.filter(
                    vehicle__driver=partner_info,
                    date__date=today
                ).aggregate(Sum('price'))['price__sum'] or 0
                daily_order_count = Order.objects.filter(
                    vehicle__driver=partner_info,
                    date__date=today
                ).count()

                # Calculate the average rating from Feedback
                average_rating = Feedback.objects.filter(driver=partner_info).aggregate(Avg('rating'))['rating__avg'] or 0
                
            else:
                print("No partner info found for the partner.")
                vehicle = None
        else:
            print("No partner found with the given details.")
            vehicle = None
    else:
        print("No partner data found in session.")
        vehicle = None

    # Prepare context with earnings, order counts, and average rating
    context = {
        'vehicle': vehicle,
        'daily_earnings': daily_earnings,
        'overall_earnings': overall_earnings,
        'daily_order_count': daily_order_count,
        'overall_order_count': overall_order_count,
        'average_rating': average_rating,  # Include average rating in context
    }

    return render(request, 'vhome.html', context)

def vorder(request):
    partner_id = request.session.get('partner_id')
    
     # Get PartnerInfo based on the partner_id from the session
    partner_info = get_object_or_404(PartnerInfo, partner__id=partner_id)

    # Fetch all vehicles associated with the partner
    vehicles = Vehicle.objects.filter(driver=partner_info)

    # Fetch orders associated with the partner's vehicles
    orders = Order.objects.filter(vehicle__driver=partner_info)

    # Prepare context
    context = {
        'orders': orders,
        'vehicles': vehicles,  # Optional: include vehicles if needed in the template
    }
    return render(request,'vorder.html',context)

def vlogin(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone')
        password = request.POST.get('password')

        try:
            partner = Partner.objects.get(phone_no=phone_number)

            if partner.check_password(password):
                # Manually set session data without using `login`
                request.session['partner_id'] = partner.id
                request.session['partner_name'] = f'{partner.firstname} {partner.lastname}'
                request.session['partner_phone'] = partner.phone_no  # Set phone number in session
                print(request.session) 

                return JsonResponse({'success': 'Login successful!'}, status=200)

            else:
                return JsonResponse({'error': 'Invalid password.'}, status=400)

        except Partner.DoesNotExist:
            return JsonResponse({'error': 'Phone number not registered.'}, status=400)

    elif request.method == 'GET':
        return render(request, 'vlogin.html')

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def generate_driver_id():
    current_date = timezone.now()  # Use Django's timezone-aware now
    date_str = current_date.strftime('%d%m%y')
    
    # Retrieve the last driver ID from the PartnerInfo model
    last_partner_info = PartnerInfo.objects.order_by('driver_id').last()
    
    if last_partner_info:
        last_driver_id = last_partner_info.driver_id
        new_number = int(last_driver_id[-4:]) + 1
    else:
        new_number = 1
    
    # Generate the new driver ID
    driver_id = f"SC{date_str}{new_number:04d}"
    return driver_id

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def vregisration(request):
    if request.method == 'POST':
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        phone_number = request.POST.get('phonenumber')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')

        # Check if passwords match
        if password != confirm_password:
            return JsonResponse({'error': 'Passwords do not match.'}, status=400)

        # Check if phone number or email already exists
        if Partner.objects.filter(phone_no=phone_number).exists():
            return JsonResponse({'error': 'Phone number already registered.'}, status=400)

        if Partner.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already registered.'}, status=400)

        # Save the Partner instance
        try:
            partner = Partner(
                firstname=first_name,
                lastname=last_name,
                phone_no=phone_number,
                email=email,
                password=make_password(password)  # Hashing the password
            )
            partner.save()
            return JsonResponse({'success': 'Registration successful! You can now log in.'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'GET':
        return render(request, 'vregisration.html')

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def drive_reg(request):
    if request.method == 'POST':
    # Extract data from POST request
        phone_number = request.POST.get('phonenumber')
        alternative_phone_number = request.POST.get('alternative_phone_number')
        dob = request.POST.get('dob')
        aadhaar_number = request.POST.get('aadhaar_number')
        driving_license = request.POST.get('driving_license')
        current_address = request.POST.get('current_address')
        
        # Extract files from FILES request
        profile_photo = request.FILES.get('profile_photo')
        license_photo = request.FILES.get('license_photo')

        # Get the partner (assuming partner exists based on phone number)
        try:
            partner = Partner.objects.get(phone_no=phone_number)
        except Partner.DoesNotExist:
            # Handle the case where the partner doesn't exist
            return render(request, 'driver_reg.html', {
                'error': 'Partner with this phone number does not exist.'
            })
        
        # Create and save the PartnerInfo object
        partner_info = PartnerInfo.objects.create(
            partner=partner,  # Correct this to pass the partner object
            alternative_phone=alternative_phone_number,
            dob=dob,
            adhar_no=aadhaar_number,
            dl=driving_license,
            dl_document=license_photo,
            profile_picture=profile_photo,
            address=current_address,
            driver_id=generate_driver_id()
        )
        
        # Redirect to login page upon success
        return redirect('vlogin')

    return render(request, 'driver_reg.html')

def vlogout(request):
    request.session.flush()  # Clears the session
    return redirect('vlogin')

def save_vehicle_status(request):
    if request.method == 'POST':
        # Retrieve the current partner's information from the session
        partner_name = request.session.get('partner_name')
        partner_phone = request.session.get('partner_phone')

        if partner_name and partner_phone:
            # Split the partner_name by spaces and handle multiple parts
            name_parts = partner_name.split()
            firstname = name_parts[0]
            lastname = ' '.join(name_parts[1:])

            partner = Partner.objects.filter(
                firstname=firstname,
                lastname=lastname,
                phone_no=partner_phone
            ).first()

            if partner:
                partner_info = PartnerInfo.objects.filter(partner=partner).first()

                if partner_info:
                    vehicle = Vehicle.objects.filter(driver=partner_info).first()

                    if vehicle:
                        # Get the selected vehicle status from the form
                        vehicle_status = request.POST.get('vehicle-status')
                        additional_status = request.POST.get('additional-status')

                        # Update the vehicle's status (active/inactive)
                        if vehicle_status in ['active', 'inactive']:
                            vehicle.status = vehicle_status

                        # If the vehicle is active, update the additional status (standing/moving)
                        if vehicle_status == 'active' and additional_status in ['standing', 'running']:
                            vehicle.vehicle_status = additional_status
                        else:
                            vehicle.vehicle_status = None  # Clear additional status if vehicle is not active

                        # Save the changes to the database
                        vehicle.save()

        return redirect('vhome')  # Redirect back to the vehicle home page

    return redirect('vhome')
    
def v_vechile_reg(request):
    partner_phone = request.session.get('partner_phone')

    if partner_phone:
        # Fetch the Partner instance using the phone number
        partner = Partner.objects.filter(phone_no=partner_phone).first()

        if not partner:
            return redirect('v_vech_reg')  # Redirect if partner not found

        # Fetch the associated PartnerInfo
        partner_info = PartnerInfo.objects.filter(partner=partner).first()

        if not partner_info:
            return redirect('v_vech_reg')  # Redirect if PartnerInfo not found
    else:
        return redirect('v_vech_reg')  # Redirect if partner data is not found in session

    if request.method == 'POST':
        # Get form data from POST request
        vehicle_number = request.POST.get('vehicleNumber')
        vehicle_name = request.POST.get('vehicleName')
        owner_name = request.POST.get('ownerName')
        vehicle_type = request.POST.get('vehicleType')
        load_capacity = request.POST.get('loadCapacity')
        current_location = request.POST.get('currentLocation')
        entered_phone_number = request.POST.get('phoneNumber')  # Get entered phone number

        # New Fields
        state = request.POST.get('state')
        district = request.POST.get('district')
        taluk_town = request.POST.get('talukTown')

        # Vehicle Purpose
        vehicle_purpose = request.POST.get('vehiclePurpose')  # Get vehicle purpose (Passenger/Logistics)

        # Check if the entered phone number matches the session phone number
        if entered_phone_number != partner_phone:
            # Redirect without saving if the phone numbers don't match
            return render(request, 'v_vechile_reg.html')  # Render the form again without saving

        # Get file data from POST request
        vehicle_photo = request.FILES.get('vehiclePhoto')
        rc_card = request.FILES.get('rcCard')
        insurance = request.FILES.get('insurance')

        # Create and save the Vehicle instance
        Vehicle.objects.create(
            vehicle_id=vehicle_number,
            driver=partner_info,  # Using the partner_info for the correct Partner
            name=vehicle_name,
            owner_name=owner_name,
            vehicle_type=vehicle_type,
            load_capacity=load_capacity,
            location=current_location,
            state=state,  # Save the state field
            district=district,  # Save the district field
            taluk_town=taluk_town,  # Save the taluk/town field
            photo=vehicle_photo,
            rc_card_photo=rc_card,
            insurance=insurance,
            status='active',  # Set status as active by default
            vehicle_status='standing',  # Set initial vehicle status to standing
            vehicle_purpose=vehicle_purpose  # Save the vehicle purpose
        )

        return redirect('vhome')  # Redirect to home page after successful registration

    return render(request, 'v_vechile_reg.html')

import logging

def update_location(request):
    if request.method == 'POST':
        new_location = request.POST.get('location')
        partner_name = request.session.get('partner_name')
        partner_phone = request.session.get('partner_phone')

        # Check if partner_name or partner_phone is None
        if partner_name is None or partner_phone is None:
            return JsonResponse({'success': False, 'error': 'Partner name or phone is missing'}, status=400)

        try:
            # Split the partner_name safely now that we know it's not None
            name_parts = partner_name.split()
            partner = Partner.objects.get(
                firstname=name_parts[0],
                lastname=' '.join(name_parts[1:]),
                phone_no=partner_phone
            )
            
            partner_info = PartnerInfo.objects.get(partner=partner)
            vehicle = Vehicle.objects.get(driver=partner_info)

            # Update the location field in the Vehicle model
            vehicle.location = new_location
            vehicle.save()

            # Return success and the URL to redirect to
            return JsonResponse({'success': True, 'redirect_url': reverse('vhome')})

        except Partner.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Partner does not exist'}, status=404)
        except PartnerInfo.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'PartnerInfo does not exist'}, status=404)
        except Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Vehicle does not exist'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def vprofile(request):
    partner_name = request.session.get('partner_name')
    partner_phone = request.session.get('partner_phone')

    # Fetch the partner using the session data
    if partner_name and partner_phone:
        name_parts = partner_name.split()
        firstname = name_parts[0]
        lastname = ' '.join(name_parts[1:])

        partner = Partner.objects.filter(
            firstname=firstname,
            lastname=lastname,
            phone_no=partner_phone
        ).first()

        if partner:
            partner_info = PartnerInfo.objects.filter(partner=partner).first()
        else:
            partner_info = None
    else:
        partner = None
        partner_info = None

    # Pass the partner and partner_info data to the template
    return render(request, 'vprofile.html', {
        'partner': partner,
        'partner_info': partner_info
    })


def vehicle_profile_view(request):
    partner_name = request.session.get('partner_name')
    partner_phone = request.session.get('partner_phone')

    vehicle = None
    today_total_trips = today_total_distance = today_total_earnings = 0
    overall_trips = overall_distance = overall_earnings = 0

    if partner_name and partner_phone:
        name_parts = partner_name.split()
        firstname = name_parts[0]
        lastname = ' '.join(name_parts[1:])
        
        partner = Partner.objects.filter(
            firstname=firstname,
            lastname=lastname,
            phone_no=partner_phone
        ).first()

        if partner:
            partner_info = PartnerInfo.objects.filter(partner=partner).first()
            if partner_info:
                vehicle = Vehicle.objects.filter(driver=partner_info).first()

                if vehicle:
                    # Get today's statistics for the vehicle
                    today = timezone.now().date()
                    today_orders = Order.objects.filter(
                        vehicle=vehicle,
                        date__date=today
                    )
                    today_total_trips = today_orders.count()
                    today_total_distance = today_orders.aggregate(total_distance=Sum('distance'))['total_distance'] or 0
                    today_total_earnings = today_orders.aggregate(total_earnings=Sum('price'))['total_earnings'] or 0

                    # Get overall statistics for the vehicle
                    all_orders = Order.objects.filter(vehicle=vehicle)
                    overall_trips = all_orders.count()
                    overall_distance = all_orders.aggregate(total_distance=Sum('distance'))['total_distance'] or 0
                    overall_earnings = all_orders.aggregate(total_earnings=Sum('price'))['total_earnings'] or 0

    context = {
        'vehicle': vehicle,
        'today_total_trips': today_total_trips,
        'today_total_distance': today_total_distance,
        'today_total_earnings': today_total_earnings,
        'overall_trips': overall_trips,
        'overall_distance': overall_distance,
        'overall_earnings': overall_earnings,
    }

    return render(request, 'v_vehile_prof.html', context)


def myearning(request):
    partner_name = request.session.get('partner_name')
    partner_phone = request.session.get('partner_phone')

    # Initialize variables for balance, daily earnings, and overall earnings
    balance = 0
    daily_earnings = 0
    overall_earnings = 0
    daily_order_count = 0
    overall_order_count = 0
    orders = []  # Initialize an empty list for orders

    if partner_name and partner_phone:
        # Split the partner_name by spaces and handle multiple parts
        name_parts = partner_name.split()
        firstname = name_parts[0]
        lastname = ' '.join(name_parts[1:])

        # Retrieve the partner based on the session data
        partner = Partner.objects.filter(
            firstname=firstname,
            lastname=lastname,
            phone_no=partner_phone
        ).first()

        if partner:
            # Retrieve the associated PartnerInfo instance
            partner_info = PartnerInfo.objects.filter(partner=partner).first()
            if partner_info:
                try:
                    # Get the pocket and balance for the partner
                    pocket = Pocket.objects.get(partner=partner)
                    balance = pocket.balance  # Partner's balance

                    # Calculate overall earnings from completed orders
                    overall_earnings = Order.objects.filter(vehicle__driver=partner_info).aggregate(Sum('price'))['price__sum'] or 0
                    overall_order_count = Order.objects.filter(vehicle__driver=partner_info).count()

                    # Calculate today's earnings and order count
                    today = timezone.now().date()
                    daily_earnings = Order.objects.filter(
                        vehicle__driver=partner_info,
                        date__date=today
                    ).aggregate(Sum('price'))['price__sum'] or 0
                    daily_order_count = Order.objects.filter(
                        vehicle__driver=partner_info,
                        date__date=today
                    ).count()

                    # Fetch transactions related to the pocket
                    transactions = Transaction.objects.filter(pocket=pocket)

                    # Retrieve all orders for the partner's vehicle
                    orders = Order.objects.filter(vehicle__driver=partner_info).values('order_id', 'date', 'distance', 'price')

                    # Render the template with the fetched data
                    return render(request, 'myearning.html', {
                        'partner': partner,
                        'balance': balance,
                        'daily_earnings': daily_earnings,
                        'overall_earnings': overall_earnings,
                        'daily_order_count': daily_order_count,
                        'overall_order_count': overall_order_count,
                        'transactions': transactions,
                        'orders': orders  # Pass orders to the template
                    })
                except Pocket.DoesNotExist:
                    return render(request, 'myearning.html', {'error': 'Pocket not found'})
            else:
                return render(request, 'myearning.html', {'error': 'Partner information not found'})
        else:
            return render(request, 'myearning.html', {'error': 'Partner not found'})
    else:
        return render(request, 'myearning.html', {'error': 'Unauthorized access'})
    
def new_ord(request):
    return render(request,'new_order.html')

def vpassbook(request):
    # Assuming partner_name and partner_phone are stored in session upon login
    partner_phone = request.session.get('partner_phone')

    # Ensure the user is authenticated or authorized
    if partner_phone:
        try:
            # Fetch the partner by phone number
            partner = Partner.objects.get(phone_no=partner_phone)

            # Try to get the corresponding pocket for the partner
            pocket = Pocket.objects.get(partner=partner)
            balance = pocket.balance  # Get the balance from the Pocket model

            # Fetch all transactions related to this particular pocket
            transactions = Transaction.objects.filter(pocket=pocket).order_by('-created_at')

            # Calculate the balance dynamically based on transactions
            running_balance = balance
            passbook_data = []
            for transaction in transactions:
                if transaction.transaction_type == 'credit':
                    running_balance -= transaction.amount
                elif transaction.transaction_type == 'debit':
                    running_balance += transaction.amount
                
                passbook_data.append({
                    'date': transaction.created_at.strftime('%Y-%m-%d'),
                    'credit': transaction.amount if transaction.transaction_type == 'credit' else 0,
                    'debit': transaction.amount if transaction.transaction_type == 'debit' else 0,
                    'balance': running_balance,
                    'description': transaction.get_description_display(),
                })

            # Pass all data to the template
            return render(request, 'vpassbook.html', {
                'partner': partner,
                'balance': balance,
                'passbook_data': passbook_data,  # Pass the passbook data
            })
        except Partner.DoesNotExist:
            return render(request, 'vpassbook.html', {'error': 'Partner not found'})
        except Pocket.DoesNotExist:
            return render(request, 'vpassbook.html', {'error': 'Pocket not found'})
    else:
        return render(request, 'vpassbook.html', {'error': 'Unauthorized access'})
    

def vauto(request):
    return render(request,'vautobo.html')


def driver_notifications(request):
    partner_id = request.session.get('partner_id')
    
    # Get the PartnerInfo instance based on the partner_id
    partner_info = get_object_or_404(PartnerInfo, partner_id=partner_id)

    # Retrieve unread notifications for the partner's info
    notifications = DriverNotification.objects.filter(driver=partner_info, is_read=False)
    
    notifications_with_orders = []
    for notification in notifications:
        order = notification.order
        order_details = {
            'order_id': order.order_id,
            'customer_phone_number': order.customer_phone_number if order.customer_phone_number else 'N/A',
            'vehicle': order.vehicle if order.vehicle else 'N/A',
            'date': order.date,
            'from_location': order.from_location,
            'to_location': order.to_location,
            'purpose': order.purpose if order.purpose else 'N/A',
            'item_name': order.item_name if order.item_name else 'N/A',
            'load_kg': f"{order.load_kg} kg" if order.load_kg else 'N/A',
            'load_image_url': order.load_image.url if order.load_image else 'N/A',
            'services': order.services if order.services else 'N/A',
            'distance': f"{order.distance} km" if order.distance else 'N/A',
            'price': f"₹{order.price}" if order.price else 'N/A',
            'processing_fee': f"₹{order.processing_fee}" if order.processing_fee else 'N/A',
            'labor_info': order.labor_info if order.labor_info else 'N/A',
            'status': order.status,
            'otp': order.otp if order.otp else 'N/A',
            'message': notification.message,
            'created_at': notification.created_at,
        }
        notifications_with_orders.append(order_details)


    return render(request, 'new_order.html', {'notifications': notifications_with_orders})


@csrf_exempt  # Only use this if you have CSRF issues; otherwise, include csrf token in your AJAX
def update_notification_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')  # This is the unique ID as a string
        action = request.POST.get('action')

        try:
            # First, retrieve the Order instance based on the string ID
            order = Order.objects.get(order_id=order_id)  # Assuming `order_id` is the unique field

            # Now, get the DriverNotification associated with that order
            notification = DriverNotification.objects.get(order=order)

            if action == 'accept':
                notification.status = 'accepted'
                notification.is_read = True
                order.status = 'confirmed'  # Change the order status to confirmed
                order.save()  # Save the updated order status
            elif action == 'reject':
                notification.status = 'rejected'
                notification.is_read = True
            else:
                return JsonResponse({'success': False, 'message': 'Invalid action'})

            notification.save()  # Save the notification changes

            return JsonResponse({'success': True, 'message': f'Notification {action}ed successfully.'})
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found.'})
        except DriverNotification.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Notification not found.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def order_operation(request):
    order_id = request.GET.get('order_id')
    order = get_object_or_404(Order, order_id=order_id)  # Fetch the order by ID
    
    # Fetch associated waiting times
    waiting_times = order.waiting_times.all()
    
    total_waiting_time_price = sum(waiting_time.waiting_time_price for waiting_time in waiting_times)

    # Calculate total price
    total_price = order.price + order.processing_fee + total_waiting_time_price

    context = {
        'order_id': order.order_id,
        'customer_name': order.customer.first_name,
        'customer_number': order.customer_phone_number,
        'from_location': order.from_location,
        'to_location': order.to_location,
        'distance': order.distance,
        'price': order.price,
        'processing_fee': order.processing_fee,
        'item_name': order.item_name,
        'item_load': order.load_kg,
        'item_image_url': order.load_image.url if order.load_image else '',
        'status': order.status,
        'otp_verified': order.otp_verified,
        'verified': order.verified,
        'total_waiting_time_price': total_waiting_time_price,  # Add total waiting time price to context
        'total_price': total_price  # Include the total price in context
    }
    
    return render(request, 'order_opr.html', context)

@csrf_exempt  # Use this if CSRF tokens are not handled in your front-end (remove if CSRF tokens are handled)
@csrf_exempt  # Use this if CSRF tokens are not handled in your front-end (remove if CSRF tokens are handled)
def validate_otp(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        otp = request.POST.get('otp')

        try:
            # Fetch the order by order_id
            order = Order.objects.get(order_id=order_id)

            # Check if the OTP is correct
            if order.otp == otp:
                # Mark the order as OTP-verified and update the status to 'in_progress'
                order.otp_verified = True
                order.status = 'in_progress'  # Update status to 'in_progress'
                order.save()

                return JsonResponse({'success': True, 'message': 'OTP is valid and verified successfully! Order status is now "in progress".'})
            else:
                return JsonResponse({'success': False, 'message': 'Incorrect OTP!'})
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found.'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})

import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')

        logger.info(f"Received request to update order ID {order_id} to status {new_status}")

        try:
            # Retrieve the order using the unique order ID
            order = Order.objects.get(order_id=order_id)

            # Update the order status
            order.status = new_status
            order.save()

            logger.info(f"Successfully updated order ID {order_id} to status {new_status}")

            # Check if status is "completed" to provide a specific alert message and redirect
            if new_status == 'completed':
                # Prepare the redirect URL and alert message
                redirect_url = reverse('vhome')
                alert_message = "Order is completed. Please update the vehicle status and location."
                notification_title = 'Completed'
                notification_message = f'Order is Successfully Completed, Thank You for Using Spedocity.'
                Notification.objects.create(
                            customer=order.customer,
                            title=notification_title,
                            message=notification_message,
                            notification_type='order_update'
                        )

                return JsonResponse({
                    'success': True,
                    'message': 'Order status updated to completed.',
                    'redirect_url': redirect_url,
                    'alert_message': alert_message
                })

            # Return a general success response if status is not "completed"
            return JsonResponse({'success': True, 'message': 'Order status updated successfully.'})
        
        except Order.DoesNotExist:
            logger.error(f"Order ID {order_id} not found.")
            return JsonResponse({'success': False, 'message': 'Order not found.'})
        except Exception as e:
            logger.error(f"Error updating order status: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@csrf_exempt  # Use with caution; consider CSRF tokens for security
def save_verification_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        verified = request.POST.get('verified') == 'true'  # Convert to boolean

        try:
            order = Order.objects.get(order_id=order_id)  # Ensure order_id is a valid field in your Order model
            order.verified = verified  # Update the verified field
            order.save()
            notification_title = 'Verification'
            notification_message = f'Your Item Is verified by the Driver.'
            Notification.objects.create(
                            customer=order.customer,
                            title=notification_title,
                            message=notification_message,
                            notification_type='order_update'
                        )
            return JsonResponse({'success': True, 'message': 'Verification status saved.'})
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def check_order_status(request):
    order_id = request.GET.get('order_id')  # Get order_id from the request

    if not order_id:  # Check if order_id is provided
        return JsonResponse({
            'success': False,
            'message': 'No order ID provided.'
        })

    try:
        # Look up the order using order_id instead of the numeric id
        order = Order.objects.get(order_id=order_id)
        return JsonResponse({
            'success': True,
            'status': order.status  # Return the status or any other relevant data
        })
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Order not found.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        })
    


def start_waiting_time(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        order = get_object_or_404(Order, order_id=order_id)
        
        # Create a new WaitingTime entry with the current time as start_time
        waiting_time = WaitingTime.objects.create(order=order, start_time=timezone.now())

        notification_title = 'Waiting Charge'
        notification_message = f'Waiting Time has been started for your order, Waiting Time charger ₹1.5 per minute.'
        Notification.objects.create(
                        customer=order.customer,
                        title=notification_title,
                        message=notification_message,
                        notification_type='order_update'
                    )
        
        return JsonResponse({"success": True, "message": "Waiting time started.", "waiting_time_id": waiting_time.id})

def stop_waiting_time(request):
    if request.method == "POST":
        waiting_time_id = request.POST.get("waiting_time_id")
        waiting_time = get_object_or_404(WaitingTime, id=waiting_time_id)
        
        # Set the end_time and save the model to calculate duration
        waiting_time.end_time = timezone.now()
        waiting_time.save()

        
        return JsonResponse({"success": True, "message": "Waiting time stopped.", "duration": str(waiting_time.duration)})
    
import io
import xlsxwriter
def download_passbook(request):
    partner_phone = request.session.get('partner_phone')
    if not partner_phone:
        return HttpResponse("Unauthorized", status=401)

    try:
        partner = Partner.objects.get(phone_no=partner_phone)
        pocket = Pocket.objects.get(partner=partner)
        transactions = Transaction.objects.filter(pocket=pocket).order_by('-created_at')

        # Prepare an in-memory file to write the xlsx data
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Passbook')

        # Define headers
        headers = ['Serial No.', 'Date', 'Credit', 'Debit', 'Available Balance', 'Description']
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)

        # Populate data
        running_balance = pocket.balance
        for row_num, transaction in enumerate(transactions, start=1):
            if transaction.transaction_type == 'credit':
                running_balance -= transaction.amount
            elif transaction.transaction_type == 'debit':
                running_balance += transaction.amount

            worksheet.write(row_num, 0, row_num)  # Serial No.
            worksheet.write(row_num, 1, transaction.created_at.strftime('%Y-%m-%d'))  # Date
            worksheet.write(row_num, 2, transaction.amount if transaction.transaction_type == 'credit' else 0)  # Credit
            worksheet.write(row_num, 3, transaction.amount if transaction.transaction_type == 'debit' else 0)  # Debit
            worksheet.write(row_num, 4, running_balance)  # Available Balance
            worksheet.write(row_num, 5, transaction.get_description_display())  # Description

        workbook.close()

        # Set up the HTTP response
        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="passbook.xlsx"'
        return response

    except Partner.DoesNotExist:
        return HttpResponse("Partner not found", status=404)
    except Pocket.DoesNotExist:
        return HttpResponse("Pocket not found for the partner", status=404)
    
def delete_vehicle_view(request, vehicle_id):
    if request.method == 'POST':
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        vehicle.delete()
        return JsonResponse({'success': True, 'message': 'Vehicle deleted successfully.'})
    
    # If not POST, return an error
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    feedback = Feedback.objects.filter(order=order).first()
    waiting_time = WaitingTime.objects.filter(order=order).first()

    context = {
        'order': order,
        'feedback': feedback,
        'waiting_time': waiting_time,
    }
    return render(request, 'order_detail.html', context)