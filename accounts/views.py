from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.decorators import role_required
from .forms import LoginForm
from accounts.models import CustomUser
from company_side.models import Company
from employees.models import Employee,Attendance,Leave 


def user_logout(request):
    logout(request)
    return redirect(user_login)
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
    present_employees = Attendance.objects.filter(employee__company=company,date=today, status='1').order_by('-check_in_time')
    
    # Count the total number of present employees
    total_present = present_employees.count()
    leaves_today = Leave.objects.filter(start_date__lte=today, end_date__gte=today,status='1')
    
    # Count unique employees on leave today
    employees_on_leave_today = leaves_today.values_list('employee', flat=True).distinct().count()
 
    
    return render(request, "company/index.html", {'present_employees': present_employees, 'total_present': total_present, 'total_employees': total_employees,'employees_on_leave_today':employees_on_leave_today})

@role_required(["2"])
def Employee_view(request):
    employee = Employee.objects.get(user=request.user)
    return render(request,"employee/employee_index.html",{'employee':employee})








def custom_page_not_found(request, exception):
    return render(request, 'accounts/error_404.html', status=404)