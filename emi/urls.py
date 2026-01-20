from django.urls import path
from . import views


urlpatterns = [
    path('users/', views.user_list, name='user_list'),
    path('success/', views.success_page, name='success_page'),
    path('emi_schedule/', views.create_emi_schedule, name='create_emi_schedule'),
    path('create_order/', views.create_order, name='create_order'),
    path('payment_status/', views.payment_status, name='payment_status'),
    path('admins/rules/', views.list_rules, name='list_rules'),
    path('admins/rules/add/', views.add_rule, name='add_rule'),
    path('admins/rules/edit/<int:rule_id>/', views.edit_rule, name='edit_rule'),
    path("admins/rules/delete/<int:rule_id>/", views.delete_rule, name="delete_rule"),

]