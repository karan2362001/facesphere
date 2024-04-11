from django.shortcuts import render,redirect
from accounts.models import CustomUser
from .models import Company,Branch
from employees.models import Employee
from accounts.decorators import role_required
from django.contrib.auth.hashers import make_password
from django.contrib import messages
import face_recognition
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import json
# Create your views here   


def face_enc(image):
    try:
        image = face_recognition.load_image_file(image)
        face_encodings = face_recognition.face_encodings(image)
        if face_encodings:
            face_encoding = face_encodings[0].tolist()  # Save the first face encoding as JSON string
            return face_encoding
        else:
            return None  # No face detected
    except Exception as e:
        print(f"Error generating face encoding: {e}")
        return None
@role_required(["1"])
def add_employee(request):
    if request.method == 'POST':
        # Extract form data from the request
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        # Extract and save the image file
        picture = request.FILES.get('picture')
        # Save the other form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')
        position = request.POST.get('position')
        salary = request.POST.get('salary')
        face_encoding = face_enc(picture)
        company = Company.objects.get(user=request.user)
        if face_encoding is None:
            messages.error(request, 'Could not generate face encoding from the provided image.')
            return redirect('add_employee')
        if password1 == password2:
                # Check if the username already exists
                if CustomUser.objects.filter(username=username).exists():
                    messages.error(request, 'Username already exists!')
                    return redirect('add_employee')
                
                else:
                    try:
                        employee_user=CustomUser.objects.create(username=username,first_name=first_name,last_name=last_name,email=email,role='2')
                        employee_user.password = make_password(password1)
                        employee_user.save()
                        employee=Employee.objects.create(
                            user=employee_user,
                            company=company,
                            picture=picture,  
                            date_of_birth=date_of_birth,
                            gender=gender,
                            address=address,
                            contact_number=contact_number,
                            position=position,
                            salary=salary,face_encoding=json.dumps(face_encoding)
                        )
                        employee.save()
                        messages.success(request, 'Employee member added successfully!')
                        return redirect('add_employee')
                    except Exception as e:
                        messages.error(request, f'An error occurred while saving the data: {e}')
                        return redirect('add_employee')
        else:
                messages.error(request, 'Passwords do not match!')
                return redirect('add_employee')
    return render(request,"company/add_employee.html")


@role_required(["1"])
def manage_employee(request):
    employees=Employee.objects.all()
    return render(request,"company/manage_employee.html",{'employees':employees})

@role_required(["1"])
def set_geofencing(request):
    return render(request,"company/set_geofencing.html")


@role_required(["1"])
def view_analytics(request):
    return render(request,"company/view_analytics.html")


@role_required(["1"])
def show_details_employee(request):
    return render(request,"company/show_details_employee.html")




