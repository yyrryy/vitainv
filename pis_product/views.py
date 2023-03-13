from __future__ import unicode_literals
from django.shortcuts import render, redirect
import json
from django.views.generic import TemplateView, UpdateView
from django.views.generic import FormView, ListView
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.db.models import Sum, F, DecimalField, ExpressionWrapper, Q
from pis_product.models import PurchasedProduct, ExtraItems, ClaimedProduct,StockOut, StockIn, Product, ProductDetail, Category, SubCategory, Supplier, Itemsbysupplier, Avancesbon
from pis_product.forms import (
    ProductForm, ProductDetailsForm, ClaimedProductForm,StockDetailsForm,StockOutForm)
from django.utils import timezone
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from pis_retailer.models import Retailer
from django.db.models import Count
from django.db import transaction
from datetime import datetime
from pis_sales.models import SalesHistory
from pis_com.models import Customer

this_year = datetime.now().year
this_month = datetime.now().month


def sitemap(request):
    pass

# add new ledger from modal
@csrf_exempt
def addclient(request):
    name=request.POST.get('name')
    phone=request.POST.get('phone') or 0000000000
    ice=request.POST.get('ice') or None
    Customer.objects.create(customer_name=name,customer_phone=phone,address=ice, retailer=Retailer.objects.get(id=request.user.retailer_user.retailer.id))
    return JsonResponse({'status':True})


def productslistbycategory(request):

    categories = Category.objects.filter(parent=None)
    cc = Category.objects.filter(children__isnull=True)
    parents = Category.objects.all()
    first=0
    if cc:
        first=cc[0].id

    ctx={
        'parents':parents,
        'categories':categories,
        'title':'لائحة المنتجات بالتصنيف',
        'children':cc,
        #first id to put it in the form of adding bulk
        'firstid':first
    }
    return render(request, 'products/productslistbycategory.html', ctx)

def categories(request):
    categories = Category.objects.all()
    ctx={
        'cc':categories,
        'title':'Liste Categories'
    }
    return render(request, 'products/categories.html', ctx)

def getproductsbycategory(request):
    # category = Category.objects.get(pk=request.POST.get('category'))
    # products = category.product.filter(category=category)[:10]
    # get ten products from the category
    products = Product.objects.filter(category__pk=request.POST.get('category'))
    ctx={
        'products':products,
    }
    return JsonResponse({
        'data':render(request, 'products/product_search.html', ctx).content.decode('utf-8')
    })

def searchproductsincategory(request):
    # Category=Category.objects.get(pk=request.POST.get('category'))
    # products = Category.product.filter(name__icontains=request.POST.get('item'))
    # earch products in category given
    products = Product.objects.filter(category__pk=request.POST.get('category'), name__icontains=request.POST.get('name'))
    ctx={
        'products':products,
    }
    return JsonResponse({
        'data':render(request, 'products/product_search.html', ctx).content.decode('utf-8')
    })


@csrf_exempt
def addbulkcategory(request, id):
    sub=Category.objects.get(pk=id)
    myfile=request.FILES["excel_file"]
    retailer=Retailer.objects.get(id=request.user.retailer_user.retailer.id)
    df = pd.read_excel(myfile)
    df = df.fillna('-')
    for d in df.itertuples():
        
        product = Product.objects.create(
            retailer=retailer,
            name=d.article,
            price=d.prix,
            pr_achat=d.prachat,
            category=sub
        )
        StockIn.objects.create(
            product=product,
            quantity=d.qty,
        )
    #return a json response
    return redirect('product:productslistbycategory')


@csrf_exempt
def addcategory(request):
    category=request.POST.get('category')
    parent=None if request.POST.get('parent')=='0' else Category.objects.get(pk=request.POST.get('parent'))
    Category.objects.create(name=category, parent=parent)
    return redirect('product:productslistbycategory')

def deletecategory(request, id):
    category=Category.objects.get(pk=id)
    category.delete()
    return redirect('product:categories')
    


