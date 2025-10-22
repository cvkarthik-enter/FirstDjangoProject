# app/views.py
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