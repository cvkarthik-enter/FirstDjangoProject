# app/views.py
from decimal import Decimal, InvalidOperation
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
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
    # last 10 changes. also can be done using the below. but in models->class PriceHistory->product (related_name='history')
    # price_history = PriceHistory.objects.filter(product=product).order_by('-updated_at')[:10]

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


# creating a new option for the admin to create a new product
@login_required
@user_passes_test(lambda u: u.is_staff)
def create_product_view(request):
    """
    Simple admin-only view to add a new product.
    Expects POST fields:
      - name
      - current_price

    GET: renders a template 'create_product.html' with a small form.
    POST: validates input, creates Product, and redirects to price list.
    """
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        raw_price = (request.POST.get('current_price') or '').strip()

        if not name:
            messages.error(request, 'Product name is required')
            return redirect('create_product')

        try:
            # converting to decimal. This will avoid floating point issues.
            price = Decimal(raw_price)
        except (InvalidOperation, TypeError):
            messages.error(request, 'Enter valid price')
            return redirect('create_product')

        if price < 0:
            messages.error(request, "Price cannot be negative.")
            return redirect('create_product')

        try:
            Product.objects.create(name=name, current_price=price)
        except IntegrityError:
            #  Since model.py Product class has name as unique. if a new object is attempting
            # to create a new Product object, with the same name as an existing object.
            messages.error(request, "A product with that name already exists.")
            return redirect('create_product')

        messages.success(request, f"Product '{name}' created with price ₹{price}.")
        return redirect('price_list')
