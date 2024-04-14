from django.urls import reverse
from company_side.models import Company

def company_name(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Check if the user is accessing the admin site
        if request.path.startswith(reverse('admin:index')):
            return {}  # Return an empty dictionary for admin pages
        else:
            # If not accessing admin, try to get the company name for the user
            try:
                company = Company.objects.get(user=request.user)
                company_name = company  # Use the company name if found
            except Company.DoesNotExist:
                company_name = "Not Found"  # Set default company name if user is not associated with a company
    else:
        company_name = "Guest"  # Set default company name if user is not authenticated

    return {'company_name': company_name}