@csrf_exempt
def product_search(request):
    name=request.POST.get('name')
    products= request.user.retailer_user.retailer.retailer_product.all().filter(name__icontains=name)
    return JsonResponse({
        'data': render(request, 'products/product_search.html', {'products': products}).content.decode('utf-8')
    })


@csrf_exempt
def getproducts(request):
    products = Product.objects.filter(name__icontains=request.POST.get('item'))
    return JsonResponse({
        'data':render(request, 'products.html', {'products': products}).content.decode('utf-8')
    })


@csrf_exempt
def addbulk(request):
    # get the uploaded file

    myfile=request.FILES[next(iter(request.FILES))]
    retailer=Retailer.objects.get(id=request.user.retailer_user.retailer.id)
    
    df = pd.read_excel(myfile)
    df = df.fillna('-')
    for d in df.itertuples():
        product = Product.objects.create(
            retailer=retailer,
            name=d.article,
            brand_name=d.marque,
            price=d.prix,
            pr_achat=d.prachat
        )
        StockIn.objects.create(
            product=product,
            quantity=d.qty,
        )
    #return a json response
    return redirect('index')

def lowstock(request):
    products = Product.objects.filter()
    low=[]
    for i in products:
        if i.product_available_items()<=10:
            low.append(i)
    return render(request, 'products/lowstock.html', {'products': low, 'title':'Produits en stock bas'})

@csrf_exempt
def addoneproduct(request):
    # get data from formData sent from the ajax request
    name = request.POST.get('name')
    price = request.POST.get('price')
    prachat = request.POST.get('prachat') 
    brand = request.POST.get('brand')
    stock=request.POST.get('stock')
    category=request.POST.get('category')
    try:
        product=Product.objects.create(
            retailer=request.user.retailer_user.retailer,
            name=name,
            brand_name=brand,
            price=price,
            pr_achat=prachat,
            category=Category.objects.get(pk=category)
        )
        StockIn.objects.create(
            product=product,
            quantity=stock,
        )
    except Exception as e:
        print(e)
    #return a json response without serialaize error data as product is not json serializable
    # return JsonResponse({
    #     'data':{
    #         'name':product.name,
    #         'price':product.price,
    #         'prachat':product.pr_achat,
    #         'brand':product.brand_name,
    #         'stock':product.product_available_items(),
    #         'id':product.id
    #     }
    # })
    return redirect('product:productslistbycategory')



# new view to update product from the modals
def updateproduct(request, id):
    # get data from formData sent from the ajax request
    try:
        name = request.POST.get('name')
        price = request.POST.get('price')
        prachat = request.POST.get('pr_achat') 
        product=Product.objects.get(pk=id)
        product.name=name
        product.price=price
        product.pr_achat=prachat
        product.save()
        #return a json response without serialaize error data as product is not json serializable
        return JsonResponse({
            'status': True,
        })
    except Exception as e:
        return JsonResponse({
            'status': False,
            'error': e
        })

# new view to add stock from modal
def addstock(request, id):
    try:
        stock = float(request.POST.get('stock'))
        product=Product.objects.get(pk=id)
        StockIn.objects.create(
            product=product,
            quantity=stock,
        )
        #return a json response without serialaize error data as product is not json serializable
        return JsonResponse({
            'status': True,
        })
    except Exception as e:
        return JsonResponse({
            'status': False,
            'error': e
        })

