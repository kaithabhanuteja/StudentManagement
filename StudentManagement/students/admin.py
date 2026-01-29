from django.contrib import admin
from .models import Profile

# Register your models here.


from .models import Profile, Student, Teacher

admin.site.register(Student)
admin.site.register(Teacher)


admin.site.register(Profile)
