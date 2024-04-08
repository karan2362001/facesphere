from django.shortcuts import render,HttpResponseRedirect
from django.http import JsonResponse
import base64
import face_recognition

def attendance_cam(request):
    if request.method == 'POST' and 'image_data' in request.POST:
        # Get the image data from the POST request
        image_data_base64 = request.POST['image_data']
        image_data = base64.b64decode(image_data_base64.split(',')[1])  # Extract base64 image data
        print(image_data)
        # Perform face detection
        # For demonstration purposes, let's assume the name is "Karan"
        name = "Karan"
    
        # Pass the name to the HTML template
        return render(request, "employee/cam.html", {"name": name})

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
