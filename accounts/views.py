from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm

# Create your views here.
def user_login(request):
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
            return redirect('Company')
        elif request.user.role == '2':
            return redirect('Employee')
        else:
            # Handle other roles or unauthorized access
            messages.error(request, 'Unauthorized access.')
            return redirect('user_login')
    except Exception as e:
        messages.error(request, 'An error occurred.')
        return redirect('user_login')

@login_required
def Company(request):
    return render(request,"company/index.html")

@login_required
def Employee(request):
    return render(request,"employee/facecam.html")