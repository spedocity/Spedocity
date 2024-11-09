from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.

def app_media_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/myapp/<filename>
    return f'myapp/{filename}'

class Partner(models.Model):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    phone_no = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # To store the hashed password

    def set_password(self, raw_password):
        """Hash the password and store it."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check the raw password against the stored hashed password."""
        return check_password(raw_password, self.password)

    def __str__(self):
        return f'{self.firstname} {self.lastname}'
    
class PartnerInfo(models.Model):
    partner = models.ForeignKey('Partner', on_delete=models.CASCADE)  # Reference to Partner model
    alternative_phone = models.CharField(max_length=15, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)  # Date of birth
    adhar_no = models.CharField(max_length=14, unique=True)  # Aadhaar number
    dl = models.CharField(max_length=20, unique=True)  # Driving license number
    dl_document = models.FileField(upload_to='dl_documents/', null=True, blank=True)  # File upload for driving license
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True) 
    address = models.TextField(null=True, blank=True)
    driver_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f'{self.partner.firstname} {self.partner.lastname} - Partner Info'

from django.db import models

class VehicleCategory(models.Model):
    WEIGHT_CATEGORIES = [
        (1, '0 to 100 kg'),
        (2, '0 to 250 kg'),
        (3, '0 to 650 kg'),
        (4, '0 to 1000 kg'),
        (5, '0 to 1500 kg'),
        (6, '0 to 2000 kg'),
        (7, 'Passenger'),
        (8, 'Ambulance')
    ]
    weight_category = models.IntegerField(choices=WEIGHT_CATEGORIES, unique=True)
    base_price_per_km = models.DecimalField(max_digits=5, decimal_places=2)  # Base price per kilometer for this category
    image = models.ImageField(upload_to='vehicle_category_images/') 
    def __str__(self):
        return self.get_weight_category_display()

class LoadPricing(models.Model):
    vehicle_category = models.ForeignKey(VehicleCategory, on_delete=models.CASCADE)  # Link to VehicleCategory
    capacity_usage = models.CharField(max_length=20)  # Capacity usage (e.g., '>3/4', '>2/4', '>1/4', 'else')
    price_per_km = models.DecimalField(max_digits=5, decimal_places=2)  # Load weight price per kilometer

    def __str__(self):
        return f'{self.vehicle_category} - {self.capacity_usage}: {self.price_per_km} rupees/km'


class Vehicle(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    VEHICLE_STATUS_CHOICES = [
        ('running', 'Running'),
        ('standing', 'Standing'),
    ]

    PURPOSE_CHOICES = [
        ('passenger', 'Passenger'),
        ('logistics', 'Logistics'),
        ('ambulance','Ambulance')
    ]

    vehicle_id = models.CharField(max_length=20, unique=True)  # Unique Vehicle ID
    driver = models.ForeignKey('PartnerInfo', on_delete=models.CASCADE)  # Driver as foreign key
    name = models.CharField(max_length=50)  # Vehicle name
    owner_name = models.CharField(max_length=50)  # Vehicle owner name
    vehicle_type = models.CharField(max_length=30)  # Type of vehicle (e.g., truck, van)
    photo = models.ImageField(upload_to='vehicle_photos/', null=True, blank=True)  # Vehicle photo
    load_capacity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Make this nullable
    rc_card_photo = models.ImageField(upload_to='rc_card_photos/', null=True, blank=True)  # RC card photo
    insurance = models.FileField(upload_to='insurance_documents/', null=True, blank=True)  # Insurance document
    location = models.CharField(max_length=500)  # Vehicle location
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='inactive')  # Active/Inactive status
    vehicle_status = models.CharField(max_length=10, choices=VEHICLE_STATUS_CHOICES, null=True, blank=True)  # Running/Standing status
    state = models.CharField(max_length=100, default='Unknown')  # Registered state
    district = models.CharField(max_length=100, default='Unknown')  # Registered district
    taluk_town = models.CharField(max_length=100, default='Unknown')  # Registered taluk or town
    vehicle_category = models.ForeignKey(VehicleCategory, on_delete=models.SET_NULL, null=True, blank=True)  # Assigned vehicle category
    vehicle_purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES, default='logistics')  # Passenger or Logistics

    def __str__(self):
        return f'{self.name} ({self.vehicle_id})'

    def save(self, *args, **kwargs):
    # Ensure that the vehicle category is assigned based on purpose and load capacity
        if self.vehicle_purpose == 'passenger':
            # Assign the passenger category and skip load capacity checks
            self.vehicle_category = VehicleCategory.objects.get(weight_category=7)

        elif self.vehicle_purpose == 'ambulance':
        # Assign the ambulance category (8th category) and skip load capacity checks
            self.vehicle_category = VehicleCategory.objects.get(weight_category=8)

        else:
            # Handle the case where load_capacity is None
            if self.load_capacity is None:
                raise ValueError("Load capacity must be provided for logistics vehicles.")

            # Ensure that load_capacity is a number (convert if needed)
            if isinstance(self.load_capacity, str):
                try:
                    self.load_capacity = float(self.load_capacity)
                except ValueError:
                    raise ValueError("Load capacity must be a number.")
            
            load_capacity_in_kg = self.load_capacity  # Convert tons to kg if needed

            # Assign vehicle category based on load capacity for logistics
            if load_capacity_in_kg <= 100:
                self.vehicle_category = VehicleCategory.objects.get(weight_category=1)
            elif load_capacity_in_kg <= 250:
                self.vehicle_category = VehicleCategory.objects.get(weight_category=2)
            elif load_capacity_in_kg <= 650:
                self.vehicle_category = VehicleCategory.objects.get(weight_category=3)
            elif load_capacity_in_kg <= 1000:
                self.vehicle_category = VehicleCategory.objects.get(weight_category=4)
            elif load_capacity_in_kg <= 1500:
                self.vehicle_category = VehicleCategory.objects.get(weight_category=5)
            elif load_capacity_in_kg <= 2000:
                self.vehicle_category = VehicleCategory.objects.get(weight_category=6)
            else:
                raise ValueError("Load capacity exceeds the supported limit.")
        
        # Call the parent class's save method
        super().save(*args, **kwargs)

