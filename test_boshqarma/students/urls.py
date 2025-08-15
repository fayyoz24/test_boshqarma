from .views import StudentTestHistoryView, AddStudentsByList
from .views import StudentDetailView
from django.urls import path
# students/<int:student_id>/subjects/<int:subject_id>/marks/
urlpatterns = [
    # path('subjects/<int:subject_id>/marks/', StudentSubjectMarksView.as_view(), name='subject-marks'),
    # path('subjects/', StudentClassSubjectView.as_view(), name='subject-marks'),
    path('detail/', StudentDetailView.as_view(), name='student-detail'),
    path('add-students/<int:school_id>', AddStudentsByList.as_view(), name='add-students'),
    path('subjects/<int:subject_id>/test-history/', StudentTestHistoryView.as_view(), name='test-history'),
]
