from rest_framework import serializers
from .models import CarWashService,Reviewmodel,PartsListModel,Purchasemodel,Users
from django.contrib.auth.hashers import make_password
import re
from django.utils import timezone
import re
from rest_framework import serializers
from .models import Users  # Import Users model
from rest_framework import status
from rest_framework.response import Response

class EmployeeRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(style={"input_type": "password"}, write_only=True)
    role = serializers.ChoiceField(choices=Users.ROLES)
    name = serializers.CharField(max_length=50)
    salary = serializers.DecimalField(allow_null=True, max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = Users
        fields = ["id", "email", "password", "name", "salary", "password_confirm", "role"]

    def validate_email(self, value):

        if not value:
            raise serializers.ValidationError({"email": "Email is required."})

        if Users.objects.filter(username=value).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})

        return value

    def validate_name(self, value):
        # If name uniqueness is required, check here
        if Users.objects.filter(name=value).exists():
            raise serializers.ValidationError({"name": "This name already exists."})
        
        # Additional name validation logic
        if not value[0].isalpha():
            raise serializers.ValidationError({"name": "Name must start with a letter."})
        
        if not re.match(r'^[A-Za-z0-9@!#$%^&*()_+=\-]*$', value):
            raise serializers.ValidationError({"name": "Employee name can only contain letters, numbers, and special characters."})
        
        if len(value) < 2:
            raise serializers.ValidationError({"name": "Name must be at least 2 characters long."})
        
        if ' ' in value:
            raise serializers.ValidationError({"name": "Name must not contain spaces."})
        
        return value
    

    def validate(self, data):
        password = data.get("password")
        password_confirm = data.get("password_confirm")
        email = data.get("email")
        role = data.get("role")
        salary = data.get("salary")

        # Password confirmation validation
        if password != password_confirm:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        # Password pattern check
        if not password:
            raise serializers.ValidationError({"password": "Password is required."})

        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@!#$%^&*()_+=\-])[A-Za-z\d@!#$%^&*()_+=\-]*$', password):
            raise serializers.ValidationError({"password": "Password must contain at least one letter, one number, and one special character."})

        # Email format and uniqueness check
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise serializers.ValidationError({"email": "Enter a valid email address."})

        if not email:
            raise serializers.ValidationError({"email": "Email is required."})
        

        # Role validation
        if role not in ["admin", "employee"]:
            raise serializers.ValidationError({"role": "Invalid role. Only 'admin' and 'employee' are allowed."})

        # Salary validation for employee and admin
        if role == "employee":
            if salary is None :
                raise serializers.ValidationError({"salary": "Salary field is required for employees."})
        
        if role == "admin":
            if salary is not None and salary != 0:
                raise serializers.ValidationError({"salary": "Salary for admins must be zero or not provided."})

        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password_confirm")
        role = validated_data.pop("role")
        email = validated_data.get("email")
        name = validated_data.get("name")
        salary = validated_data.get("salary")

        # Create the user
        user = Users.objects.create(
            username=email,  # Use email as the username
            email=email,
            name=name,
            role=role,
            salary=salary
        )

        user.set_password(password)
        user.save()

        # Handle special fields for employee users
        if user.role == "employee":
            user.discount_remaining = None
            user.free_services_used = None
            user.services_inhand_count = 0 
            user.services_finished = 0 
            user.save()

        return user

# Emp loginSerializer
class EmployeeLoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    class Meta:
        model = Users
        fields = ["email","password"]


