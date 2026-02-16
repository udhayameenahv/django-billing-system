from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('generate_bill/<int:bill_id>', views.generate_bill, name='generate_bill'),
    path('purchase_history/', views.purchase_history, name='purchase_history'),
]