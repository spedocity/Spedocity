from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from datetime import date
from Myadmin.models import Employee
from customer.models import Order, Customer
from vparnter.models import PartnerInfo, Vehicle
from django.db.models import Sum
# Create your views here.
def ahome(request):
    # Calculate statistics
    total_partners = PartnerInfo.objects.count()  # Total number of partners
    total_customers = Customer.objects.count()  # Total number of customers
    orders_today = Order.objects.filter(date=date.today()).count()  # Orders placed today
    total_orders = Order.objects.count()  # Total number of orders

    context = {
        'total_partners': total_partners,
        'total_customers': total_customers,
        'orders_today': orders_today,
        'total_orders': total_orders,
    }
    return render(request,"Ahome.html",context)

def aorder(request):
    orders = Order.objects.all().order_by('-date')

    context = {
        'orders': orders,
    }
    return render(request,"a_orders.html",context)

def aemployee(request):
    return render(request,'aemployee.html')

def customer_list_view(request):
    # Fetch all customers from the database
    customers = Customer.objects.all()

    context = {
        'customers': customers,
    }
    return render(request, 'customer_list.html', context)

def partner_list(request):
    partner_info_list = PartnerInfo.objects.select_related('partner').all()
    return render(request, 'partner_list.html', {'partner_info_list': partner_info_list})

def partner_details_view(request, partner_id):
    # Retrieve PartnerInfo based on partner_id
    partner_info = get_object_or_404(PartnerInfo, partner_id=partner_id)
    
    # Retrieve vehicles associated with the partner
    vehicles = Vehicle.objects.filter(driver=partner_info)

    total_orders = Order.objects.filter(driver=partner_info).count()
    total_earnings = Order.objects.filter(driver=partner_info).aggregate(total=Sum('price'))['total'] or 0
    
    # Retrieve all orders associated with the partner
    all_orders = Order.objects.filter(driver=partner_info)
    
    # Pass partner_info and vehicles to the template
    context = {
        'partner_info': partner_info,
        'vehicles': vehicles,
        'total_orders': total_orders,
        'total_earnings': total_earnings,
        'all_orders': all_orders,
    }
    
    return render(request, 'partner_details.html', context)

from django.contrib.auth.hashers import check_password

def alogin(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # Get email from POST data
        password = request.POST.get('password')

        try:
            # Query the Employee model using email
            employee = Employee.objects.get(email=email)

            # Validate password using check_password to compare with hashed password
            if check_password(password, employee.password):
                # Manually set session data without using `login`
                request.session['employee_id'] = employee.id  # Store employee ID
                request.session['employee_name'] = f'{employee.first_name} {employee.last_name}'  # Store employee name
                print(request.session) 

                return JsonResponse({'success': 'Login successful!'}, status=200)

            else:
                return JsonResponse({'error': 'Invalid password.'}, status=400)

        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Email not registered.'}, status=400)

    elif request.method == 'GET':
        return render(request, 'alogin.html')
    
def alogout_view(request):
    logout(request)
    return redirect('ahome')