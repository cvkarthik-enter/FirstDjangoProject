# app/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Login and Logout
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Price listing (for all users)
    path('prices/', views.price_list_view, name='price_list'),

    # Admin-only price update
    path('update/<int:product_id>/', views.update_price_view, name='update_price'),
]