from django.shortcuts import get_object_or_404, render,redirect
from accounts.models import CustomUser
from .models import Company,Branch,Company_geo_f_set
from employees.models import Employee,Leave
from accounts.decorators import role_required
from django.contrib.auth.hashers import make_password
from django.contrib import messages
import face_recognition
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import json
from django.http import HttpResponseRedirect
from django.urls import reverse
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
                        #employee_user.set_password('password1')  
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
                        return redirect('manage_employee')
                    except Exception as e:
                        messages.error(request, f'An error occurred while saving the data: {e}')
                        return redirect('add_employee')
        else:
                messages.error(request, 'Passwords do not match!')
                return redirect('add_employee')
    return render(request,"company/add_employee.html")


@role_required(["1"])
def manage_employee(request):
    company = Company.objects.get(user=request.user)
    employees=Employee.objects.filter(company=company)
    return render(request,"company/manage_employee.html",{'employees':employees})

@role_required(["1"])
def set_geofencing(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            # Extract latitude, longitude, and range from JSON data
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            range_value = data.get('range')
            print(latitude, longitude, range_value)  # Just for debugging

            # Here you can add your logic to save geofencing data to the database
            company = Company.objects.get(user=request.user)
            try:
                company_geo_f_set = Company_geo_f_set.objects.get(company=company)
                # If the object exists, update its fields
                company_geo_f_set.latitude = latitude
                company_geo_f_set.longitude = longitude
                company_geo_f_set.location_range = range_value
                company_geo_f_set.save()
                
                print("Company_geo_f_set object updated successfully.")
            except Company_geo_f_set.DoesNotExist:
                # If the object doesn't exist, create a new one
                company_geo_f_set = Company_geo_f_set.objects.create(
                    company=company,
                    latitude=latitude,
                    longitude=longitude,
                    location_range=range_value
                )
                print("Company_geo_f_set object created successfully.")
            except Exception as e:
                print(f"An error occurred: {e}")
                messages.error(request, 'An error occurred while processing your request.')
                return redirect(set_geofencing)
            
            messages.success(request, 'Geofencing data saved successfully.')
            # Redirect to a success page using the PRG pattern
            return redirect(set_geofencing)
        except json.JSONDecodeError:
            messages.error(request, 'Invalid JSON data.')
            
        except Exception as e:
            messages.error(request, 'An error occurred while processing your request.')
            return redirect(set_geofencing)

    # Always render the form template for GET requests
    return render(request, "company/set_geofencing.html")


@role_required(["1"])
def view_analytics(request):
    return render(request,"company/view_analytics.html")


@role_required(["1"])  # Custom decorator to restrict access based on role
def show_details_employee(request, employee_id):
    try:
        # Retrieve the company associated with the current user
        company = Company.objects.get(user=request.user)
        
        # Retrieve the employee with the specified ID belonging to the same company
        employee = Employee.objects.get(company=company, id=employee_id)
        
        # Render the template with the employee details as context
        return render(request, "company/show_details_employee.html", {'employee': employee})
    
    except Company.DoesNotExist:
        # If the company doesn't exist, add a message and redirect to manage_employee
        messages.error(request, "Company not found.")
        return redirect('manage_employee')
    
    except Employee.DoesNotExist:
        # If the employee doesn't exist or doesn't belong to the same company, add a message and redirect to manage_employee
        messages.error(request, "Employee not found.")
        return redirect('manage_employee')




# def edit_details_employee(request, employee_id):
#     try:
#         # Retrieve the company associated with the current user
#         company = Company.objects.get(user=request.user)
        
#         # Retrieve the employee with the specified ID belonging to the same company
#         employee = Employee.objects.get(company=company, id=employee_id)
        
#         # Render the template with the employee details as context
#         return render(request, "company/edit_details_employee.html", {'employee': employee})
    
#     except Company.DoesNotExist:
#         # If the company doesn't exist, add a message and redirect to manage_employee
#         messages.error(request, "Company not found.")
#         return redirect('manage_employee')
    
#     except Employee.DoesNotExist:
#         # If the employee doesn't exist or doesn't belong to the same company, add a message and redirect to manage_employee
#         messages.error(request, "Employee not found.")
#         return redirect('manage_employee')
    
    
    
@role_required(["1"])
def edit_details_employee(request, employee_id):
    # Retrieve the employee object to edit
    employee = get_object_or_404(Employee, id=employee_id)
    user=CustomUser.objects.get(username=employee.user.username)

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

        if password1 == password2:
            try:
                # Update employee data
                user.first_name = first_name
                user.last_name = last_name
                user.username = username
                user.email = email
                if password1:
                    #user.password = password1
                   # user.set_password(password1)
                    user.set_password(password1) 
                user.save(update_fields=['first_name','last_name','username','email','password'])
                if picture:
                    employee.picture = picture
                    face_encoding = face_enc(picture)
                    if face_encoding:
                        employee.face_encoding = json.dumps(face_encoding)
                    else:
                        messages.error(request, 'Could not generate face encoding from the provided image.')
                        return redirect('edit_details_employee', employee_id=employee_id)
                    
                employee.date_of_birth = date_of_birth
                employee.gender = gender
                employee.address = address
                employee.contact_number = contact_number
                employee.position = position
                employee.salary = salary
                
                # # Update face encoding if picture is provided
                # if picture:
                #     face_encoding = face_enc(picture)
                #     if face_encoding:
                #         employee.face_encoding = json.dumps(face_encoding)
                #     else:
                #         messages.error(request, 'Could not generate face encoding from the provided image.')wha
                #         return redirect('edit_details_employee', employee_id=employee_id)

                # employee.save()
                employee.save(update_fields=['picture', 'date_of_birth', 'gender', 'address', 
                    'contact_number', 'position', 'salary', 'face_encoding'])
                
                messages.success(request, 'Employee member updated successfully!')
                return redirect('manage_employee')
            except Exception as e:
                messages.error(request, f'An error occurred while saving the data: {e}')
        else:
            messages.error(request, 'Passwords do not match!')

    return render(request, 'company/edit_details_employee.html', {'employee': employee})





@role_required(["1"])
def delete_details_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
        # Delete the employee
    employee.delete()
    messages.success(request, 'Employee deleted successfully!')
    return redirect('manage_employee')  # Redirect to the appropriate page after deletion






@role_required(["1"])
def manage_employee_leave(request):
    company = Company.objects.get(user=request.user)
    employees=Employee.objects.filter(company=company)
    leaves = Leave.objects.filter(employee__company=company, status='3').order_by('-application_date')
    print(leaves)
    return render(request,"company/manage_employee_leave.html",{'leaves':leaves})


@role_required(["1"])
def manage_employee_leave_reject(request, leave_id):
    try:
        leave = get_object_or_404(Leave, id=leave_id)
        leave.status = "0"
        leave.save()
        messages.success(request, 'Employee Leave Rejected...')
    except Leave.DoesNotExist:
        messages.error(request, 'Leave request does not exist.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        # Log the error using the logging module

    return redirect('manage_employee_leave')

@role_required(["1"])
def manage_employee_leave_approve(request, leave_id):
    try:
        leave = get_object_or_404(Leave, id=leave_id)
        leave.status = "1"
        leave.save()
        messages.success(request, 'Employee Leave Accepted...')
    except Leave.DoesNotExist:
        messages.error(request, 'Leave request does not exist.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        # Log the error using the logging module

    return redirect('manage_employee_leave')