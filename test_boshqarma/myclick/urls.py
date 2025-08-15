from django.urls import path
from . import views

urlpatterns = [
    path('process/click/transaction/create/<int:session_id>', views.CreateClickTransactionView.as_view()),
    path('process/click/transaction/', views.ClickTransactionTestView.as_view()),
    path('process/click/service/<service_type>', views.ClickMerchantServiceView.as_view())
]
