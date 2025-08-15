from .views import SubjectListView, StudentMonthSessionListView, MonthSessionGetView
from django.urls import path


# students/<int:student_id>/subjects/<int:subject_id>/marks/
urlpatterns = [
    # path('subjects/<int:subject_id>/marks/', StudentSubjectMarksView.as_view(), name='linkedin-url'),

    path('subjects', SubjectListView.as_view(), name='sujects'),
    path('month-sessions', StudentMonthSessionListView.as_view(), name='month-sessions'),
    path('month-sessions/<int:month_session_id>', MonthSessionGetView.as_view(), name='month-sessions-get'),
    
]