class Pricing(models.Model):
    vehicle_category = models.ForeignKey(VehicleCategory, on_delete=models.CASCADE)  # Vehicle category for the pricing
    distance_km = models.FloatField()  # Distance traveled in kilometers
    load_weight = models.FloatField()  # Load weight in kg

    def get_load_pricing(self):
        # Calculate the fraction of the capacity used
        load_percentage = self.load_weight / (self.vehicle_category.get_max_load_capacity_in_kg())  # Assuming max load capacity in kg

        # Determine the pricing based on load capacity usage
        if load_percentage > 0.75:
            return LoadPricing.objects.get(vehicle_category=self.vehicle_category, capacity_usage='>3/4').price_per_km
        elif load_percentage > 0.5:
            return LoadPricing.objects.get(vehicle_category=self.vehicle_category, capacity_usage='>2/4').price_per_km
        elif load_percentage > 0.25:
            return LoadPricing.objects.get(vehicle_category=self.vehicle_category, capacity_usage='>1/4').price_per_km
        else:
            return LoadPricing.objects.get(vehicle_category=self.vehicle_category, capacity_usage='else').price_per_km

    def calculate_charges(self):
        # Calculate base price and load weight price
        base_price_per_km = self.vehicle_category.base_price_per_km
        load_price_per_km = self.get_load_pricing()

        # Calculate total charges based on distance
        base_charges = base_price_per_km * self.distance_km
        load_charges = load_price_per_km * self.distance_km
        return base_charges + load_charges

    def calculate_final_price(self):
        charges = self.calculate_charges()
        final_price = charges + (0.40 * charges) + 20 + (0.30 * charges)
        return final_price * 1.10  # Additional 10% increase

    def __str__(self):
        return f'Pricing for {self.vehicle_category} - {self.distance_km} km'
    

class Pocket(models.Model):
    partner = models.ForeignKey('Partner', on_delete=models.CASCADE)  # Link to Partner model
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE)  # Link to Vehicle model
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Balance in the pocket
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the pocket was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for when the pocket was last updated

    def __str__(self):
        return f'Pocket of {self.partner.firstname} {self.partner.lastname} - Vehicle: {self.vehicle.name}'

    def add_funds(self, amount, description):
        """Add funds to the pocket and log the transaction."""
        if amount > 0:
            self.balance += amount
            self.save()
            Transaction.objects.create(
                pocket=self,
                amount=amount,
                transaction_type='credit',
                description=description  # Pass the description to the transaction
            )
            return True
        return False

    def deduct_funds(self, amount, description):
        """Deduct funds from the pocket and log the transaction."""
        if 0 < amount <= self.balance:
            self.balance -= amount
            self.save()
            Transaction.objects.create(
                pocket=self,
                amount=amount,
                transaction_type='debit',
                description=description  # Pass the description to the transaction
            )
            return True
        return False
    

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]

    DESCRIPTION_CHOICES = [
        ('subscription_fee', 'Subscription Fee'),
        ('processing_fee', 'Processing Fee'),
    ]

    pocket = models.ForeignKey('Pocket', on_delete=models.CASCADE, related_name='transactions')  # Link to the Pocket model
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount for the transaction
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)  # Type of transaction
    description = models.CharField(max_length=20, choices=DESCRIPTION_CHOICES)  # Description of the transaction
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the transaction was made

    def __str__(self):
        return f'{self.transaction_type.capitalize()} of {self.amount} ({self.get_description_display()}) on {self.created_at}'

    class Meta:
        ordering = ['-created_at']  # Order transactions by date, latest first


class DriverNotification(models.Model):
    driver = models.ForeignKey( 'PartnerInfo', on_delete=models.CASCADE)
    order = models.ForeignKey('customer.Order', on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for {self.driver} - Order {self.order.id}'
    
    def delete_previous_notification(self):
        """Delete the previous notification for the same order, if it exists."""
        # Get the previous notification (if any)
        previous_notification = DriverNotification.objects.filter(order=self.order).exclude(id=self.id).first()
        if previous_notification:
            previous_notification.delete()

    def save(self, *args, **kwargs):
        # Delete the previous notification for the same order
        self.delete_previous_notification()
        super().save(*args, **kwargs)

class WaitingTime(models.Model):
    order = models.ForeignKey('customer.Order', on_delete=models.CASCADE, related_name="waiting_times")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)  # Store the calculated duration
    waiting_time_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Add a field for price

    def save(self, *args, **kwargs):
        # If end_time is set, calculate duration
        if self.end_time:
            self.duration = self.end_time - self.start_time
            # Calculate the waiting time price (1.5 rupees per minute)
            total_minutes = self.duration.total_seconds() / 60  # Convert duration to minutes
            self.waiting_time_price = round(total_minutes * 1.5)  # Round to nearest value
        super().save(*args, **kwargs)

    def get_formatted_duration(self):
        """Return the duration as a formatted string (hh:mm) without milliseconds."""
        if self.duration:
            total_seconds = int(self.duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{hours}h {minutes}m"
        return "0h 0m"  # Default if no duration
     
    def __str__(self):
        return f"Waiting Time for Order {self.order.order_id} - Duration: {self.get_formatted_duration()}, Price: {self.waiting_time_price} rupees"  
