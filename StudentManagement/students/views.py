from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Student, Teacher, Attendance
from .forms import StudentForm, TeacherForm, AttendanceForm, RegisterForm


from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

#---------------- DASHBOARD ----------------

@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'today_attendance': Attendance.objects.filter(
            date=timezone.now().date()
        ).count()
    })

#---------------- AUTH ----------------


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()

        # 1. Create Student profile automatically
        Student.objects.create(
            name=user.username,
            email=user.email,
            age=18,
            course="Not Assigned"
        )

        # 2. Assign student permissions automatically
        content_type = ContentType.objects.get_for_model(Student)
        view_student = Permission.objects.get(
            codename='view_student',
            content_type=content_type
        )

        attendance_ct = ContentType.objects.get(app_label='students', model='attendance')
        view_attendance = Permission.objects.get(
            codename='view_attendance',
            content_type=attendance_ct
        )

        user.user_permissions.add(view_student, view_attendance)

        # 3. Auto login
        login(request, user)

        # 4. Redirect to student dashboard
        return redirect('student_dashboard')

    return render(request, 'register.html', {'form': form})


#---------------- STUDENTS ----------------

@login_required
def student_list(request):
    query = request.GET.get('q', '').strip()
    students = Student.objects.all().order_by('-id')

    if query:
        students = students.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(course__icontains=query)
        )

    paginator = Paginator(students, 5)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'students/student_list.html', {
        'page_obj': page_obj,
        'query': query
    })


@login_required
def add_student(request):
    form = StudentForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('student_list')
    return render(request, 'students/add_student.html', {'form': form})


@login_required
def edit_student(request, id):
    student = get_object_or_404(Student, id=id)
    form = StudentForm(request.POST or None, instance=student)
    if form.is_valid():
        form.save()
        return redirect('student_list')
    return render(request, 'students/edit_student.html', {'form': form})


@login_required
def delete_student(request, id):
    get_object_or_404(Student, id=id).delete()
    return redirect('student_list')

#---------------- TEACHERS ----------------

@login_required
@permission_required('students.view_teacher', raise_exception=True)
def teacher_list(request):
    return render(request, 'teachers/teacher_list.html', {
        'teachers': Teacher.objects.all()
    })


@login_required
@permission_required('students.add_teacher', raise_exception=True)
def add_teacher(request):
    form = TeacherForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('teacher_list')
    return render(request, 'teachers/add_teacher.html', {'form': form})

@login_required
@permission_required('students.change_teacher', raise_exception=True)
def edit_teacher(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    form = TeacherForm(request.POST or None, instance=teacher)
    if form.is_valid():
        form.save()
        return redirect('teacher_list')
    return render(request, 'teachers/edit_teacher.html', {'form': form})


@login_required
@permission_required('students.delete_teacher', raise_exception=True)
def delete_teacher(request, id):
    get_object_or_404(Teacher, id=id).delete()
    return redirect('teacher_list')


@login_required
def my_students(request):
    teacher = Teacher.objects.filter(email=request.user.email).first()
    return render(request, 'teachers/my_students.html', {
        'students': Student.objects.filter(teacher=teacher)
    })

#---------------- ATTENDANCE ----------------

@login_required
def mark_attendance(request):
    form = AttendanceForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('attendance_list')
    return render(request, 'attendance/mark_attendance.html', {'form': form})

@login_required
def attendance_list(request):
    records = Attendance.objects.select_related('student').order_by('-date')
    return render(request, 'attendance/attendance_list.html', {
        'records': records
    })


#----------students dashboard----------

@login_required
def dashboard(request):

    # Student
    if request.user.has_perm('students.view_attendance') and not request.user.has_perm('students.add_attendance'):
        return redirect('student_dashboard')

    # Teacher
    if request.user.has_perm('students.add_attendance'):
        return redirect('teacher_dashboard')

    # Admin
    return render(request, 'dashboard.html', {
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'today_attendance': Attendance.objects.filter(
            date=timezone.now().date()
        ).count()
    })


#--------------teacher dashboard----------------
@login_required
@permission_required('students.add_attendance', raise_exception=True)
def teacher_dashboard(request):
    # find teacher linked to logged in user (by email)
    teacher = Teacher.objects.filter(user=request.user).first()

    if not teacher:
        return render(request, 'teachers/teacher_dashboard.html', {
            'error': 'Teacher profile not found'
        })

    students = Student.objects.filter(teacher=teacher)

    attendance = Attendance.objects.filter(student__in=students)

    total_classes = attendance.count()
    present = attendance.filter(status='P').count()
    today = attendance.filter(date=timezone.now().date()).count()

    return render(request, 'teachers/teacher_dashboard.html', {
        'teacher': teacher,
        'students_count': students.count(),
        'total_classes': total_classes,
        'present': present,
        'today_attendance': today,
        'students': students[:10]
    })


#--------------student dashboard----------------

@login_required
def student_dashboard(request):
    student = Student.objects.filter(email=request.user.email).first()

    if not student:
        return render(request, 'students/student_dashboard.html', {
            'error': 'Student profile not found'
        })

    records = Attendance.objects.filter(student=student).order_by('-date')

    total = records.count()
    present = records.filter(status='P').count()
    percentage = (present / total * 100) if total > 0 else 0

    return render(request, 'students/student_dashboard.html', {
        'student': student,
        'records': records[:10],
        'total': total,
        'present': present,
        'percentage': round(percentage, 2)
    })


# main dashboard view
@login_required
def dashboard(request):
    user = request.user

    # ADMIN
    if user.is_superuser:
        return render(request, 'dashboard.html', {
            'total_students': Student.objects.count(),
            'total_teachers': Teacher.objects.count(),
            'today_attendance': Attendance.objects.filter(
                date=timezone.now().date()
            ).count()
        })

    # TEACHER
    teacher = Teacher.objects.filter(user=user).first()
    if teacher:
        return redirect('teacher_dashboard')

    # STUDENT
    student = Student.objects.filter(user=user).first()
    if student:
        return redirect('student_dashboard')

    # fallback
    return render(request, 'error.html', {
        'message': 'No role assigned to this account'
    })