# Emp serializer for crud operation
class EmpAndAdminManage(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.CharField(required=True)
    class Meta:
        model = Users
        fields = ["email","name", "salary", "role", "password", "last_working_day", "is_active"]
    
    def validate(self, data):
        password = data.get("password")
        # If password is provided, hash it
        if password:
            data["password"] = make_password(password)
            
        role = data.get("role")
        if role not in ["admin", "employee"]:
            raise serializers.ValidationError({"role": "Invalid role. Only 'admin' and 'employee' are allowed."})
        
        return data
    

class EmpSee(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ["id","name", "salary", "role", "last_working_day","services_inhand_count","services_finished"]


# Customer
class CustomerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(style={"input_type": "password"}, write_only=True)
    role = serializers.ChoiceField(choices=Users.ROLES)
    name = serializers.CharField(max_length=50)
    salary = serializers.DecimalField(allow_null=True, max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = Users
        fields = ["id", "email", "password", "name", "salary", "password_confirm", "role"]

    def validate_email(self, value):

        if not value:
            raise serializers.ValidationError({"email": "Email is required."})

        if Users.objects.filter(username=value).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})

        return value

    def validate_name(self, value):
        # If name uniqueness is required, check here
        if Users.objects.filter(name=value).exists():
            raise serializers.ValidationError({"name": "This name already exists."})
        
        # Additional name validation logic
        if not value[0].isalpha():
            raise serializers.ValidationError({"name": "Name must start with a letter."})
        
        if not re.match(r'^[A-Za-z0-9@!#$%^&*()_+=\-]*$', value):
            raise serializers.ValidationError({"name": " name can only contain letters, numbers, and special characters."})
        
        if len(value) < 2:
            raise serializers.ValidationError({"name": "Name must be at least 2 characters long."})
        
        if ' ' in value:
            raise serializers.ValidationError({"name": "Name must not contain spaces."})
        
        return value
    

    def validate(self, data):
        password = data.get("password")
        password_confirm = data.get("password_confirm")
        email = data.get("email")
        role = data.get("role")
        salary = data.get("salary")

        # Password confirmation validation
        if password != password_confirm:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        # Password pattern check
        if not password:
            raise serializers.ValidationError({"password": "Password is required."})

        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@!#$%^&*()_+=\-])[A-Za-z\d@!#$%^&*()_+=\-]*$', password):
            raise serializers.ValidationError({"password": "Password must contain at least one letter, one number, and one special character."})

        # Email format and uniqueness check
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise serializers.ValidationError({"email": "Enter a valid email address."})

        if not email:
            raise serializers.ValidationError({"email": "Email is required."})
        
        if role != "customer":
            raise serializers.ValidationError({"role": "Invalid role. Only 'Customer' are allowed."})
        
        # Salary validation for employee and admin
        if salary is not None and salary != 0:
                raise serializers.ValidationError({"salary": "Salary should not be provided."})
        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password_confirm")
        role = validated_data.pop("role")
        email = validated_data.get("email")
        name = validated_data.get("name")

        # Create the user
        user = Users.objects.create(
            username=email,  # Use email as the username
            email=email,
            name=name,
            role=role,
        )

        user.set_password(password)
        user.save()

        # Handle special fields for employee users
        if user.role == "customer":
            user.discount_remaining = 0
            user.free_services_used = 0
            user.salary=None
            user.save()

        return user
    

# Customer Login Serializer
class CustomerLoginSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    class Meta:
        model = Users
        fields = ["email","password"]


# Customer serializer for crud operation
class CustomerManage(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.CharField(required=True)
    class Meta:
        model = Users
        fields = ["email","name", "salary", "role", "password", "last_working_day", "is_active"]
    
    def validate(self, data):
        password = data.get("password")
        # If password is provided, hash it
        if password:
            data["password"] = make_password(password)
            
        role = data.get("role")
        if role != "customer":
            raise serializers.ValidationError({"role": "Invalid role. Only 'Customer' are allowed."})
            
        return data


class CustomerSee(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ["id","email","name", "role","discount_remaining","free_services_used"]


# Serializer for records of serives
class CarWashServiceSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())
    customer = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())
    service_type = serializers.ChoiceField(choices=CarWashService.SERVICE_TYPE_CHOICES,required=True)

    class Meta:
        model = CarWashService
        fields = ["id", "service_type", "employee", "customer", "status", "final_price","vehicle_number"]

    def validate_vehicle_number(self, value):
        # Custom validation for vehicle number
        if not value:
            raise serializers.ValidationError("Vehicle number cannot be empty.")
        return value

    def validate_status(self, value):
        instance = self.instance
        if instance and instance.status == "completed" and value != "completed":
            raise serializers.ValidationError("You cannot change the status of a completed service.")
        return value

    # Check if the employee exists in the database
    def validate_employee(self, value):
        return value
    # Check if the customer exists in the database
    def validate_customer(self, value):
        return value

class CarWashUpdate(serializers.ModelSerializer):
    service_type = serializers.ChoiceField(choices=CarWashService.SERVICE_TYPE_CHOICES,required=True)  # Ensures field is mandatory
    status = serializers.ChoiceField(choices=CarWashService.STATUS,required=True)
    vehicle_number = serializers.CharField(required=True)

    class Meta:
        model = CarWashService
        fields = ["service_type", "status","vehicle_number"]  # Only these fields can be updated in the PUT request

    def validate_vehicle_number(self, value):
        # Custom validation for vehicle number
        if not value:
            raise serializers.ValidationError("Vehicle number cannot be empty.")
        return value

    def validate_status(self, value):
        instance = self.instance
        if instance and instance.status == "completed" and value != "completed":
            raise serializers.ValidationError("You cannot change the status of a completed service.")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviewmodel
        fields = ["ratings","review"]

    def validate_ratings(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Ratings must be between 1 and 5.")
        if not isinstance(value, int):
            raise serializers.ValidationError("Rating must be an integer.")
        return value
    
    def validate_review(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("Review text cannot be empty.")
        return value
    
class PartsListSerializer(serializers.ModelSerializer):
    
    parts_manufacture_date = serializers.CharField(required=True)  # Ensures field is mandatory
    class Meta:
        model = PartsListModel
        fields = ["id","parts_name", "parts_prices", "parts_manufacture_date", "parts_expire_date", "company_name", "description","stock_quantity"]

    def validate_parts_expire_date(self, value):
        """
        Validate that the expiry date is later than the manufacture date.
        """
        
        manufacture_date = self.initial_data.get("parts_manufacture_date") #to get the data from serializer
        try:
            manufacture_date = timezone.datetime.strptime(manufacture_date, "%Y-%m-%d").date()
            if value <= manufacture_date:
                raise serializers.ValidationError("Expiry date should be later than the manufacture date.")  
        except:
            return Response({"error":"Manufacture date must be a valid format or required"}, status=status.HTTP_404_NOT_FOUND)
        return value

    def validate_parts_name(self, value):
        if not value:
            raise serializers.ValidationError("parts name cant be empty")
        return value     


class PurchaseSerializer(serializers.ModelSerializer):
    parts = serializers.PrimaryKeyRelatedField(queryset=PartsListModel.objects.all())
    employee = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())
    customer = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())
    quantity = serializers.IntegerField(min_value=1, required=True)  # Ensure quantity is positive

    class Meta:
        model = Purchasemodel
        fields = ["id","parts", "customer", "employee", "quantity"]

    def validate_quantity(self, value):
        """
        Custom validation for quantity. Ensure it is greater than 0 and less than or equal to available stock.
        """
        if value < 1:
            raise serializers.ValidationError("Quantity must be a positive integer.")
        return value

    def validate(self, data):
        """
        Custom validation for the entire data to ensure stock availability.
        """
        part = data.get("parts")
        # Ensure the part exists in the database
        if part is None:
            raise serializers.ValidationError({"parts": "The part does not exist."})
        return data