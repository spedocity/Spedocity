import random
from django.db import models
from django.contrib.auth.hashers import make_password
from vparnter.models import Partner,PartnerInfo,Vehicle
from django.utils import timezone
import datetime
import uuid


class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    state = models.CharField(max_length=100)  # New field for state
    district = models.CharField(max_length=100)  # New field for district
    city = models.CharField(max_length=100)
    work_place = models.CharField(max_length=1000, null=True, blank=True)  # New field for work place
    home_place = models.CharField(max_length=1000, null=True, blank=True)  # New field for home place
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    password = models.CharField(max_length=128)
    otp = models.CharField(max_length=4, editable=False)

    def save(self, *args, **kwargs):
        # Assign a 4-digit OTP if not already set
        if not self.otp:
            self.otp = str(random.randint(1000, 9999))
        # Hash the password before saving the model instance
        if not self.password.startswith('pbkdf2_'):  # Check if password is already hashed
            self.password = make_password(self.password)
        super(Customer, self).save(*args, **kwargs)

        # Create a welcome notification after customer is created
        Notification.objects.create(
            customer=self,
            title="Welcome to Our Service!",
            message=f"Hello {self.first_name}, welcome to our service! We are glad to have you.",
            
        )


    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    

class SliderImage(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='slider_images/')

    def __str__(self):
        return self.title if self.title else f"Slider Image {self.id}"
    
class ViaLocation(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='via_locations')
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.location
    
    # Define status choices before the model class
STATUS_CHOICES = [
    ('booking', 'Booking'),
    ('confirmed', 'Confirmed'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('canceled', 'Canceled'),
]


class Order(models.Model):
    order_id = models.CharField(max_length=15, unique=True, editable=False)  # Unique order ID
    customer = models.ForeignKey('customer', on_delete=models.CASCADE)  # Reference to Customer model
    customer_phone_number = models.CharField(max_length=15)  # Phone number field for the customer
    driver = models.ForeignKey('vparnter.PartnerInfo', on_delete=models.CASCADE)  # Reference to PartnerInfo model
    vehicle = models.ForeignKey('vparnter.Vehicle', on_delete=models.CASCADE)  # Reference to Vehicle model
    date = models.DateTimeField(default=timezone.now)  # Order date
    from_location = models.CharField(max_length=255)  # Pickup location
    to_location = models.CharField(max_length=255)  # Drop-off location
    purpose = models.TextField()  # Purpose of the order
    item_name = models.CharField(max_length=255)  # Name of the item being transported
    load_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Load weight in kg, can be null
    load_image = models.ImageField(upload_to='load_images/', null=True, blank=True)  # Image of the load, can be null
    services = models.CharField(max_length=255)  # Services requested
    distance = models.DecimalField(max_digits=10, decimal_places=2)  # Distance in kilometers
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the order
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2)  # Processing fee
    labor_info = models.JSONField(null=True, blank=True)  # Labor info stored as JSON
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='booking')
    otp = models.CharField(max_length=6, null=True, blank=True)  # OTP field for verification
    verified = models.BooleanField(default=False)  # Checkbox for verification
    otp_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.order_id

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = uuid.uuid4().hex[:15]  # Generate a 15-character unique ID
        super(Order, self).save(*args, **kwargs)

    def create_order_update_notification(self, title, message):
        """Creates a notification for order updates."""
        Notification.objects.create(
            customer=self.customer,
            title=title,
            message=message,
            notification_type='order_update'
        )

    def __str__(self):
        return f"Order {self.order_id} by Customer {self.customer_id}"
    

from django.core.validators import MinValueValidator, MaxValueValidator

class Feedback(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    driver = models.ForeignKey(PartnerInfo, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)  # Add this line
    rating = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return f"Feedback by {self.customer} for {self.driver} on Order {self.order.order_id}"
    
from django.contrib.auth import get_user_model


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('order_update', 'Order Update'),
        ('payment_notification', 'Payment Notification'),
        ('promotional', 'Promotional'),
        ('general', 'General'),
        ('important', 'Important'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='general')

    def __str__(self):
        return f"{self.title} - {self.customer.email} - {'Read' if self.is_read else 'Unread'}"

    class Meta:
        ordering = ['-created_at']  # Show most recent notifications first