# new view for product history
def producthistory(request, id):
    product=Product.objects.get(pk=id)
    pr=StockIn.objects.filter(product=product).order_by('-dated_order')
    stockout=PurchasedProduct.objects.filter(product=product)
    totalin=pr.aggregate(Sum('quantity')).get('quantity__sum')
    totalcost=round(float(totalin)*float(product.pr_achat), 2)
    ctx={ 'title':'تفاصيل المنتج', 'stockin':pr, 'product':product,  'totalin':totalin, 'totalcost':totalcost, 'netprofit':0, 'unitcost':totalcost/totalin}
    if stockout:
        totalamountout=stockout.aggregate(Sum('purchase_amount')).get('purchase_amount__sum')
        ctx.update({
            'stockout':stockout,
            'totalamountout':round(totalamountout, 2),
            'totalout':stockout.aggregate(Sum('quantity')).get('quantity__sum'),
            'netprofit':round(float(totalamountout)-float(totalcost), 2),
            'rest':totalin-stockout.aggregate(Sum('quantity')).get('quantity__sum'), 'percentage':round(stockout.aggregate(Sum('quantity')).get('quantity__sum')*100/totalin),
        })
    else:
        ctx.update({
            'netprofit':-float(totalcost)
        })
    return render(request, 'products/producthistory.html', ctx)



def reports(request):
    return render(request, 'products/reports.html', {'title':'التقارير'})


def reportnetprofit(request):
    year=this_year if request.POST.get('year')=='0' else request.POST.get('year')
    month=False if request.POST.get('month')=='0' else request.POST.get('month')
    if month:
        totalprofit=round(SalesHistory.objects.filter(
            created_at__year=year, created_at__month=month
            ).aggregate(
            total_revenue=Sum('paid_amount')
        )['total_revenue'] or 0, 2)

        totalcost=round(Product.objects.filter(
            stockin_product__dated_order__year=year, stockin_product__dated_order__month=month
            ).annotate(
                total_items=Sum('stockin_product__quantity')
            ).aggregate(
                total_cost=ExpressionWrapper(Sum(F('pr_achat') * F('total_items'), output_field=DecimalField()), output_field=DecimalField())
            )['total_cost'] or 0, 2)
    else:
        totalprofit=round(SalesHistory.objects.filter(
            created_at__year=year
            ).aggregate(
            total_revenue=Sum('paid_amount')
        )['total_revenue'] or 0, 2)
        totalcost=round(Product.objects.filter(
            stockin_product__dated_order__year=year
            ).annotate(
                total_items=Sum('stockin_product__quantity')
            ).aggregate(
                total_cost=ExpressionWrapper(Sum(F('pr_achat') * F('total_items'), output_field=DecimalField()), output_field=DecimalField())
            )['total_cost'] or 0, 2)
    

    
    
    #for i in products:
        #totalcost+=round(float(i.product_available_items())*float(i.pr_achat), 2)
        # stockout=PurchasedProduct.objects.filter(product=i)
        # if stockout:
        #     for i in stockout:
        #         totalprofit+=i.purchase_amount
        
    
   
    return JsonResponse({
        'totalprofit':totalprofit,
        'totalcost':totalcost,
        'netprofit':round(float(totalprofit)-float(totalcost), 2)
    })


def productsranking(request):
    year=this_year if request.POST.get('year')=='0' else request.POST.get('year')
    month=False if request.POST.get('month')=='0' else request.POST.get('month')
    if month:products = (
    PurchasedProduct.objects.filter(
        created_at__year=year, created_at__month=month
        ).values('product')
    .annotate(
        total_quantity=Sum('quantity'),
        total_purchase_amount=Sum('purchase_amount')
    )
    .order_by('-total_quantity')
    .values('product__name', 'total_quantity', 'total_purchase_amount')[:10]
    )
    else:
        products = (
    PurchasedProduct.objects.filter(
        created_at__year=year
        ).values('product')
    .annotate(
        total_quantity=Sum('quantity'),
        total_purchase_amount=Sum('purchase_amount')
    )
    .order_by('-total_quantity')
    .values('product__name', 'total_quantity', 'total_purchase_amount')[:10]
    )
    return JsonResponse({
        'data':render(request, 'products/productsranking.html', {'products':products}).content.decode('utf-8')
    })


