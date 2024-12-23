from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta
from django.conf import settings
from django.core.validators import RegexValidator

# Base User Model
class Users(AbstractUser):
    # Add any common fields if necessary
    ROLES = (
        ('admin', 'Admin'),
        ('employee', 'Employee'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=10, choices=ROLES,default='customer')
    name = models.CharField(max_length=50,unique=True,null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    joining_date = models.DateField(auto_now_add=True)
    last_working_day = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    email = models.EmailField(unique=True)
    discount_remaining = models.IntegerField(null=True, blank=True)  # Tracks remaining discount percentage
    free_services_used = models.IntegerField(null=True, blank=True)  # Track how many free services used

    services_inhand_count = models.PositiveIntegerField(null=True, blank=True) # if services is in_progress)
    services_finished = models.PositiveIntegerField(null=True, blank=True) # if services is completed)


# Service records    
class CarWashService(models.Model):

    SERVICE_TYPE_CHOICES = [
    ("full_carwash", "Full Carwash - 70 Rupees"),
    ("inside_vacuum", "Inside Vacuum - 40 Rupees"),
    ("only_body", "Only Body - 30 Rupees"),
    ("full_with_polish", "Full with Polish - 100 Rupees"),
    ("only_polish", "Only Polish - 30 Rupees"),
    ]
# Defining prices for each service type
    SERVICE_PRICE = {
    "full_carwash": 70,
    "inside_vacuum": 40,
    "only_body": 30,
    "full_with_polish": 100,
    "only_polish": 30,
    }

    STATUS=[("completed", "Complete"),
             ("in_progress", "In Progress"),
                                  ] 
    
    vehicle_number_validator = RegexValidator(
        regex=r'^[A-Z]{2}\d{2}[a-z]{2}\d{4}$',
        message="Vehicle number must be in the format 'XX00XX0000' (e.g.:-'MH14fu1234')."
    )
                                  
    # Model fields
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES, default="full_carwash")
    employee = models.ForeignKey('Users', null=True, blank=True, on_delete=models.CASCADE, 
                                 related_name="CarWashService")
    customer = models.ForeignKey('Users', on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS,max_length=15, 
                                  default="in_progress")
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)    
    vehicle_number = models.CharField( max_length=10,
                        validators=[vehicle_number_validator], 
                        help_text="Enter the vehicle number in the format 'XX00XX0000'. eg:-'MH14fu1234'",
                        null=False, blank=False 
                        )

    services_start_date = models.DateTimeField(auto_now_add=True)# jab created honga {created_at}
    services_end_date = models.DateTimeField(null=True, blank=True)  # Updated when completed

    def time_taken_for_services(self):
        """Calculate the time difference between start and end."""
        if self.services_end_date:
            return self.services_end_date - self.services_start_date
        return None

    def save(self, *args, **kwargs):
    # Check if the status is changing to "completed"
        if self.status == 'completed' and not self.services_end_date:
            self.services_end_date = now()
            # Update the employee's service counts
            employee = self.employee  # The employee who performed the service
            if employee.services_inhand_count > 0:
                employee.services_inhand_count -= 1  # Decrease services in hand 
            employee.services_finished += 1  # Increase services finished
            employee.save()

        elif self.pk is None:  # New service being created
            employee = self.employee  # The employee who will perform the service
            employee.services_inhand_count += 1  # Increase services in hand
            employee.save()

        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.service_type} "

    @property
    def price(self):
        """Returns the price based on the selected service type."""
        return self.SERVICE_PRICE.get(self.service_type, 0)  # Default to 0 if no match
    
    # Making a static method in service for sales count
    @staticmethod
    def count_services_by_period(period):
        """Count services based on the period selected by the user."""
        today = timezone.now().date()
        today_date = CarWashService.objects.filter(services_start_date__date=today)

        yesterday = today - timedelta(days=1)
        yesterday_date = CarWashService.objects.filter(services_start_date__date=yesterday)

        start_of_week = today - timedelta(days=today.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday
        week_date = CarWashService.objects.filter(services_start_date__gte=start_of_week, services_start_date__lte=end_of_week)

        month_date = CarWashService.objects.filter(services_start_date__month=today.month, services_start_date__year=today.year)

        period_dict={
            "today":today_date,
            "yesterday":yesterday_date,
            "weekly":week_date,
            "monthly":month_date
        }

        count = period_dict.get(period, None)

        if count is not None:
            return count  # Return the count of services for the given period
        else:
            return 0  # Return 0 if period is invalid


class Reviewmodel(models.Model):

    RATINGS_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]
    #positive small Integer
    ratings = models.PositiveSmallIntegerField(choices=RATINGS_CHOICES, default=3)
    review = models.CharField(max_length=500,blank=False)

    def __str__(self):
        return f"{self.ratings()}"
    
class PartsListModel(models.Model):

    parts_name = models.CharField(max_length=50,unique=True)
    parts_prices = models.PositiveIntegerField()
    parts_manufacture_date = models.DateField(null=False) 
    parts_expire_date = models.DateField(null=False)
    company_name = models.CharField(max_length=50,null=False,default="local")
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    stock_quantity = models.PositiveIntegerField(default=1, help_text="Number of items in stock.")
    

class Purchasemodel(models.Model):

    parts = models.ForeignKey('PartsListModel', related_name='parts_purchase', on_delete=models.CASCADE)
    customer = models.ForeignKey('Users', related_name='parts_Customer', on_delete=models.CASCADE)
    employee = models.ForeignKey('Users', related_name='parts_emp', on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now=True)
    
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        # Calculate total price based on quantity
        self.total_price = self.parts.parts_prices * self.quantity
        super().save(*args, **kwargs)