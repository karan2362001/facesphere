import json
from django.shortcuts import render,redirect
from django.http import JsonResponse
import base64
import face_recognition
import numpy as np
import io
from PIL import Image

from employees.models import Employee




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
            # image_data = base64.b64decode(image_data_base64.split(',')[1])
            # print(image_data)

            # Get face encodings
            face_encodings = face_enc(image_data_base64)
            

            # if face_encodings is not None:
            #     # Perform face recognition or any other operations as needed
            #     # For demonstration, let's just return the first face encoding
            #     first_face_encoding = face_encodings[0].tolist()
            if face_encodings is not None:
                # Retrieve the first face encoding (assuming only one face is present in the image)
                recent_face_encoding = face_encodings[0]
                print("hello")

                # Get the name of the person corresponding to the face encoding
                face_name = get_face_name(recent_face_encoding)
                print(face_name)
                
                return render(request, "employee/facecam.html")
            else:
                return redirect(attendance_cam)
        except Exception as e:
            
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
            print("1212121")
            # Return the corresponding name or identifier associated with the face encoding
            

            return Employee.objects.get(face_encoding=json.dumps(db_encoding)).user.username
    return None  # If no match is found