def downranking(request):
    year=this_year if request.POST.get('year')=='0' else request.POST.get('year')
    month=False if request.POST.get('month')=='0' else request.POST.get('month')
    if month:products = (
    PurchasedProduct.objects.filter(
        created_at__year=year, created_at__month=month
        ).values('product')
    .annotate(
        total_quantity=Sum('quantity'),
        total_purchase_amount=Sum('purchase_amount')
    )
    .order_by('total_quantity')
    .values('product__name', 'total_quantity', 'total_purchase_amount')[:10]
    )
    
    else:
        products = (
    PurchasedProduct.objects.filter(
        created_at__year=year
        ).values('product')
    .annotate(
        total_quantity=Sum('quantity'),
        total_purchase_amount=Sum('purchase_amount')
    )
    .order_by('total_quantity')
    .values('product__name', 'total_quantity', 'total_purchase_amount')[:10]
    )
    
    return JsonResponse({
        'data':render(request, 'products/productsranking.html', {'products':products}).content.decode('utf-8')
    })

def relve(request):
    products=request.user.retailer_user.retailer.retailer_product.all()
    return render(request, 'products/relve.html', {'title': 'جرد المخزون', 'products':products})


def statsofrelve(request):
    year=this_year if request.POST.get('year')=='0' else request.POST.get('year')
    month=False if request.POST.get('month')=='0' else request.POST.get('month')
    product_data = []
    products=request.user.retailer_user.retailer.retailer_product.all()
    # Loop through each product
    for product in products:
        if month:
        # Get the available and sold items for the product
            totalitems=StockIn.objects.filter(
                product=product, dated_order__year=year, dated_order__month=month
            ).aggregate(Sum('quantity'))['quantity__sum'] or 0   
            available_items = product.product_available_items()
            sold_items = PurchasedProduct.objects.filter(
                product=product, created_at__year=year, created_at__month=month
            ).aggregate(Sum('quantity'))['quantity__sum'] or 0

            # Calculate the total cost and total profit for the product
            total_cost = round(float(product.pr_achat) * float(totalitems), 2)
            total_profit = PurchasedProduct.objects.filter(
                product=product, created_at__year=year, created_at__month=month
            ).aggregate(Sum('purchase_amount'))['purchase_amount__sum'] or 0
            
            # Calculate the net profit for the product
            net_profit = round(float(total_profit) - float(total_cost), 2)

            # Add the product data to the list
            product_data.append({
                'id': product.id,
                'name': product.name,
                'available_items': available_items,
                'sold_items': sold_items,
                'total_profit': total_profit,
                'total_cost': total_cost,
                'net_profit': net_profit,
            })
        else:
            totalitems=StockIn.objects.filter(
                product=product, dated_order__year=year
            ).aggregate(Sum('quantity'))['quantity__sum'] or 0
            available_items = product.product_available_items()
            sold_items = PurchasedProduct.objects.filter(
                product=product, created_at__year=year
            ).aggregate(Sum('quantity'))['quantity__sum'] or 0

            # Calculate the total cost and total profit for the product
            total_cost = round(float(product.pr_achat) * float(totalitems), 2)
            total_profit = PurchasedProduct.objects.filter(
                product=product, created_at__year=year
            ).aggregate(Sum('purchase_amount'))['purchase_amount__sum'] or 0
            
            # Calculate the net profit for the product
            net_profit = round(float(total_profit) - float(total_cost), 2)

            # Add the product data to the list
            product_data.append({
                'id': product.id,
                'name': product.name,
                'available_items': available_items,
                'sold_items': sold_items,
                'total_profit': total_profit,
                'total_cost': total_cost,
                'net_profit': net_profit,
            })
    sorted_list = sorted(product_data, key=lambda k: k['total_profit'], reverse=True)

    return JsonResponse({
        'data':render(request, 'products/relvestats.html', {"products":sorted_list}).content.decode('utf-8')
    })


