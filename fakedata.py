import os
import random
from faker import Faker
from django.core.wsgi import get_wsgi_application
import pytz
from datetime import datetime, time, timedelta

# Define the timezone
timezone = pytz.timezone('Asia/Kolkata')  # Adjust the timezone as per your requirement

# Use the timezone in Faker
fake = Faker('en_IN')

# Set the default timezone for Faker
fake.timezone = timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facesphere.settings')
application = get_wsgi_application()

from accounts.models import CustomUser
from company_side.models import Company, Branch
from employees.models import Employee, Attendance, Leave

def create_fake_data(num_entries):
    # Get existing companies
    companies = Company.objects.all()

    # Create employees
    for _ in range(num_entries):
        company = random.choice(companies)
        custom_user = CustomUser.objects.create_user(
            username=fake.unique.user_name(),  # Ensure unique usernames
            email=fake.email(),
            password='12345',
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            role='2'  # '1' for Company, '2' for Employee
        )
        employee = Employee.objects.create(
            user=custom_user,
            company=company,
            date_of_birth=fake.date_time_between(start_date='-60y', end_date='-18y', tzinfo=timezone).date(),
            gender=random.choice(['Male', 'Female', 'Other']),
            address=fake.address(),
            contact_number=fake.phone_number(),
            position=fake.job(),
            salary=random.randint(20000, 100000),
        )
        
        # Create attendance records for two months
        attendance_dates = set()  # To keep track of already created attendance dates for this employee
        for _ in range(60):  # 60 days for two months
            while True:
                attendance_date = fake.date_time_between(start_date='-2M', end_date='now', tzinfo=timezone).date()
                if attendance_date not in attendance_dates:
                    # Check if attendance record already exists for this date
                    if not Attendance.objects.filter(employee=employee, date=attendance_date).exists():
                        attendance_dates.add(attendance_date)
                        break
            
            if attendance_date in attendance_dates:
                start_time = fake.time_object()
                start_datetime = datetime.combine(attendance_date, start_time)
                end_datetime = start_datetime + timedelta(hours=random.randint(1, 8))
                
                if start_datetime < end_datetime:
                    Attendance.objects.create(
                        employee=employee,
                        date=attendance_date,
                        check_in_time=start_datetime,  # Pass complete datetime object
                        check_out_time=end_datetime,   # Pass complete datetime object
                        status=random.choice(['1', '0']),  # '1' for Present, '0' for Absent
                    )

        # Create leave records
        for _ in range(random.randint(1, 5)):  # Assuming 1-5 leave requests
            Leave.objects.create(
                employee=employee,
                start_date=fake.date_time_between(start_date='-3M', end_date='now', tzinfo=timezone).date(),
                end_date=fake.date_time_between(start_date='-3M', end_date='now', tzinfo=timezone).date(),
                reason=fake.text(max_nb_chars=200),
                status=random.choice(['3', '1', '0']),  # '3' for Pending, '1' for Approved, '0' for Rejected
            )

if __name__ == '__main__':
    num_entries = 20  # Change the number as per your requirement
    create_fake_data(num_entries)
