from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', views.user_list, name='user_list'),
    path('success/', views.success_page, name='success_page'),
    path('payment/create/', views.create_order, name='create_order'),
    path('emi/create/', views.create_emi_schedule, name='create_emi_schedule'),
    path('emi/list/', views.list_emi_schedule, name='list_emi_schedule'),
    path('payment/status/', views.payment_status, name='payment_status'),
    path('rules/', views.rule_list, name='rule_list'),
    path('rules/<int:pk>/', views.rule_detail, name='rule_detail'),
]