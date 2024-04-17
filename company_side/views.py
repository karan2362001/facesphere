from django.shortcuts import get_object_or_404, render,redirect
from accounts.models import CustomUser
from .models import Company,Branch,Company_geo_f_set,LeaveDeductionRate
from employees.models import TAX_CHOICES_INDIA, Attendance, Employee,Leave, Salary_employee, Tax
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
from django.db.models import Count, Q
from datetime import datetime, timedelta
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

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
    search_query = request.GET.get('search')
    if search_query:
        employees = employees.filter(
            Q(user__first_name__icontains=search_query) | 
            Q(user__last_name__icontains=search_query) 
            #Q(user__email__icontains=search_query)
        )
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


def employee_report(request):
    company = Company.objects.get(user=request.user)
    employees=Employee.objects.filter(company=company)
     # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        employees = employees.filter(
            Q(user__first_name__icontains=search_query) | 
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    return render(request,"company/employee_report.html",{'employees':employees})




@role_required(["1"])
def report_employee(request,employee_id):
    employee = Employee.objects.get(id=employee_id)
    print(employee)
    if request.method == 'GET':
        # Get selected month and year from the request
        selected_date = request.GET.get('selected_date')
        if selected_date:
            selected_year, selected_month = selected_date.split('-')
            selected_year = int(selected_year)
            selected_month = int(selected_month)
        else:
            # If no date is selected, default to current month and year
            selected_year = datetime.now().year
            selected_month = datetime.now().month

        # Calculate start and end dates for the selected month
        start_of_month = datetime(selected_year, selected_month, 1)
        end_of_month = start_of_month.replace(day=1, month=selected_month + 1) - timedelta(days=1)

        # Get leaves for the selected month
        leaves = Leave.objects.filter(
            employee=employee,
            start_date__range=[start_of_month, end_of_month]
        )

        # Calculate total days in the selected month
        total_days = (end_of_month - start_of_month).days + 1

        # Calculate present days based on attendances
        present_days_employee= Attendance.objects.filter(
            employee=employee,
            date__range=[start_of_month, end_of_month],
            status='1'
        )
        
        present_days_count= present_days_employee.count()

        # Calculate total leave days
        total_leave_days = sum((leave.end_date - leave.start_date).days + 1 for leave in leaves)

        # Calculate absent days based on total days, present days, and total leave days
        absent_days = total_days - present_days_count - total_leave_days

        return render(request, "company/report_employee_by_id.html", {
            'leaves': leaves,
            'employee': employee,
            'present_days': present_days_count,
            'absent_days': absent_days,
            'total_leave_days': total_leave_days,
            'selected_month': selected_month,
            'selected_year': selected_year,'present_days_employee':present_days_employee,
        })
        
        
        
        
        
        

def download_attendance_report1(request,selected_year, selected_month,employee_id):
    
    employee = Employee.objects.get(id=employee_id)

    # Calculate start and end dates for the selected month
    start_of_month = datetime(selected_year, selected_month, 1)
    end_of_month = start_of_month.replace(day=1, month=selected_month + 1) - timedelta(days=1)

    # Fetch attendance records for the employee for the selected month
    attendance_records = Attendance.objects.filter(
        employee=employee,
        date__range=[start_of_month, end_of_month]
    ).order_by('date')

    # Fetch leave records for the employee for the selected month
    leave_records = Leave.objects.filter(
        employee=employee,
        start_date__range=[start_of_month, end_of_month]
    ).order_by('start_date')

    # Perform analytics
    total_records = attendance_records.count()
    present_count = attendance_records.filter(status='1').count()
    absent_count = attendance_records.filter(status='0').count()
    leave_count = leave_records.count()

    # Create a PDF document
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="attendance_report_{selected_year}_{selected_month}.pdf"'

    # Create a PDF report using ReportLab
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Title
    title = f"Attendance Report for {selected_month}/{selected_year} - {employee.user.first_name} {employee.user.last_name}"
    styles = getSampleStyleSheet()
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))

    # Analytics
    analytics_data = [
        ['Total Records', 'Present Count', 'Absent Count', 'Leave Count'],
        [total_records, present_count, absent_count, leave_count]
    ]
    table_analytics = Table(analytics_data, colWidths='*')
    table_analytics.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                                         ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                         ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                         ('BOX', (0, 0), (-1, -1), 0.25, colors.black)]))
    elements.append(table_analytics)
    elements.append(Spacer(1, 12))

    # Attendance Table
    attendance_data = [['Date', 'Check In Time', 'Check Out Time']]
    for record in attendance_records:
        attendance_data.append([
            record.date.strftime("%Y-%m-%d"),
            record.check_in_time.strftime("%H:%M:%S") if record.check_in_time else '',
            record.check_out_time.strftime("%H:%M:%S") if record.check_out_time else ''
        ])
    table_attendance = Table(attendance_data, colWidths=[80, 80, 80])
    table_attendance.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                                           ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                           ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black)]))
    elements.append(Paragraph("Attendance Records", styles['Heading1']))  # Adjust style name here
    elements.append(table_attendance)
    elements.append(Spacer(1, 12))

    # Leave Table
    leave_data = [['Start Date', 'End Date', 'Reason']]
    for leave in leave_records:
        leave_data.append([
            leave.start_date.strftime("%Y-%m-%d"),
            leave.end_date.strftime("%Y-%m-%d"),
            leave.reason
        ])
    table_leave = Table(leave_data, colWidths=[80, 80, 200])
    table_leave.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                     ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                     ('BOX', (0, 0), (-1, -1), 0.25, colors.black)]))
    elements.append(Paragraph("Leave Records", styles['Heading1']))  # Adjust style name here
    elements.append(table_leave)

    doc.build(elements)
    return response


