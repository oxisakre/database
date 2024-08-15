from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('stats/', views.stats_view, name='stats_view'),
    path('boxes/', views.box_usage_view, name='box_usage'),
]
