from django.contrib import admin
from .models import Student
# Register your models here.
# class JobTitleAdmin(admin.ModelAdmin):
#     list_display=['job_title', 'sector']
#     search_fields = ['job_title']
#     ordering = ['job_title']
#     @admin.display(description='sector')
#     def sector(self, object):
#         return object.sector.sector


class StudentAdmin(admin.ModelAdmin):
    list_display=['username', 'first_name', 'last_name','current_class']
    search_fields = ['first_name', 'last_name']
    ordering = ['current_class', 'first_name']
    @admin.display(description='username')
    def username(self, object):
        try:
            return object.user.username
        except:
            return "None"
admin.site.register(Student, StudentAdmin)