def salary_management(request):
    company = Company.objects.get(user=request.user)
    employees=Employee.objects.filter(company=company)
    
    search_query = request.GET.get('search')
    if search_query:
        employees = employees.filter(
            Q(user__first_name__icontains=search_query) | 
            Q(user__last_name__icontains=search_query) 
            #Q(user__email__icontains=search_query)
        )
   
    return render(request,"company/salary_management.html",{'employees':employees})






# @role_required(["1"])
# def salary_employee_form(request, employee_id):
#     # Retrieve the employee object to edit
#     employee = get_object_or_404(Employee, id=employee_id)
#     user=CustomUser.objects.get(username=employee.user.username)

#     if request.method == 'POST':
       
#         housing_allowance = request.POST.get('housing_allowance')
#         transport_allowance = request.POST.get('transport_allowance')
#         medical_allowance = request.POST.get('medical_allowance')
#         bonus = request.POST.get('bonus')

#         # Save employee details into the database
#         salary_employee = Salary_employee.objects.create(
#             employee=employee,
#             housing_allowance=housing_allowance,
#             transport_allowance=transport_allowance,
#             medical_allowance=medical_allowance,
#             bonus=bonus,
#         )

#         # Parse and save tax data
#         taxes = request.POST.getlist('taxes[]')
#         for tax in taxes:
#             tax_type, tax_amount = tax['type'], tax['amount']
#             Tax.objects.create(
#                 employee=employee,
#                 tax_type=tax_type,
#                 amount=tax_amount
#             )

#     return render(request, 'company/salary_employee_form.html', {'employee': employee,"tax_choices":TAX_CHOICES_INDIA})


def leave_deduction_rate(request):
    company = get_object_or_404(Company, user=request.user)  # Assuming company data is represented by User model
     # Fetch existing leave deduction rates for the company, if any
    leave_deduction_rate = LeaveDeductionRate.objects.filter(company=company).first()
    
    # Pre-fill form data if leave deduction rates exist
    leave_type_data = {}
    if leave_deduction_rate:
        leave_type_data = {
            'sick_leave': leave_deduction_rate.sick_leave,
            'vacation_leave': leave_deduction_rate.vacation_leave,
            'casual_leave': leave_deduction_rate.casual_leave,
            'earned_leave': leave_deduction_rate.earned_leave,
            'maternity_leave': leave_deduction_rate.maternity_leave,
            'paternity_leave': leave_deduction_rate.paternity_leave,
            'bereavement_leave': leave_deduction_rate.bereavement_leave,
            'compensatory_off': leave_deduction_rate.compensatory_off,
        }
    if request.method == 'POST':
        try:
            # Extract leave deduction rates from the request
            sick_leave = request.POST.get('sick_leave')
            vacation_leave = request.POST.get('vacation_leave')
            casual_leave = request.POST.get('casual_leave')
            earned_leave = request.POST.get('earned_leave')
            maternity_leave = request.POST.get('maternity_leave')
            paternity_leave = request.POST.get('paternity_leave')
            bereavement_leave = request.POST.get('bereavement_leave')
            compensatory_off = request.POST.get('compensatory_off')
          
            
            # Check if leave deduction rates already exist for this company
            leave_deduction_rate, created = LeaveDeductionRate.objects.get_or_create(company=company)
            
            if not created:
                # Update leave deduction rates if already exist
                leave_deduction_rate.sick_leave = sick_leave
                leave_deduction_rate.vacation_leave = vacation_leave
                leave_deduction_rate.casual_leave = casual_leave
                leave_deduction_rate.earned_leave = earned_leave
                leave_deduction_rate.maternity_leave = maternity_leave
                leave_deduction_rate.paternity_leave = paternity_leave
                leave_deduction_rate.bereavement_leave = bereavement_leave
                leave_deduction_rate.compensatory_off = compensatory_off
           
                
                leave_deduction_rate.save()
            else:
                # Set leave deduction rates if newly created
                leave_deduction_rate.sick_leave = sick_leave
                leave_deduction_rate.vacation_leave = vacation_leave
                leave_deduction_rate.casual_leave = casual_leave
                leave_deduction_rate.earned_leave = earned_leave
                leave_deduction_rate.maternity_leave = maternity_leave
                leave_deduction_rate.paternity_leave = paternity_leave
                leave_deduction_rate.bereavement_leave = bereavement_leave
                leave_deduction_rate.compensatory_off = compensatory_off
               
                
                leave_deduction_rate.save()
            
            messages.success(request, "Leave deduction rates updated successfully.")
            return redirect('salary_management')  # Replace 'salary_management' with your actual URL name
        except Exception as e:
            messages.error(request, "Error while updating leave deduction rates.")
            return redirect('leave_deduction_rate')  # Redirect back to the form
        
    return render(request, 'company/leave_deduction_rate.html',{'leave_type_data':leave_type_data})


    
    
