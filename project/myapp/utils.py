from . models import CarWashService

def calculate_discount(customer):
    """
    Calculate the applicable discount for a customer based on completed services.
    """
    discount = customer.discount_remaining
    if discount == 0:
        completed_services = CarWashService.objects.filter(
            customer=customer, status="completed"
        ).count()


    free_service_threshold = 50  # Every 50 services grants 1 free service
    free_services_earned = completed_services // free_service_threshold

    # Define the discount ranges using a dictionary
    discount_dict  = {0:0,
            5:5,
            35:20,
            45:30}
    
    discount = 0  # Default to 0 if no match
    for min_services,discount_value in discount_dict .items():
        if min_services <=  completed_services :
            discount = discount_value

    if free_services_earned > customer.free_services_used:
        discount = 100  # Free service
        customer.free_services_used = free_services_earned
        customer.discount_remaining = discount

    else:
        customer.discount_remaining = discount

    customer.save()

    return discount


def calculate_final_price(service_type, discount):
    """
    Calculate the final price based on service type and discount.
    """

    base_price = CarWashService.SERVICE_PRICE.get(service_type, 0)
    if discount == 100:
        discounted_price = 0
        
    else :
        discounted_price = base_price - (base_price * discount / 100)
    return discounted_price
