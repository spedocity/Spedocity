from django.db import models
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator

class Employee(models.Model):
    # Validator for employee_id to ensure correct format
    employee_id_validator = RegexValidator(
        regex=r'^EHASCD[A-Z]{3}$',
        message='Employee ID must be in the format EHASCDDXXX'
    )
    
    # Employee Details
    employee_id = models.CharField(max_length=12, unique=True, validators=[employee_id_validator])  # Format: EHASCDDXXX
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    address = models.TextField()
    
    # Aadhaar and Joining Info
    aadhaar_number = models.CharField(max_length=12, unique=True)  # Aadhaar numbers are 12 digits long
    joining_date = models.DateField()

    # Secure Password Field
    password = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        # Hash the password before saving if it's a new employee or password is being updated
        if not self.pk or 'password' in self.get_dirty_fields():  # 'get_dirty_fields()' checks for updates (optional)
            self.password = make_password(self.password)
        super(Employee, self).save(*args, **kwargs)

    def _str_(self):
        return f"{self.employee_id} - {self.first_name} {self.last_name}"