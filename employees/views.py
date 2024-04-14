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
    leaves=Leave.objects.filter(employee=employee)
    return render(request,"employee/employee_attendance_report.html",{'leaves':leaves,'employee':employee})