def dailystatsstock(request):
    date=request.POST.get('date')
    product_data = []
    products=request.user.retailer_user.retailer.retailer_product.all()
    # Loop through each product
    for product in products:
        # Get the available and sold items for the product
        totalitems=StockIn.objects.filter(
            product=product
        ).aggregate(Sum('quantity'))['quantity__sum'] or 0   
        available_items = product.product_available_items()
        sold_items = PurchasedProduct.objects.filter(
            product=product, created_at__date=date
        ).aggregate(Sum('quantity'))['quantity__sum'] or 0

        # Calculate the total cost and total profit for the product
        total_cost = round(float(product.pr_achat) * float(totalitems), 2)
        total_profit = PurchasedProduct.objects.filter(
            product=product, created_at__date=date
        ).aggregate(Sum('purchase_amount'))['purchase_amount__sum'] or 0
        
        # Calculate the net profit for the product
        net_profit = round(float(total_profit) - float(total_cost), 2)

        # Add the product data to the list
        product_data.append({
            'id': product.id,
            'name': product.name,
            'available_items': available_items,
            'sold_items': sold_items,
            'total_profit': total_profit,
            'total_cost': total_cost,
            'net_profit': net_profit,
        })
    sorted_list = sorted(product_data, key=lambda k: k['total_profit'], reverse=True)

    return JsonResponse({
        'data':render(request, 'products/relvestats.html', {"products":sorted_list}).content.decode('utf-8')
    })
def supply(request):
    suppliers=Supplier.objects.all()

    return render(request, 'products/supply.html', {'title':'ادخال السلع', 'suppliers':suppliers})


def addsupply(request):
    nbon=request.POST.get('nbon')
    items = json.loads(request.POST.get('items'))
    reciept=Itemsbysupplier.objects.create(supplier=Supplier.objects.get(pk=request.POST.get('supplier')), items=request.POST.get('items'), total=request.POST.get('total'), nbon=nbon, rest=request.POST.get('total'))
    with transaction.atomic():
        for i in items: 
            try:
                item=i.get('item_id')
                product = Product.objects.get(pk=item)
                if(not int(i['price'])==0):
                    product.pr_achat=float(i['price'])
                # or get the average pr_achat
                #product.pr_achat=round((float(product.pr_achat)+float(i['price']))/2, 2)

                product.save()
                
                StockIn.objects.create(
                    product=product,
                    quantity=i['qty'],
                    reciept=reciept
                )
            except Exception as e:
                pass
        
        return JsonResponse({
            'status': True,
        })

def bonentree(request, id):
    itemsbysupplier = json.loads(Itemsbysupplier.objects.get(id=id).items)
    
    return render(request, 'products/bonentree.html', {
        'suppliers':Supplier.objects.all(), 
        'items':itemsbysupplier,
        'title':'معلومات فاتورة الدخول',
        'bon':Itemsbysupplier.objects.get(id=id),
        'avances':Avancesbon.objects.filter(bon=id)
    })

def bonsentrees(request):
    bb=Itemsbysupplier.objects.all().order_by('-date')
    return render(request, 'products/supplierslist.html', {
        'title':'لائحة فزاتير الموردين',
        'bonslist':bb,
        # bons is true to add condition in template to only use one teplate for suppliers list and bons list
        'bons':True
    })

def supplierslist(request):
        
    suppliers=Supplier.objects.all()
    supplier_data = []
    for supplier in suppliers:
        rest = Itemsbysupplier.objects.filter(supplier=supplier).aggregate(rest=Sum('rest'))['rest'] or 0
        supplier_data.append({'id':supplier.id, 'name':supplier.name, 'details':supplier.detals, 'rest':rest})
    
    return render(request, 'products/supplierslist.html', {
        'title':'لائحة الموردين',
        'suppliers':supplier_data
    })

def supplierinfo(request, id):
    

    supplier=Supplier.objects.get(pk=id)
    bons=Itemsbysupplier.objects.filter(supplier=supplier)
    return render (request, 'products/supplierinfo.html', {
        'title':'Bon entree',
        'bons':bons,
        'supplier':supplier
    })

