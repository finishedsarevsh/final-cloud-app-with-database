import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from onlinecourse.models import Course, Lesson, Instructor, Learner, Question, Choice, Enrollment

# 1. Create superuser
admin_user, created = User.objects.get_or_create(username='admin')
admin_user.set_password('admin12345')
admin_user.is_superuser = True
admin_user.is_staff = True
admin_user.first_name = 'Admin'
admin_user.last_name = 'User'
admin_user.email = 'admin@example.com'
admin_user.save()
print(f"Superuser 'admin' ready (created={created})")

# 2. Create test learner user
student_user, created = User.objects.get_or_create(username='student1')
student_user.set_password('student12345')
student_user.first_name = 'Student'
student_user.last_name = 'One'
student_user.email = 'student1@example.com'
student_user.save()
print(f"Test user 'student1' ready (created={created})")

learner, created = Learner.objects.get_or_create(
    user=student_user,
    defaults={'occupation': Learner.STUDENT, 'social_link': 'https://github.com/student1'}
)

instructor_user, _ = User.objects.get_or_create(
    username='instructor1',
    defaults={'first_name': 'Lead', 'last_name': 'Instructor', 'email': 'instructor@example.com'}
)
instructor, _ = Instructor.objects.get_or_create(
    user=instructor_user,
    defaults={'full_time': True, 'total_learners': 50}
)

# 3. Create Course
course, created = Course.objects.get_or_create(
    name='Cloud Application Development',
    defaults={
        'description': 'Master cloud app development with Django, databases, and continuous integration.',
        'pub_date': date.today(),
        'total_enrollment': 1
    }
)
course.instructors.add(instructor)
print(f"Course '{course.name}' ready (id={course.id})")

# 4. Create Lessons
lessons_data = [
    ("Introduction to Cloud Applications", "Overview of cloud architectures, REST APIs, microservices, and full-stack development."),
    ("Django Models and Databases", "Deep dive into Django ORM, database schema migrations, and relational modeling."),
    ("Assessment and Grading Systems", "Implementing user assessment forms, automated grading logic, and result dashboards.")
]

for idx, (title, content) in enumerate(lessons_data):
    lesson, _ = Lesson.objects.get_or_create(
        course=course,
        order=idx,
        defaults={'title': title, 'content': content}
    )

# 5. Create 3 Questions with 3-4 Choices each
# Question 1 (Single correct answer: models.py)
q1, _ = Question.objects.get_or_create(
    course=course,
    question_text="Which file is used to define Django database models?",
    defaults={'grade': 30}
)
Choice.objects.get_or_create(question=q1, choice_text="models.py", defaults={'is_correct': True})
Choice.objects.get_or_create(question=q1, choice_text="views.py", defaults={'is_correct': False})
Choice.objects.get_or_create(question=q1, choice_text="urls.py", defaults={'is_correct': False})
Choice.objects.get_or_create(question=q1, choice_text="admin.py", defaults={'is_correct': False})

# Question 2 (Single correct answer: python manage.py migrate)
q2, _ = Question.objects.get_or_create(
    course=course,
    question_text="Which command applies migrations to the database in Django?",
    defaults={'grade': 30}
)
Choice.objects.get_or_create(question=q2, choice_text="python manage.py makemigrations", defaults={'is_correct': False})
Choice.objects.get_or_create(question=q2, choice_text="python manage.py migrate", defaults={'is_correct': True})
Choice.objects.get_or_create(question=q2, choice_text="python manage.py runserver", defaults={'is_correct': False})
Choice.objects.get_or_create(question=q2, choice_text="python manage.py test", defaults={'is_correct': False})

# Question 3 (Multiple correct answers: POST and GET)
q3, _ = Question.objects.get_or_create(
    course=course,
    question_text="Which of the following HTTP methods can HTML forms natively use to submit data?",
    defaults={'grade': 40}
)
Choice.objects.get_or_create(question=q3, choice_text="POST", defaults={'is_correct': True})
Choice.objects.get_or_create(question=q3, choice_text="GET", defaults={'is_correct': True})
Choice.objects.get_or_create(question=q3, choice_text="DELETE", defaults={'is_correct': False})
Choice.objects.get_or_create(question=q3, choice_text="CONNECT", defaults={'is_correct': False})

# 6. Enroll test learner in course
enrollment, created = Enrollment.objects.get_or_create(
    user=student_user,
    course=course,
    defaults={'mode': Enrollment.HONOR}
)
print(f"Enrollment for student1 in {course.name} ready (created={created})")
print("Data setup completed successfully!")
