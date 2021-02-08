
from django.urls import path

from api import views

urlpatterns = [
    path('optimize/', views.optimize),
    path('risk-return/', views.risk_return)
]
