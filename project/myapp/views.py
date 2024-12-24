# Standard library imports # Django imports
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, HttpResponse, redirect
from django.contrib.auth import authenticate
from django.core.mail import send_mail

# Third-party imports # Rest Framework imports
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.pagination import PageNumberPagination

# Project-level imports
from project import settings
from .utils import calculate_discount, calculate_final_price

# Local app imports
from .models import Users,CarWashService, Reviewmodel, PartsListModel, Purchasemodel
from .serializer import (
            EmployeeRegistrationSerializer, EmployeeLoginSerializer, EmpAndAdminManage,EmpSee, 
            CustomerRegisterSerializer, CustomerLoginSerializer,CustomerManage,CustomerSee,
            CarWashServiceSerializer, CarWashUpdate, ReviewSerializer,PartsListSerializer, PurchaseSerializer
            )

# For generating access and refresh tokens
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


# Employeee and admin 
# Signup for employees and admin
class EmpRegisterView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to register

    def post(self, request):
        
        try:
            serializer = EmployeeRegistrationSerializer(data=request.data)  # Getting the data from user side
            if not serializer.is_valid():  # Validating the data
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            emp = serializer.save()  # Saving the validated data
            return Response(
                {"message": "success"},
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Login for employees
class EmployeeLoginView(APIView):
    permission_classes = [AllowAny]  # Allow anyone

    def post(self, request):

        try:
            serializer = EmployeeLoginSerializer(data=request.data)  # Getting data from user
            if not serializer.is_valid():  # Validated data
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            email = request.data.get("email")  # Extracting the employee email from the validated data
            password = request.data.get("password")  # Extracting the password from the validated data

            # Check if the username & password provided by the user exists or not
            employee = authenticate(request, username=email, password=password)
            print(employee)
            user_role = Users.objects.filter(role__in=["employee", "admin"], email=email).first()
            print(user_role)

            if [user_role or employee] is None:
                    return Response(
                    { "error": {
                            "non_field_error": ["Email or password is not valid"],
                            "role_error": ["You are not registered as a employee"]
                                } },
                    status=status.HTTP_401_UNAUTHORIZED
                )
            token = get_tokens_for_user(employee)
            return Response(
                    {
                        "token": token,
                        "message": "success"
                    },
                    status=status.HTTP_200_OK
                )

        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Logout for employees
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Allow any user to log out

    def post(self, request):

        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            print(refresh_token)
            token = RefreshToken(refresh_token)
            # Blacklist the token
            token.blacklist()

            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_200_OK,
            )

        except TokenError:
            return Response(
                {"error": "Invalid token or token has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except AuthenticationFailed:
            return Response(
                {"error": "Authentication failed."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


#list of admins  
class AdminAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check if the current user is admin
        if request.user.role != "admin":
            return Response(
                {"detail": "Permission denied. (You are not admin)"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        try:
            admin_name = request.query_params.get("name", None)
            
            if admin_name:
                # Filter by employee ID
                admin = Users.objects.filter(name__icontains=admin_name,role="admin")
                # If no matching user is found, return a 404 Not Found response
                if not admin.exists():
                    return Response(
                        {"detail": f"Admin with Name {admin_name} not found."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            else:
                # Get all employees
                admin = Users.objects.filter(role="admin")
            
            # Serialize the employee data
            serializer = EmpSee(admin, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)    

        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# CRUD for employees, accessible only by admin
class EmployeeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check if the current user is admin
        if request.user.role != "admin":
            return Response(
                {"detail": "Permission denied. (You are not admin)"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        try:
            empname = request.query_params.get("name", None)
            if empname:
                # Filter by employee ID
                employee = Users.objects.filter(name__icontains=empname,role="employee")
                # If no matching user is found, return a 404 Not Found response
                if not employee.exists():
                    return Response(
                        {"detail": f"Employee contains alphabet  {empname} not found."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            else:
                # Get all employees
                employee = Users.objects.filter(role="employee")
            
            # Serialize the employee data
            serializer = EmpSee(employee, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def post(self, request):
        if request.user.role != "admin":  # Check if the user is not an admin
            return Response(
                {"detail": "Permission denied. (You are not admin)"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        try:
            serializer = EmployeeRegistrationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def put(self, request, pk):
        if request.user.role != "admin":
            return Response(
                {"detail": "Permission denied. (You are not admin)"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        try:
            employee = get_object_or_404(Users, pk=pk)
            serializer = EmpAndAdminManage(employee, data=request.data)  # if want to partial .add partial=True after request.data
            
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            emp=Users.objects.filter(last_working_day__isnull=False).update(is_active=False)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def patch(self, request, pk):
        if request.user.role != "admin":
            return Response(
                {"detail": "Permission denied. (You are not admin)"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        try:
            employee = get_object_or_404(Users, pk=pk)
            serializer = EmpAndAdminManage(employee, data=request.data, partial=True)
            
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            value = serializer.save()
            response_data = {
                "message": "Employee updated successfully",
                "serializer": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK) 
       
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def delete(self, request, pk):
        if request.user.role != "admin":
            return Response(
                {"detail": "Permission denied. (You are not admin)"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        try:
            emp = Users.objects.get(pk=pk, role__in=["admin", "employee"])
            emp.delete()
            return Response(
            {"detail": "Employee deleted."},
                    status=status.HTTP_204_NO_CONTENT,
                    )
        except ObjectDoesNotExist:
            return Response({"message": "Invalid pk"}, status=status.HTTP_400_BAD_REQUEST)
    
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Customer
# Signup for customer
class CustomerRegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):

        try:
            serializer = CustomerRegisterSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
            customer = serializer.save()
            return Response(
                {
                    "message": "Registered successfully!",
                    "customer": {
                        "email": customer.email,
                        "first_name": customer.first_name,
                        "last_name": customer.last_name
                    }
                },
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        

# Login for customer
class CustomerLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        try:
            serializer = CustomerLoginSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            customer = authenticate(request, username=email, password=password)
            user_role = Users.objects.filter(role__in=["customer", "admin"], email=email).first()

            if [user_role or customer] is None :
                    return Response({
                            "error": {
                                        "non_field_error": ["Email or password is not valid"],
                                        "role_error": ["You are not registered as a customer"]
                                        }        
                        }, 
                        status=status.HTTP_401_UNAUTHORIZED
                        )
        
            token = get_tokens_for_user(customer)
            return Response(
                            {
                                "token": token, 
                                "message": "success"
                            }, 
                            status=status.HTTP_200_OK)
            
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Crud operation for Customer if user is Admin
class CustomerAPI(APIView):
    permission_classes = [IsAuthenticated]  # Ensure that the user is authenticated
   
    def get(self, request):
        if request.user.role != "admin":
            return Response(
            {"detail": "Permission denied.(you are not admin)"}, 
            status=status.HTTP_403_FORBIDDEN
            )

        try:
            customer_name = request.query_params.get("name", None)
            if customer_name :
                customer = Users.objects.filter(name=customer_name,role="customer")
                            # If no matching user is found, return a 404 Not Found response
                if not customer.exists() or None:
                    return Response(
                        {"detail": f"Employee with Name {customer_name} not found."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            else:    
                customer = Users.objects.filter(role="customer")

            serializer = CustomerSee(customer, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Users.DoesNotExist:
            return Response(
                {"detail": "Customer not found."}, 
                status=status.HTTP_404_NOT_FOUND
                )
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def post(self, request):
        # Check if the current user is admin
        if request.user.role != "admin":
            return Response(
                    {"detail": "Permission denied.(you are not admin)"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            serializer = CustomerRegisterSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
    def put(self,request,pk):
        if request.user.role != "admin":
            return Response(
            {"detail": "Permission denied.(you are not admin)"}, 
            status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            customer = get_object_or_404(Users,pk=pk)
            serializer = CustomerManage(customer,data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def patch(self,request,pk):
        if request.user.role != "admin":
            return Response(
                    {"detail": "Permission denied.(You are not admin)"}, 
                    status=status.HTTP_403_FORBIDDEN
                    )
        
        try:
            customer = get_object_or_404(Users,pk=pk)
            serializer = CustomerManage(customer,data=request.data,partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

            value = serializer.save()
            response_data={"message":"customer added succesfully","serializer":
                        serializer.data}
            return Response(response_data,status=status.HTTP_200_OK)
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


    def delete(self, request, pk):
        if request.user.role != "admin":
            return Response(
                {"detail": "Permission denied.(you are not admin)"}, 
                status=status.HTTP_403_FORBIDDEN
                )
        
        try:
            emp = Users.objects.get(pk=pk, role="customer")
            emp.delete()
            return Response(
            {"detail": "Customer deleted."},
                    status=status.HTTP_204_NO_CONTENT,
                    )
        
        except ObjectDoesNotExist:
            return Response({"message": "Invalid pk"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Crud operation for Customer if user is Customer
class CustomerCrudAPI(APIView):
    permission_classes = [IsAuthenticated]  # Ensure that the user is authenticated
   
    def get(self, request):
        if request.user.role != "customer":
            return Response(
            {"detail": "Permission denied.(you are not a customer)"}, 
            status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            cutomer_id=request.user.id
            customer = Users.objects.filter(id=cutomer_id,role="customer")
            serializer = CustomerSee(customer, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Users.DoesNotExist:
            return Response(
                {"detail": "Customer not found."}, 
                status=status.HTTP_404_NOT_FOUND
                )
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def put(self,request,pk):
        if request.user.role != "customer":
            return Response(
            {"detail": "Permission denied.(you are not customer)"}, 
            status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            cutomer_id=request.user.id
            print(cutomer_id)
            customer = get_object_or_404(Users,pk=pk,id=cutomer_id)
            print(customer)
            serializer = CustomerManage(customer,data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
            
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

# Services
# Making services record here
class CarWashServiceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        if request.user.role != "admin":    
            return Response(
                {"detail": "Permission denied.(You are not admin)"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            customer_name = request.query_params.get("customer_name", None)
            service_id = request.query_params.get("id", None)
            employee_name = request.query_params.get("employee_name", None)
                # Create a Q object to build the filter dynamically
            query = Q()

            if customer_name:
                query &= Q(customer__name__icontains=customer_name)
            if service_id:
                query &= Q(id=service_id)
            if employee_name:
                query &= Q(employee__name__icontains=employee_name)

            services = CarWashService.objects.filter(query)
                            # If no matching user is found, return a 404 Not Found response

            if not services.exists():
                return Response(
                    {"detail": "No matching CarWashService records found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = CarWashServiceSerializer(services, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def post(self, request):
        if request.user.role != "admin":
            return Response(
                {"detail": "Permission denied. (You are not admin)"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            serializer = CarWashServiceSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            customer = serializer.validated_data["customer"]
            service_type = serializer.validated_data["service_type"]
            vehicle_number = serializer.validated_data["vehicle_number"]
            # Calculate discount and final price

            obj=CarWashService.objects.filter(customer_id=customer)
            
            existing_purchase = CarWashService.objects.filter(
                service_type=service_type,vehicle_number=vehicle_number,status="in_progress"
                ).first()
        
            if obj and  existing_purchase:
                return Response("this services for this vehical is already in progess")
            
            discount = calculate_discount(customer)
            final_price = calculate_final_price(service_type, discount)

            service = serializer.save()
            service.final_price = final_price
            service = serializer.save()

            # Reset discount after use (if applicable)
            customer.discount_remaining = 0
            customer.save()

            # Response data to be sent back
            response_data = {
                "message": "Car wash service created successfully!",
                "id": service.id,
                "base_price": CarWashService.SERVICE_PRICE.get(service_type, 0),
                "discount": f"{discount}% applied" if discount > 0 else "No discount applied",
                "final_price": final_price,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def put(self,request,pk):

        if request.user.role != "admin":
            return Response(
                {"detail": "Permission denied. (You are not admin)"},
                status=status.HTTP_403_FORBIDDEN,
                )
        
        try:
            carwash = get_object_or_404(CarWashService,pk=pk)
            serializer = CarWashUpdate(carwash,data=request.data)
            
            statuss = request.data.get("status")
            vh_nos = request.data.get("vehicle_number")
            servi = request.data.get("service_type")

            vehicle_number = carwash.vehicle_number
            type = carwash.service_type
            customer_id = carwash.customer.id

            recorded_status = carwash.status
            if recorded_status:
                return Response("This Services is already completed")

            # status = carwash.status
            print(type,customer_id,vehicle_number,statuss)
                    # Check if a purchase with the same part , and customer already exists

            existing_purchase = CarWashService.objects.filter(
                    service_type=type,status=statuss,vehicle_number=vehicle_number
                ).first()
            
            if not (vh_nos and statuss and servi):
                return Response({"error": "Vehicle number, status, or service cannot be empty."}, status=400)

            if statuss ==  "in_progress" and existing_purchase:
                    return Response("the services for this vehical is already in progess")
            else:
                if not serializer.is_valid():
                    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
                services = serializer.save()

                if not services.status:
                    return Response(
                        {"detail":"Status field is required"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                print(f"Old service_type: {type}, New service_type: {services.service_type}")

                #print(services.customer)
                if  services.service_type != type :
                    # Calculate discount if service_type has changed and price has increased
                    discount = calculate_discount(services.customer)
                    final_price = calculate_final_price(services.service_type, discount)
                    # Update the final price if the new service type has a higher price

                    services.final_price = final_price
                    services.save()

                if services.status != 'completed':
                    return Response(serializer.data,status=status.HTTP_400_BAD_REQUEST)
                
                discount = calculate_discount(services.customer)
                base_price = CarWashService.SERVICE_PRICE.get(request.data.get('service_type', services.service_type), 0)
                email_status = self.send_email(services, base_price, discount,)
                
                response_data = {
                    "message": "Car wash service updated successfully!",
                    "id": services.id,
                    "status": services.status,
                    "service_type" : services.service_type,
                    "base_price" : base_price,
                    "discount": discount,
                    "services_start_date" : services.services_start_date,
                    "services_end_date" : services.services_end_date,
                    "final_price":services.final_price,
                    "email_status": email_status
                    }
                return Response(response_data,status=status.HTTP_200_OK)    
                   
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def send_email(self, service, base_price, discount):
        # Extract customer email
        to_email = service.customer.email
        to_email ='danishp14g@yopmail.com'

        print('email-------',to_email)
        # Calculate base price inside the method
        base_price = CarWashService.SERVICE_PRICE.get(service.service_type, 0)
        discount = service.customer.discount_remaining

        customer = service.customer
        cus_name = customer.name
        service_type = service.service_type
        services_start_date = service.services_start_date
        services_end_date = service.services_end_date
        employee = service.employee
        emp_name = employee.name
        price_before_discount = base_price
        applied_discount = discount,
        final_price = service.final_price
        

        # Create the message
        message = f"""
        Hello {cus_name},

        Your Car Wash service is completed successfully.
        This is the details 
        
        Service Type: {service_type}
        Employee Name : {emp_name} 
        Employee_Email: {employee}
        Base Price: ₹{price_before_discount}
        Discount Applied: {applied_discount }%
        Final Price: ${final_price}

        
        Thank you for using our services!
        """

        try:
        # Send the email
            send_mail(
                subject="Your Car Wash Service is Completed!",
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[to_email])
            
            print('email sent')
            return "Email sent successfully"

        except Exception as e:
                return f"Error sending email: {str(e)}"  # Return error if email sending fails    

    def delete(self, request, pk):
        if request.user.role != "admin":
            return Response(
                {"detail": "Permission denied. (You are not admin)"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        try:
            employee = CarWashService.objects.get(pk=pk)
            employee.delete()
            return Response(
                {"detail": "WashService deleted."},
                status=status.HTTP_204_NO_CONTENT,
            )
        
        except CarWashService.DoesNotExist:
            return Response(
                {"detail": "WashService not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class EmpEfficency(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        if request.user.role != "admin":
            return Response(
                {"detail": "Permission denied. (You are not admin)"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Get query parameters
            employee_name = request.query_params.get("employee_name", None)
            vehicle_number = request.query_params.get("vehicle_number", None)
            service_type = request.query_params.get("service_type", None)
            customer_name = request.query_params.get("customer_name", None)

            # Create a Q object to build the filter dynamically
            query = Q()

            if vehicle_number:
                query &= Q(vehicle_number__istartswith=vehicle_number)
            if service_type:
                query &= Q(service_type__istartswith=service_type)
            if employee_name:
                query &= Q(employee__name__istartswith=employee_name)
            if customer_name:
                query &= Q(customer__name__istartswith=customer_name)

            # Filter services based on dynamic query
            services = CarWashService.objects.filter(query).order_by('id')
                
            # Check if any services match the filter
            if not services.exists():
                return Response("No matching services found", status=status.HTTP_404_NOT_FOUND)

            total_services = 0
            service_data = []
                # Iterate through each service to calculate the total time
            for service in services:
                if service.services_start_date and service.services_end_date:
                    # Calculate the time difference for each service and add to total_time
                    time_taken = (service.services_end_date - service.services_start_date).total_seconds()

                    # Convert to hours and minutes
                    hours, remainder = divmod(int(time_taken), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    time_in_format = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

                    service_data.append({
                    "service_id": service.id,
                    "service_type": service.service_type,
                    "time_taken_hours": time_in_format,
                    "services_start_date": service.services_start_date,
                    "services_end_date": service.services_end_date,
                    "vehicle_nos":service.vehicle_number,
                    "employee_name":service.employee.name,
                    "customer_name":service.customer.name,
                    "status":service.status
                            })
                    
                    total_services +=1 

            # Return the total time in hours
            return Response({"total_services":total_services,
                             "service_details": service_data})

        except Users.DoesNotExist:
            return Response("Employee or Customer not found", status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Sales count
class ServicesCountAPIView(APIView):
    permission_classes=[IsAuthenticated]  # Ensure that the user is authenticated

    def post(self, request):
        if request.user.role != "admin":
            return Response(
            {"detail": "Permission denied.(You are not admin)"},
              status=status.HTTP_403_FORBIDDEN
              )  
        
        try:  
            period = request.data.get("period", "today") # Weekly Sale
        
            services = CarWashService.count_services_by_period(period) 
            count_today = services.count()

            total_earnings = sum(service.final_price  if service.final_price is not None else 0 for service in services)
            serializer = CarWashServiceSerializer(services,many=True)

            # Return the count and period in the response
            response_data = {
                'count': count_today,
                "total_earnings":total_earnings,
                'services': serializer.data,
            }
            return Response(response_data)
        except ValueError as e:
                raise ValidationError(str(e))   # Will return a 400 error with the message
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )   


# About_Us
class AboutUs(APIView):
    permission_classes = [AllowAny]
    
    def get(self,request):
        return HttpResponse("Carsss is a leading car wash company dedicated to providing top-notch vehicle cleaning services. With a focus on quality, convenience, and customer satisfaction, \n we have \n Full Carwash: \n Inside Vacuum: \n Only Body: \n Full with Polish: \n Only Polish: ")


# Sociallinks
class SocialLinks(APIView):
    permission_classes = [AllowAny]
    PLATFORM_REDIRECTS = {
            "facebook": "https://www.facebook.com/login.php/",
            "youtube": "https://www.youtube.com/",
            "instagram": "https://www.instagram.com/accounts/login/",
            "twitter": "https://www.twitter.com/login",
        }
    
    def post(self, request):

        try:
            platform_name = request.data.get("name")
            redirect_url = self.PLATFORM_REDIRECTS.get(platform_name)
            if redirect_url:
                return redirect(redirect_url)
            else:
                return Response(
                    {"error": "Platform not supported"}, 
                    status=status.HTTP_400_BAD_REQUEST
                    )
            
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ReviewPagination(PageNumberPagination):
    page_size = 2 # Number of reviews per page
    page_size_query_param = 'page_size'  # Allow the client to specify page size
    max_page_size = 3  # Limit the maximum page size


class ReviewAPI(APIView):
    permission_classes = [IsAuthenticated]
            
    def post(self,request):

        try:
            serializer = ReviewSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            review = serializer.save()
            response_data = {"message": "review and rating created successfully!", 
                            "review": review.review,
                            "ratings":review.ratings}
            return Response(response_data,
                        status=status.HTTP_201_CREATED
                        )
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

class GiveReviews(APIView):
    permission_classes = [AllowAny]

    def get(self, request):    

        try: 
            reviews = Reviewmodel.objects.all()
            paginator = ReviewPagination()  # Create an instance of the custom pagination class
            paginated_reviews = paginator.paginate_queryset(reviews, request)  # Apply pagination to the queryset
            # Serialize the paginated data
            serializer = ReviewSerializer(paginated_reviews, many=True)
            return paginator.get_paginated_response(serializer.data)  # Return paginated response
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

class SpearPartsList(APIView):
    permission_classes = [IsAuthenticated]    

    def get(self,request):
        if request.user.role != "admin":
            return Response(
                {"detail": "Permission denied. (You are not admin)"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        try:
            parts_name = request.query_params.get("parts_name", None)
            if parts_name :
                partslist = PartsListModel.objects.filter(parts_name__istartswith=parts_name)
                            # If no matching user is found, return a 404 Not Found response
                if not partslist.exists():
                    return Response(
                        {"detail": f"PartsList with id {parts_name} not found."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            else:
                partslist = PartsListModel.objects.all()

            serializer = PartsListSerializer(partslist, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    def post(self,request):
        if request.user.role != "admin":
            return Response(
                {"detail": "Permission denied. (You are not admin)"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        try:
            serializer = PartsListSerializer(data=request.data)
            print(serializer,"---------------------------------")
            if not serializer.is_valid():
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

            value = serializer.save()
            response_data = {"message":"part added succesfully","response_data":
                        serializer.data}
            return Response(
                response_data ,
                status=status.HTTP_201_CREATED)
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    def put(self,request,pk):
        if request.user.role != "admin":
            return Response(
                {"detail": "Permission denied. (You are not admin)"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        try:
            list = get_object_or_404(PartsListModel,pk=pk)
            serializer = PartsListSerializer(list,data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
            value = serializer.save()
            response_data = {"message":"part added succesfully","serializer":
                        serializer.data}
            return Response(response_data,status=status.HTTP_200_OK)
            
        except PartsListModel.DoesNotExist:
            return Response({"error": "Part not found."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    def patch(self,request,pk):
        if request.user.role != "admin":
            return Response(
                {"detail": "Permission denied. (You are not admin)"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        try:
            list = get_object_or_404(PartsListModel,pk=pk)
            serializer = PartsListSerializer(list,data=request.data,partial=True)
            if serializer.is_valid():
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)       
            
            value = serializer.save()
            response_data = {"message":"part added succesfully","serializer":
                        serializer.data}
            return Response(response_data,status=status.HTTP_200_OK)   
          
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 
    
    def delete(self,request,pk):
        if request.user.role != "admin":
            return Response(
                {"detail": "Permission denied. (You are not admin)"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        try:
                parts = PartsListModel.objects.get(pk=pk)
                parts.delete()
                return Response({"message":"part deleted successfully"},status=status.HTTP_204_NO_CONTENT)
        
        except   PartsListModel.DoesNotExist:
            return Response(
                {"message":"part not found "},status=status.HTTP_400_BAD_REQUEST)  
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )       

class Purchase(APIView):

    permission_classes = [IsAuthenticated]
    def get(self,request):
        if request.user.role not in["admin","employee"]:
            return Response(
                {"detail": "Permission denied. (You are not admin)"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        try:
            # purchase_id = request.query_params.get("id",None)
            # if purchase_id :
            #     purchase = Purchasemodel.objects.filter(id=purchase_id)
            #     if not purchase.exists() or None:
            #         return Response(
            #             {"detail": f"Admin with ID {purchase_id} not found."},
            #             status=status.HTTP_404_NOT_FOUND,
            #         )
                
            # else:   
            purchase = Purchasemodel.objects.all()
            data = []
            for item in purchase:
                part_id = item.parts_id  # Access the related ForeignKey field (assuming it points to PartsListModel)
                customer= item.customer
                employee = item.employee
                part = item.parts
                quantity=item.quantity
                parts_prices=part.parts_prices
                total_price = parts_prices * quantity
                
                data.append(
                    {
                     "part_id":part_id,
                     "part_name":part.parts_name,
                     "customer":customer.name,
                     "employee":employee.name,
                     "quantity":quantity,
                     "parts_prices":parts_prices,       
                     "total_price":total_price,
                     })

            serializer = PurchaseSerializer(Purchase,many=True)
            return Response(data,status=status.HTTP_200_OK)
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def post(self, request):
        if request.user.role not in["admin","employee"]:
            return Response(
                {"detail": "Permission denied. (You are not admin)"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            # Validate parts and quantity before proceeding
            parts_id = request.data.get('parts')
            quantity = request.data.get('quantity')
            employee_id = request.data.get('employee')
            customer_id = request.data.get('customer')

            part = get_object_or_404(PartsListModel, id=parts_id)
            employee = get_object_or_404(Users, id=employee_id)
            customer = get_object_or_404(Users, id=customer_id)

            if part.stock_quantity < quantity:
                return Response(
                    {"error": "Not enough stock available for this part."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if a purchase with the same part, employee, and customer already exists
            existing_purchase = Purchasemodel.objects.filter(
                parts=part, employee=employee, customer=customer
            ).first()

            if not existing_purchase:
                purchase = serializer.save() # Save the purchase record
                # Deduct the stock quantity

            # If a record exists, update the quantity and total price
            existing_purchase.quantity += quantity  # Add the new quantity to the existing quantity
            existing_purchase.save()  # Save the updated record

            # Deduct the stock quantity based on the new total purchase
            part.stock_quantity -= quantity
            part.save()

            # Create the purchase record
            serializer = PurchaseSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
            response_data = {
                    "message": "Purchase created successfully!",
                    "serializer": serializer.data
                }
            return Response(response_data, status=status.HTTP_201_CREATED) 
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )    

    def delete(self,request,pk):
        if request.user.role not in["admin","employee"]:
            return Response(
                {"detail": "Permission denied. (You are not admin)"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        try:
                parts = Purchasemodel.objects.get(pk=pk)
                parts.delete()
                return Response({"message":"part deleted successfully"},status=status.HTTP_204_NO_CONTENT)
        
        except Purchasemodel.DoesNotExist:
            return Response(
                {"message":"parchased record not found "},status=status.HTTP_400_BAD_REQUEST) 
        
        except Exception as e:
        # Handle any exception that occurs
            return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 