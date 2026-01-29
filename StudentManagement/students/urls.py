from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/edit/<int:id>/', views.edit_student, name='edit_student'),
    path('students/delete/<int:id>/', views.delete_student, name='delete_student'),
# teachers
    path('', views.dashboard, name='dashboard'),

    # Teachers
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/add/', views.add_teacher, name='add_teacher'),
    path('teachers/edit/<int:id>/', views.edit_teacher, name='edit_teacher'),
    path('teachers/delete/<int:id>/', views.delete_teacher, name='delete_teacher'),
#attebdance
path('attendance/mark/', views.mark_attendance, name='mark_attendance'),
path('attendance/', views.attendance_list, name='attendance_list'),
path('my-students/', views.my_students, name='my_students'),

    
# AUTH
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

# dashboard
    path('', views.dashboard, name='dashboard'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),

]