def addpaymentsupplier(request, id):
    amount=request.POST.get('amount')
    details=request.POST.get('details')
    bon=Itemsbysupplier.objects.get(pk=id)
    avances=Avancesbon.objects.filter(bon=bon).aggregate(Sum('avance'))['avance__sum']
    if avances:
        avances=float(avances)+float(amount)
    else:avances=amount
    bon.rest=float(bon.total)-float(avances)
    bon.save()
    Avancesbon.objects.create(
        bon=bon,
        avance=amount,
        details=details,
    )
    #return reverse('product:bonentree', kwargs={'id':bon.id})
    return JsonResponse({
        'rr':'rest'
    })

def addsupplier(request):
    try:
        name=request.POST.get('name')
        details=request.POST.get('details')
        Supplier.objects.create(name=name, detals=details)
        return JsonResponse({
            'data':'تمت الاضافة'
        })
    except :
        return JsonResponse({
            'data':'حدث خطأ'
        })

def dailystats(request):
    date=request.POST.get('date')
    totalprofit=round(SalesHistory.objects.filter(
            created_at__date=date
            ).aggregate(
            total_revenue=Sum('paid_amount')
        )['total_revenue'] or 0, 2)
    totalcost=round(Product.objects.filter(
            stockin_product__dated_order__date=date
            ).annotate(
                total_items=Sum('stockin_product__quantity')
            ).aggregate(
                total_cost=ExpressionWrapper(Sum(F('pr_achat') * F('total_items'), output_field=DecimalField()), output_field=DecimalField())
            )['total_cost'] or 0, 2)
    return JsonResponse({
        'totalprofit':totalprofit,
        'totalcost':totalcost,
        'netprofit':totalprofit-totalcost
    })

def dailyproductsranking(request):
    date=request.POST.get('date')
    products = (
    PurchasedProduct.objects.filter(
        created_at__date=date
        ).values('product')
    .annotate(
        total_quantity=Sum('quantity'),
        total_purchase_amount=Sum('purchase_amount')
    )
    .order_by('-total_quantity')
    .values('product__name', 'total_quantity', 'total_purchase_amount')
    )
    return JsonResponse({
        'data':render(request, 'products/productsranking.html', {'products':products}).content.decode('utf-8')
    })


def dailyproductsrankingdown(request):
    date=request.POST.get('date')
    products = (
    PurchasedProduct.objects.filter(
        created_at__date=date
        ).values('product')
    .annotate(
        total_quantity=Sum('quantity'),
        total_purchase_amount=Sum('purchase_amount')
    )
    .order_by('-total_quantity')
    .values('product__name', 'total_quantity', 'total_purchase_amount')
    )
    return JsonResponse({
        'data':render(request, 'products/productsranking.html', {'products':products}).content.decode('utf-8')
    })





class ProductItemList(TemplateView):
    template_name = 'products/product_list.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return 

        return super(
            ProductItemList, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProductItemList, self).get_context_data(**kwargs)
        products = (
            self.request.user.retailer_user.retailer.retailer_product.all()
        )
        context.update({
            'products': products
        })
        return context


class ProductDetailList(TemplateView):
    template_name = 'products/item_details.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))

        return super(
            ProductDetailList, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProductDetailList, self).get_context_data(**kwargs)
        try:
            product = (
                self.request.user.retailer_user.retailer.
                retailer_product.get(id=self.kwargs.get('pk'))
            )
        except ObjectDoesNotExist:
            raise Http404('Product not found with concerned User')

        context.update({
            'items_details': product.product_detail.all().order_by(
                '-created_at'),
            'product': product,
        })

        return context


class AddNewProduct(FormView):
    form_class = ProductForm
    template_name = 'products/add_product.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        return super(
            AddNewProduct, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        product = form.save()

        return HttpResponseRedirect(reverse('product:stock_items_list'))

    def form_invalid(self, form):
        return super(AddNewProduct, self).form_invalid(form)


