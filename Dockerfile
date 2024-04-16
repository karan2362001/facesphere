# Use an official Python runtime as a parent image
FROM python:3.9

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Install libgl1-mesa-glx package to resolve libGL.so.1 error
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Install CMake
RUN apt-get update && apt-get install -y cmake

# Set the working directory in the container
WORKDIR /facesphere

# Copy the current directory contents into the container at /code
COPY . /facesphere/

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run django project
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
