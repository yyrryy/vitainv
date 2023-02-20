from django import template
from pis_product.models import StockIn,StockOut, Product

register = template.Library()

@register.simple_tag
def product_notifications(retailer_id):
    p=Product.objects.filter(retailer__id=retailer_id)
    return len([i for i in p if i.product_available_items()<=10])

@register.simple_tag
def lenproducts():
    return Product.objects.all().count

@register.simple_tag
def products():
    return Product.objects.all()

