from django.urls import path
from .views import AdminAPIView
from .views import EmpRegisterView, EmployeeLoginView, EmployeeAPIView
from .views import CustomerRegisterView, CustomerLoginView, CustomerAPI,CustomerCrudAPI
from .views import CarWashServiceView
from .views import ServicesCountAPIView
from .views import LogoutView
from .views import AboutUs,SocialLinks,ReviewAPI,GiveReviews
from .views import SpearPartsList,Purchase,EmpEfficency


urlpatterns = [
 path('admin_api/', AdminAPIView.as_view(), name='admin_api'),
 path('admin_api/<int:pk>/', AdminAPIView.as_view(), name='admin_api'),
 path('emp_register/', EmpRegisterView.as_view(), name='emp_register'),
 path('employee_login/', EmployeeLoginView.as_view(), name='employee_login'),
 path('employee_api/', EmployeeAPIView.as_view(), name='employee_api'),
 path('employee_api/<int:pk>/', EmployeeAPIView.as_view(), name='employee_api'),
 path('customer_register/', CustomerRegisterView.as_view(), name='customer_register'),
 path('customer_login/', CustomerLoginView.as_view(), name='customer_login'),
 path('customer_api/',CustomerAPI.as_view(),name='customer_api'),
 path('customer_api/<int:pk>/', CustomerAPI.as_view(), name='customer_api'),

 path('customer_crud/', CustomerCrudAPI.as_view(), name='customer_crud'),
 path('customer_crud/<int:pk>/', CustomerCrudAPI.as_view(), name='customer_crud'),

 path('carwash_service/',CarWashServiceView.as_view(),name='carwash_service'),
 path('carwash_service/<int:pk>/',CarWashServiceView.as_view(),name='carwash_service'), 
 path('services_count/',ServicesCountAPIView.as_view(),name='services_count'),
 path('logout/', LogoutView.as_view(), name='logout'),
 path('about_us/',AboutUs.as_view(),name='about_us'),
 path('social_links/',SocialLinks.as_view(),name='social_links'),
 path('review/',ReviewAPI.as_view(),name="review"),
 path('see_reviews/',GiveReviews.as_view(),name="see_reviews"),

 path('spear_parts_list/',SpearPartsList.as_view(),name='spear_parts_list'),
 path('spear_parts_list/<int:pk>/',SpearPartsList.as_view(),name='spear_parts_list'),
 path('purchase/',Purchase.as_view(),name='purchase'),
 path('purchase/<int:pk>/',Purchase.as_view(),name='purchase'),

 path('emp_efficency/',EmpEfficency.as_view(),name='emp_efficency')

]