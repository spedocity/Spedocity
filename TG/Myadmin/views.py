from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def ahome(request):
    return render(request,"Ahome.html")

def aorder(request):
    return render(request,"a_orders.html")

def aemployee(request):
    return render(request,'aemployee.html')