def salary_employee_form(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
     # Fetch existing salary details for the employee, if any
    salary_employee = Salary_employee.objects.filter(employee=employee).first()
    
    # Fetch existing tax details for the employee, if any
    tax_types = ['income_tax', 'pf', 'esi', 'professional_tax', 'tds']
    existing_taxes = Tax.objects.filter(employee=employee, tax_type__in=tax_types)
    existing_tax_data = {tax.tax_type: tax.amount for tax in existing_taxes}
    
    if request.method == 'POST':
        # Extract salary details from the request
        try:
            housing_allowance = request.POST.get('housing_allowance')
            transport_allowance = request.POST.get('transport_allowance')
            medical_allowance = request.POST.get('medical_allowance')
            bonus = request.POST.get('bonus')
            
            # Extract tax details from the request
            income_tax = request.POST.get('income_tax')
            pf = request.POST.get('pf')
            esi = request.POST.get('esi')
            professional_tax = request.POST.get('professional_tax')
            tds = request.POST.get('tds')
            
            # Check if salary details already exist for this employee
            salary_employee, created = Salary_employee.objects.get_or_create(
                employee=employee,
                defaults={
                    'housing_allowance': housing_allowance,
                    'transport_allowance': transport_allowance,
                    'medical_allowance': medical_allowance,
                    'bonus': bonus
                }
            )
            
            # Update salary details if already exist
            if not created:
                salary_employee.housing_allowance = housing_allowance
                salary_employee.transport_allowance = transport_allowance
                salary_employee.medical_allowance = medical_allowance
                salary_employee.bonus = bonus
                salary_employee.save()
            
                # Update or create tax details for this employee
            tax_types = ['income_tax', 'pf', 'esi', 'professional_tax', 'tds']
            tax_amounts = [income_tax, pf, esi, professional_tax, tds]
            
            for tax_type, tax_amount in zip(tax_types, tax_amounts):
                tax, created = Tax.objects.get_or_create(
                    employee=employee,
                    tax_type=tax_type,
                    defaults={'amount': tax_amount}
                )
                if not created:
                    tax.amount = tax_amount
                    tax.save()
                    print(f"{tax_type} updated.")
                else:
                    print(f"New {tax_type} created.")
            
            messages.success(request, "Salary details and taxes updated successfully.")
            return redirect('salary_management')  # Replace 'salary_management' with your actual URL name
        except Exception as e:
            messages.error(request,"Error while handling data...")
            return redirect(salary_employee_form,employee_id)
         
    return render(request, 'company/salary_employee_form.html', {'employee': employee,'tax_choices': TAX_CHOICES_INDIA,'salary_employee': salary_employee, 'existing_tax_data': existing_tax_data})


# def calculate_total_earnings(employee, salary_employee):
#     # Calculate total earnings including salary and allowances
#     total_earnings = employee.salary + salary_employee.housing_allowance + \
#                      salary_employee.transport_allowance + \
#                      salary_employee.medical_allowance + salary_employee.bonus
#     return total_earnings



# def calculate_leave_deduction(salary, leave_type, start_date, end_date, company_instance):
#     try:
#         # Fetch the deduction rates for the company from the database
#         company_deduction_rates = LeaveDeductionRate.objects.get(company=company_instance).deduction_rates
        
#         # Get the deduction rate for the specific leave type
#         deduction_rate_info = company_deduction_rates.get(leave_type)
#         deduction_rate = deduction_rate_info['rate']
        
#     except LeaveDeductionRate.DoesNotExist:
#         raise ValueError("Deduction rates not found for the company")

#     # Calculate the number of days for the leave duration
#     leave_duration = (end_date - start_date).days + 1  # Add 1 to include both start and end dates

#     # Fixed deduction period of 30 days
#     deduction_period = 30

#     # Calculate the leave deduction amount
#     leave_deduction = (deduction_rate * salary / deduction_period) * leave_duration

#     return leave_deduction
