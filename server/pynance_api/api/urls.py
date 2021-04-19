
from django.urls import path

from api import views

urlpatterns = [
    path('risk-return/', views.risk_return),
    path('correlation/', views.correlation),
    path('optimize/', views.optimize),
    path('efficient-frontier', views.efficient_frontier),
    path('moving-averages', views.moving_averages),
    path('discount-dividend', views.discount_dividend)
]
