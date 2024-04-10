from django.shortcuts import render,redirect
from django.http import JsonResponse
import base64
import face_recognition
import numpy as np
import io
from PIL import Image




def face_enc(image_data):
    try:
        # Load image data
        #image = face_recognition.load_image_file(image_data)
        image_data = io.BytesIO(base64.b64decode(image_data))
        
        # Open image using PIL (Python Imaging Library)
        pil_image = Image.open(image_data)
        
        # Convert PIL image to numpy array
        image = np.array(pil_image)
        print(image)
        
        # Detect faces in the image
        face_locations = face_recognition.face_locations(image)
        print("++++++face Locations")
        
        if len(face_locations) > 0:
            # If faces are detected, encode them
            face_encodings = face_recognition.face_encodings(image, face_locations)
            print("++++++face encodings")
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
            print("++++++image from html done")
            # Get face encodings
            face_encodings = face_enc(image_data_base64)

            if face_encodings is not None:
                # Perform face recognition or any other operations as needed
                # For demonstration, let's just return the first face encoding
                first_face_encoding = face_encodings[0].tolist()
                print("++++++image face encodin g in html")
                return render(request, "employee/cam.html")
            else:
                return redirect(attendance_cam)
        except Exception as e:
            
            return redirect(attendance_cam)

    return render(request, "employee/cam.html")


def process_image(request):
    if request.method == 'POST' and 'image_data' in request.POST:
        print("hiiiiiiiiiiiii")
        # Get the image data from the POST request
        image_data_base64 = request.POST['image_data']
        image_data = base64.b64decode(image_data_base64.split(',')[1])  # Extract base64 image data
        print(image_data)
        # Perform face detection
        face_locations = face_recognition.face_locations(image_data)
        print(face_locations)
        # Perform face comparison with known faces (assumed stored in a database or directory)
        known_face_encodings = [...]  # Load known face encodings from a database or directory
        known_face_names = [...]      # Corresponding known face names
        
        # Encode the face in the image
        unknown_face_encodings = face_recognition.face_encodings(image_data, face_locations)
        
        # Compare the detected face with known faces
        for unknown_face_encoding in unknown_face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, unknown_face_encoding)
            name = "Unknown"
            
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                break  # Assuming we only need one match
        
        # Return the name as JSON response
        return JsonResponse({'name': name})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