class AddProductItems(FormView):
    template_name = 'products/add_product_items.html'
    form_class = ProductDetailsForm

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        return super(AddProductItems, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        product_item_detail = form.save()
        return HttpResponseRedirect(
            reverse('product:item_details', kwargs={
                'pk': product_item_detail.product.id
            })
        )

    def form_invalid(self, form):
        return super(AddProductItems, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(AddProductItems, self).get_context_data(**kwargs)
        try:
            product = (
                self.request.user.retailer_user.retailer.
                retailer_product.get(id=self.kwargs.get('product_id'))
            )
        except ObjectDoesNotExist:
            raise Http404('Product not found with concerned User')

        context.update({
            'product': product
        })
        return context


class PurchasedItems(TemplateView):
    template_name = 'products/purchased_items.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        return super(PurchasedItems, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PurchasedItems, self).get_context_data(**kwargs)
        purchased_product = PurchasedProduct.objects.filter(
            product__retailer=self.request.user.retailer_user.retailer
        ).order_by('-created_at')

        context.update({
            'purchased_products': purchased_product
        })

        return context


class ExtraItemsView(TemplateView):
    template_name = 'products/purchased_extraitems.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        return super(ExtraItemsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ExtraItemsView, self).get_context_data(**kwargs)
        extra_products = ExtraItems.objects.filter(
            retailer=self.request.user.retailer_user.retailer
        )

        context.update({
            'purchased_extra_items': extra_products
        })

        return context


class ClaimedProductFormView(FormView):
    template_name = 'products/claimed_product.html'
    form_class = ClaimedProductForm

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        return super(
            ClaimedProductFormView, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def purchased_items_update(claimed_item, claimed_number):
        product = (
            claimed_item.product.product_detail.filter(
                available_item__gte=claimed_number
            ).first()
        )
        product.purchased_item = (
            product.purchased_item - claimed_number
        )
        product.save()

    # def claimed_items_payment(self, claimed_item, amount):
    #     payment_form_kwargs = {
    #         'customer': claimed_item.customer.id,
    #         'retailer': self.request.user.retailer_user.retailer.id,
    #         'amount': amount,
    #         'description': 'Amount Refunded from Claimed'
    #                        ' Item ID (%s)' % claimed_item.id
    #     }
    #     payment_form = PaymentForm(payment_form_kwargs)
    #     if payment_form.is_valid():
    #         payment_form.save()

    def form_valid(self, form):
        claimed_item = form.save()

        # update the purchased product accordingly
        self.purchased_items_update(
            claimed_item=claimed_item,
            claimed_number=int(form.cleaned_data.get('claimed_items'))
        )

        # Doing a payment of claimed amount
        # self.claimed_items_payment(
        #     claimed_item=claimed_item,
        #     amount=form.cleaned_data.get('claimed_amount')
        # )

        return HttpResponseRedirect(reverse('product:items_list'))
    
    def form_invalid(self, form):
        return super(ClaimedProductFormView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(
            ClaimedProductFormView, self).get_context_data(**kwargs)

        products = (
            self.request.user.retailer_user.retailer.
            retailer_product.all().order_by('name')
        )
        customers = (
            self.request.user.retailer_user.retailer.
            retailer_customer.all().order_by('customer_name')
        )
        context.update({
            'products': products,
            'customers': customers,
        })

        return context


class ClaimedItemsListView(TemplateView):
    template_name = 'products/claimed_product_list.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        return super(
            ClaimedItemsListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(
            ClaimedItemsListView, self).get_context_data(**kwargs)
        context.update({
            'claimed_items': ClaimedProduct.objects.all().order_by(
                '-created_at')
        })
        return context


class StockItemList(ListView):
    template_name = 'products/stock_list.html'
    

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))

        return super(
            StockItemList, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset
        

    def get_context_data(self, **kwargs):
        
        context = super(StockItemList, self).get_context_data(**kwargs)
        context.update({
            'search_value_name': self.request.GET.get('name'),
            'title':"Liste des produits",


        })
        return context


class AddStockItems(FormView):
    template_name = 'products/add_stock_item.html'
    form_class = StockDetailsForm

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        return super(AddStockItems, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        product_item_detail = form.save()
        return HttpResponseRedirect(
             reverse('product:stockin_list', kwargs={'product_id': self.kwargs.get('product_id')})
            # used to reverse to entréé list
            #reverse('index')
        )

    def form_invalid(self, form):
        return super(AddStockItems, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(AddStockItems, self).get_context_data(**kwargs)
        try:
            product = (
                self.request.user.retailer_user.retailer.
                retailer_product.get(id=self.kwargs.get('product_id'))
            )
        except ObjectDoesNotExist:
            raise Http404('Product not found with concerned User')

        context.update({
            'product': product,
            'title':'Ajouter Entrée'
        })
        return context


class StockOutItems(FormView):
    form_class = StockOutForm
    template_name = 'products/stock_out.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        return super(StockOutItems, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        product_item_detail = form.save()
        return HttpResponseRedirect(
            reverse('product:stock_items_list')
        )

    def form_invalid(self, form):
        return super(StockOutItems, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(StockOutItems, self).get_context_data(**kwargs)
        try:
            product = (
                self.request.user.retailer_user.retailer.
                    retailer_product.get(id=self.kwargs.get('product_id'))
            )
        except ObjectDoesNotExist:
            raise Http404('Product not found with concerned User')

        context.update({
            'product': product,
            'title':"Sorties"
        })
        return context


class StockDetailView(TemplateView):
    template_name = 'products/stock_detail.html'

    def get_context_data(self, **kwargs):
        context = super(
            StockDetailView, self).get_context_data(**kwargs)

        try:
            item = Product.objects.get(id=self.kwargs.get('product_id'))
        except StockIn.DoesNotExist:
            return Http404('Item does not exists in database')

        item_stocks_in = item.stockin_product.all()
        item_stocks_out = item.stockout_product.all()

        context.update({
            'item': item,
            'item_stock_in': item_stocks_in.order_by('-dated_order'),
            'item_stock_out': item_stocks_out.order_by('-dated'),
        })

        return context


class StockInListView(ListView):
    template_name = 'products/stockin_list.html'
    paginate_by = 100
    model = StockIn
    ordering = '-id'

    def get_queryset(self):
        queryset = self.queryset
        if not queryset:
            queryset = StockIn.objects.all()

        queryset = queryset.filter(product=self.kwargs.get('product_id'))
        return queryset.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(StockInListView, self).get_context_data(**kwargs)
        context.update({
            'product': Product.objects.get(id=self.kwargs.get('product_id')),
            'title':'Entrée'
        })
        return context


class StockOutListView(ListView):
    template_name = 'products/stockout_list.html'
    paginate_by = 100
    model = StockOut
    ordering = '-id'

    def get_queryset(self, **kwargs):
        queryset = self.queryset
        if not queryset:
            queryset = StockOut.objects.all()

        queryset = queryset.filter(product=self.kwargs.get('product_id'))
        return queryset.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(StockOutListView, self).get_context_data(**kwargs)
        context.update({
            'product': Product.objects.get(id=self.kwargs.get('product_id'))
        })
        return context

#this update products
class ProductUpdateView(UpdateView):
    template_name = 'products/update_product.html'
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy('index')


class StockInUpdateView(UpdateView):
    template_name = 'products/update_stockin.html'
    model = StockIn
    form_class = StockDetailsForm

    def form_valid(self, form):
        obj = form.save()
        return HttpResponseRedirect(
            reverse('product:stockin_list',
                    kwargs={'product_id': obj.product.id})
        )
    
    def form_invalid(self, form):
        return super(StockInUpdateView, self).form_invalid(form)


def deleteproduct(request):
    if request.method == 'POST':
        product_id = request.POST.get('id')
        product = Product.objects.get(id=product_id)
        product.delete()
        return JsonResponse({'status': 'success'})