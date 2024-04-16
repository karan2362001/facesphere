import json
from django.shortcuts import render,redirect
from django.http import HttpResponseBadRequest, JsonResponse
import base64
import face_recognition
import numpy as np
import io
from PIL import Image
from accounts.decorators import role_required
from company_side.models import Company,Company_geo_f_set
from employees.models import Employee,Attendance,Leave
from accounts.models import CustomUser
from django.utils import timezone
from django.contrib import messages
from math import radians, sin, cos, sqrt, atan2
from django.db.models import Count, Q
from datetime import datetime, timedelta
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

def face_enc(image_data):
    try:
        # Load image data
        #image = face_recognition.load_image_file(image_data)
        image_data = io.BytesIO(base64.b64decode(image_data.split(',')[1]))
        
        # Open image using PIL (Python Imaging Library)
        pil_image = Image.open(image_data)
        
        # Convert PIL image to numpy array
        image = np.array(pil_image)

        
        # Detect faces in the image
        face_locations = face_recognition.face_locations(image)

        
        if len(face_locations) > 0:
            # If faces are detected, encode them
            face_encodings = face_recognition.face_encodings(image, face_locations)
      
            return face_encodings
        else:
            # If no faces are detected, return None
            return None
    except Exception as e:
        # If an error occurs during face encoding, print error and return None
        print(f"Error generating face encoding: {e}")
        return None
    
    
def attendance_cam(request):
    if request.method == 'POST' and 'image_data' in request.POST:
        try:
            image_data_base64 = request.POST['image_data']
            
            latitude = request.POST['latitude']
            longitude = request.POST['longitude']
            # geofence_center = (23.045351984509566, 72.67995464145855) 
            #employee_location = (float(lat),float(lon))
            # result = is_inside_geofence(employee_location, geofence_center, radius=100) 
            print(latitude,longitude)
            face_encodings = face_enc(image_data_base64)
            if face_encodings is not None:
                
                recent_face_encoding = face_encodings[0]
                
                face_name = get_face_name(recent_face_encoding)
                
                user=CustomUser.objects.get(username=face_name)
                
                employee=Employee.objects.get(user=user)
                print(employee)
                company_details = employee.company.id
                print(company_details)
                company_details_set = Company.objects.get(id=company_details)
                print(company_details_set)
                company_geo_f_set = Company_geo_f_set.objects.get(company=company_details_set)
                print(company_geo_f_set)
                geofence_center = (company_geo_f_set.latitude,company_geo_f_set.longitude)
                employee_location = (float(latitude),float(longitude))
                result = is_inside_geofence(employee_location=employee_location, geofence_center=geofence_center, radius=company_geo_f_set.location_range) 
                #print(Company_geo_f_set.latitude,Company_geo_f_set.longitude,Company_geo_f_set.location_range)
                print(result)
                
                today = timezone.now().date()
                print("++++++")
                if result:
                    attendance1=Attendance.objects.filter(employee=employee, date=today, status='1').exists()
                    if attendance1 :
                        print("#####")
                        attendance=Attendance.objects.get(employee=employee, date=today, status='1')
                        if attendance and attendance.check_in_time and attendance.check_out_time:
                            print("-------")
                            messages.error(request,"Already filled attendance for this day. 😒")
                            return render(request, "employee/facecam.html", {'attendance': attendance})
                        else:
                            if attendance and not attendance.check_out_time:
                                print("chekkkkk")
                                
                                attendance.check_out_time=timezone.now()
                                
                                attendance.save()
                                messages.success(request,"Check Out Time Added successfully 👍")
                                return render(request, "employee/facecam.html", {'attendance': attendance})
                            else:
                                print("create   ---")
                                attendance=Attendance.objects.create(employee=employee,status='1')
                                messages.success(request,"Check In Time Added successfully 👍")
                                return render(request, "employee/facecam.html", {'attendance': attendance})
                    else:
                        print("@@@@@")
                        attendance=Attendance.objects.create(employee=employee,status='1')
                        messages.success(request,"Check In Time Added successfully 👍")
                        return render(request, "employee/facecam.html", {'attendance': attendance})
                else:
                    messages.error(request,"You are Not in Valid Location 🗺️📌")
                    return redirect(attendance_cam)
            else:
                return redirect(attendance_cam)
        except Exception as e:
            print("!!!!!!")
            messages.error(request,f"Error while handling request {e}")
            return redirect(attendance_cam)

    return render(request, "employee/facecam.html")

def get_face_name(face_encoding):
    # Fetch all face encodings from the database
    all_face_encodings = [json.loads(employee.face_encoding) for employee in Employee.objects.all()]
    print(all_face_encodings)

    # Compare the face encoding with all encodings from the database
    for db_encoding in all_face_encodings:
        # Calculate the similarity score
        print(type(db_encoding))
        match = face_recognition.compare_faces([db_encoding], face_encoding)
        print("++++++++++++++++")
        print(match[0])
        if match[0]:  # If there is a match
            return Employee.objects.get(face_encoding=json.dumps(db_encoding)).user.username
    return None  # If no match is found


def haversine_distance(coord1, coord2):
      
        R = 6371000  # meters

        lat1, lon1 = radians(coord1[0]), radians(coord1[1])
        lat2, lon2 = radians(coord2[0]), radians(coord2[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1


        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance
    
def is_inside_geofence(employee_location, geofence_center, radius):
        
        distance = haversine_distance(employee_location, geofence_center)
        return distance <= radius
    
    
    
    
    
    
    


@role_required(["2"])  # Assuming role_required is a custom decorator to check user roles
def apply_leave(request):
    employee = Employee.objects.get(user=request.user)
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        print(start_date,end_date,reason)
        
        # Basic validation
        if not start_date or not end_date or not reason:
            messages.error(request,"Please fill all the fields.")
            return redirect('apply_leave')
        
        # Convert dates to datetime objects for comparison
        try:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request,"Error occurred getting date from input field.")
            return redirect('apply_leave')
        
        # Check if start date is before end date
        if start_date >= end_date:
            messages.error(request,"Start Date must be earlier than End Date.")
            return redirect('apply_leave')
        
     
        # Save leave
        Leave.objects.create(employee=employee, start_date=start_date, end_date=end_date, reason=reason)
        messages.success(request, "Leave applied successfully!")
        return redirect('leave_management')
    
    return render(request, "employee/apply_leave.html", {'employee': employee})



@role_required(["2"])
def leave_management(request):
    employee = Employee.objects.get(user=request.user)
    leaves=Leave.objects.filter(employee=employee)
    return render(request,"employee/leave_management.html",{'leaves':leaves,'employee':employee})



@role_required(["2"])
def employee_attendance_report(request):
    employee = Employee.objects.get(user=request.user)
    
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

        return render(request, "employee/employee_attendance_report.html", {
            'leaves': leaves,
            'employee': employee,
            'present_days': present_days_count,
            'absent_days': absent_days,
            'total_leave_days': total_leave_days,
            'selected_month': selected_month,
            'selected_year': selected_year,'present_days_employee':present_days_employee,
        })
        
        
        
        

def download_attendance_report(request, selected_year, selected_month):
    # Get the currently logged-in employee
    employee = Employee.objects.get(user=request.user)

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
