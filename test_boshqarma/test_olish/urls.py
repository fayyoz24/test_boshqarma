from .views import (CreateTestSessionView, TestResultsView,  
                     FakeQuestionOptionAPIView,
                    DeleteTestSessionView, FakeUserCreateView,
                    SubjectTestHistoryView, ResultsByClassSubjectThemes,
                    ThemeStudentResultsView, SchoolSubjectAveragesView)
from .view_test import AddTest
from django.urls import path
urlpatterns = [
    path('create-test_session/<int:subject_theme_id>', CreateTestSessionView.as_view(), name='teacher-marking'),
    path('test-results/<int:test_session_id>', TestResultsView.as_view(), name='teacher-marks-get'),
    path('fake-question-option', FakeQuestionOptionAPIView.as_view(), name='fake-question-option'),
    path('delete-test-session/<int:pk>', DeleteTestSessionView.as_view(), name='delete-test-session'),
    path('subject-test-history/<int:subject_id>', SubjectTestHistoryView.as_view(), name='delete-test-session'),
    path('class/<int:class_id>/subject/<int:subject_id>/results/', ResultsByClassSubjectThemes.as_view(), name='class-test-results'),
    path('theme/<int:theme_id>/results', ThemeStudentResultsView.as_view(), name='theme-student-results'),
    path('school-subject-average', SchoolSubjectAveragesView.as_view(), name='school-subject-average'),
    path('fake-users', FakeUserCreateView.as_view(), name='fake-users'),
    
    
    path('add-test/<int:theme_id>/', AddTest.as_view(), name='add-test'),


]