# decorators.py

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "You don't have permission to access this page.")
                return redirect('user_login')  # Redirect to login page
        return wrapper
    return decorator
