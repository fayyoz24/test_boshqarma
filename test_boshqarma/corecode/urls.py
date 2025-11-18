from .views import SubjectListCreateView, ClassListCreateView, TeacherCreateView, ClassUpdateDetailView, SubjectUpdateDetailView,StudentListCreateView, StudenListView
from .views import ClassDetailView, SubjectListView, StudentMonthSessionListView, MonthSessionGetView
from django.urls import path


# students/<int:student_id>/subjects/<int:subject_id>/marks/
urlpatterns = [
    # path('subjects/<int:subject_id>/marks/', StudentSubjectMarksView.as_view(), name='linkedin-url'),
    path('student-list-create/<int:id>', StudentListCreateView.as_view(), name='student-list-create'),
    path('student-list', StudenListView.as_view(), name='student-list-create'),
    path('teacher-create', TeacherCreateView.as_view(), name='teacher-create'),
    path('subject-create', SubjectListCreateView.as_view(), name='subject-create'),
    path('class-create', ClassListCreateView.as_view(), name='class-create'),
    path('class-get-update/<int:id>', ClassUpdateDetailView.as_view(), name='class-get-update'),
    path('subject-get-update/<int:id>', SubjectUpdateDetailView.as_view(), name='subject-get-update'),
    
    
    path('class/<int:pk>', ClassDetailView.as_view(), name='class-pk'),


    path('subjects', SubjectListView.as_view(), name='sujects'),
    path('month-sessions', StudentMonthSessionListView.as_view(), name='month-sessions'),
    path('month-sessions/<int:month_session_id>', MonthSessionGetView.as_view(), name='month-sessions-get'),
    
]

