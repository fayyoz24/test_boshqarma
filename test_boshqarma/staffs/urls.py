from .views import (TeacherProfileView, 
                    # TeacherMarkClassView, 
                    # TeacherMarksView, 
                    DashboardAnalyticsView, 
                    TumanAnalyticsBySubjectView,
                    SchoolAnalyticsBySubjectView
                    )

from django.urls import path
# students/<int:student_id>/subjects/<int:subject_id>/marks/
urlpatterns = [
    path('teacher-detail/', TeacherProfileView.as_view(), name='teacher'),
    # path('teacher/marking', TeacherMarkClassView.as_view(), name='teacher-marking'),
    # path('teacher/marks-get/', TeacherMarksView.as_view(), name='teacher-marks-get'),
    path('analytics/dashboard/', DashboardAnalyticsView.as_view(), name='dashboard-analytics'),
    path('analytics/tuman-by-subjects/', TumanAnalyticsBySubjectView.as_view(), name='tuman-analytics'),
    path('analytics/school-by-subjects/', SchoolAnalyticsBySubjectView.as_view(), name='school-analytics'),
]
# teacher/marks/
