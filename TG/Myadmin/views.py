from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from datetime import date
from customer.models import Order, Customer
from vparnter.models import PartnerInfo

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
    partner_info = get_object_or_404(PartnerInfo, partner_id=partner_id)
    return render(request, 'partner_details.html', {'partner_info': partner_info})