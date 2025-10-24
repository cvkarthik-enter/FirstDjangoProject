# app/views.py
from decimal import Decimal, InvalidOperation
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

from .models import Product, PriceHistory


@login_required
def price_list_view(request):
    products = Product.objects.all()
    context = {
        'products': products,
        'page_title': 'Current Prices',
    }
    return render(request, 'price_list.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def update_price_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    price_history = product.history.all()[:10]

    if request.method == 'POST':
        new_price_raw = request.POST.get('new_price')
        try:
            new_price = float(new_price_raw)
        except (TypeError, ValueError):
            messages.error(request, "Invalid price entered.")
            return redirect('update_price', product_id=product.id)

        # Save old price to history
        PriceHistory.objects.create(
            product=product,
            old_price=product.current_price,
            updated_by=request.user
        )

        # Update product price
        product.current_price = new_price
        product.save()

        messages.success(request, f"Price updated to ₹{new_price}")
        return redirect('price_list')

    context = {
        'product': product,
        'price_history': price_history,
        'page_title': f"Update Price: {product.name}",
    }
    return render(request, 'update_price.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def create_product_view(request):
    """
    Admin-only view to add a new product.
    GET: render form.
    POST: validate and create product or redirect back with messages.
    """
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        price_raw = (request.POST.get('current_price') or '').strip()

        if not name:
            messages.error(request, "Product name is required.")
            return redirect('create_product')

        try:
            price = Decimal(price_raw)
        except (InvalidOperation, TypeError):
            messages.error(request, "Enter a valid price (e.g. 199.99).")
            return redirect('create_product')

        if price < 0:
            messages.error(request, "Price cannot be negative.")
            return redirect('create_product')

        try:
            Product.objects.create(name=name, current_price=price)
        except IntegrityError:
            messages.error(request, "A product with that name already exists.")
            return redirect('create_product')

        messages.success(request, f"Product '{name}' created with price ₹{price}.")
        return redirect('price_list')

    # GET
    context = {'page_title': 'Add New Product'}
    return render(request, 'create_product.html', context)


def login_view(request):
    """
    Function-based login view:
    - Redirects authenticated users to price_list.
    - Clears pending messages on GET to keep the login page clean.
    - Handles POST to authenticate and login user.
    - Honors 'next' parameter for redirects after login.
    """
    # If the user is already authenticated, redirect them away from login page.
    if request.user.is_authenticated:
        return redirect('price_list')

    # Consume pending messages on GET so the login page does not show previous messages
    if request.method == 'GET':
        list(messages.get_messages(request))

    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = (request.POST.get('password') or '').strip()
        next_url = request.POST.get('next') or request.GET.get('next') or reverse('price_list')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'login.html', {'next': next_url}, status=200)

    # GET: render login form. include next if present in querystring
    next_url = request.GET.get('next', '')
    return render(request, 'login.html', {'next': next_url})


@require_POST
def logout_view(request):
    """
    Logs out the user and redirects to the login page with an info message.
    Only accepts POST for safety.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')