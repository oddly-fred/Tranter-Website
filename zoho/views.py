from django.shortcuts import render, get_object_or_404
from .models import ZohoProduct

def zoho_home(request):
    is_nigeria = getattr(request, 'is_nigeria', False)

    if is_nigeria:
        products = ZohoProduct.objects.all()
    else:
        products = ZohoProduct.objects.filter(region__in=['global', 'both'])

    return render(request, 'zoho/zoho.html', {
        'products': products,
        'is_nigeria': is_nigeria
    })


def product_detail(request, slug):
    product = get_object_or_404(ZohoProduct, slug=slug)

    return render(request, 'zoho/product_detail.html', {
        'product': product
    })


def zoho_detail(request, slug):
    product = get_object_or_404(ZohoProduct, slug=slug)
    return render(request, "zoho/product_detail.html", {"product": product})