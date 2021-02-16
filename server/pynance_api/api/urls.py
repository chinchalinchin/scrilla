
from django.urls import path

from api import views

urlpatterns = [
    path('optimize/', views.optimize),
    path('risk-return/', views.risk_return),
    path('efficient-frontier', views.efficient_frontier),
    path('moving-averages', views.moving_averages),
    path('discount-dividend', views.discount_dividend)
]
