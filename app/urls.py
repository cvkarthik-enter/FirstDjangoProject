# app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Login and Logout
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('accounts/login/', views.login_view),   # <-- add this line

    # Price listing (for all users)
    path('prices/', views.price_list_view, name='price_list'),

    # Admin-only price update
    path('update/<int:product_id>/', views.update_price_view, name='update_price'),

    # Admin-only create new product
    path('create/', views.create_product_view, name="create_product"),
]