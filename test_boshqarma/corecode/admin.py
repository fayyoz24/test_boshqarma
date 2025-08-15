from django.contrib import admin
from .models import Subject, Class, School, Tuman, MonthSession
# Register your models here.
# class JobTitleAdmin(admin.ModelAdmin):
#     list_display=['job_title', 'sector']
#     search_fields = ['job_title']
#     ordering = ['job_title']
#     @admin.display(description='sector')
#     def sector(self, object):
#         return object.sector.sector
admin.site.register(Tuman)
admin.site.register(School)
admin.site.register(Class)
admin.site.register(Subject)
admin.site.register(MonthSession)