from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.decorators import role_required
from .forms import LoginForm
from accounts.models import CustomUser
from company_side.models import Company
from employees.models import Employee,Attendance 

# Create your views here.
def user_login(request):
    # if request.user.is_authenticated:
    #     # If the user is already logged in, redirect them to the home page
    #     return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        try:
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                print(username,password)
                user = authenticate(request, username=username, password=password)
                print(user)
                if user is not None:
                    login(request, user)
                
                    return redirect('home')  # Redirect to appropriate page after login
                else:
                    messages.error(request, 'Invalid username or password.')
                    return redirect('user_login')
        except Exception as e:
            messages.error(request, 'An error occurred during login.')
            return redirect('user_login')
    else:
        form = LoginForm()
    
    return render(request,"accounts/login.html",{'form': form})



@login_required
def home(request):
    try:
        if request.user.role == '1':
            print("INNN ")
            return redirect('Company_view')
        elif request.user.role == '2':
            return redirect('Employee_view')
        else:
            # Handle other roles or unauthorized access
            messages.error(request, 'Unauthorized access.')
            return redirect('user_login')
    except Exception as e:
        messages.error(request, 'An error occurred.')
        return redirect('user_login')

@role_required(["1"])
def Company_view(request):
    # Get today's date
    today = timezone.now().date()
    
    # Get the logged-in user's company
    company= Company.objects.get(user=request.user)
    # Count the total number of employees belonging to the company
    total_employees = Employee.objects.filter(company=company).count()
    
    # Filter attendance records for present employees today and order by check-in time (latest first)
    present_employees = Attendance.objects.filter(date=today, status='1').order_by('-check_in_time')
    
    # Count the total number of present employees
    total_present = present_employees.count()
    
    return render(request, "company/index.html", {'present_employees': present_employees, 'total_present': total_present, 'total_employees': total_employees})

@role_required(["2"])
def Employee_view(request):
    return render(request,"employee/facecam.html")