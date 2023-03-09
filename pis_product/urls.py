from django.urls import re_path



# import all above in one line not commented
from .views import (
    ProductItemList, ProductDetailList, AddNewProduct, AddProductItems,
    PurchasedItems, ExtraItemsView, ClaimedProductFormView,
    ClaimedItemsListView, StockItemList, AddStockItems, StockOutItems,
    StockDetailView, StockInListView, StockOutListView, ProductUpdateView,
    StockInUpdateView, addbulk, product_search, deleteproduct, lowstock, addoneproduct, getproducts, productslistbycategory, categories, addbulkcategory, deletecategory, addcategory, getproductsbycategory, searchproductsincategory, updateproduct, addstock, producthistory, supply, addsupply, reportnetprofit, reports, productsranking, downranking, relve, statsofrelve, addsupplier, dailystats, dailyproductsranking, dailyproductsrankingdown, bonentree, supplierslist, supplierinfo, addpaymentsupplier, addclient, dailystatsstock, bonsentrees
)

from pis_product.logs_view import DailyStockLogs, MonthlyStockLogs


urlpatterns = [
    re_path(r'^addclient/',addclient, name='addclient'),
    re_path(r'^bonsentrees/',bonsentrees, name='bonsentrees'),
    re_path(r'^dailystatsstock/',dailystatsstock, name='dailystatsstock'),
    re_path(r'^bonentree/(?P<id>\d+)',bonentree, name='bonentree'),
    re_path(r'^supplierslist/',supplierslist, name='supplierslist'),
    re_path(r'^supplierinfo/(?P<id>\d+)',supplierinfo, name='supplierinfo'),
    re_path(r'^addpaymentsupplier/(?P<id>\d+)',addpaymentsupplier, name='addpaymentsupplier'),
    re_path(r'^dailystats/',dailystats, name='dailystats'),
    re_path(r'^dailyproductsranking/',dailyproductsranking, name='dailyproductsranking'),
    re_path(r'^dailyproductsrankingdown/',dailyproductsrankingdown, name='dailyproductsrankingdown'),

    re_path(r'^items/list/$', ProductItemList.as_view(), name='items_list'),
    re_path(r'^items/addbulk/',addbulk, name='addbulk'),
    re_path(r'^product_search',product_search, name='product_search'),
    re_path(r'^item/(?P<pk>\d+)/detail/list/$',ProductDetailList.as_view(),name='item_details'),
    re_path(r'^item/(?P<product_id>\d+)/add/$',AddProductItems.as_view(),name='add_product_items'),
    re_path(r'^items/purchased/$', PurchasedItems.as_view(),name='purchased_items'),
    re_path(r'^items/extra/purchased/$', ExtraItemsView.as_view(),name='purchased_extra_items'),
    re_path(r'^items/claimed/$', ClaimedProductFormView.as_view(),name='claimed_items'),
    re_path(r'^items/claimed/list/$', ClaimedItemsListView.as_view(),name='claimed_items_list'),
    re_path(r'^retailer/(?P<retailer_id>\d+)/add/$',AddNewProduct.as_view(),name='add_product'),
    re_path(r'^stock/items/list/$', StockItemList.as_view(), name='stock_items_list'),
    re_path(r'^stock/item/(?P<product_id>\d+)/add/$',AddStockItems.as_view(),name='add_stock_items'),
    re_path(r'^stock/item/(?P<product_id>\d+)/out/$',StockOutItems.as_view(),name='stock_out_items'),
    re_path(r'^stock/item/(?P<product_id>\d+)/detail/$',StockDetailView.as_view(),name='stock_detail'),
    re_path(r'^(?P<product_id>\d+)/stock/in/$',StockInListView.as_view(),name='stockin_list'),
    re_path(r'^(?P<product_id>\d+)/stock/out/$',StockOutListView.as_view(),name='stockout_list'),
    re_path(r'^(?P<pk>\d+)/update/$',ProductUpdateView.as_view(),name='update_product'),
    re_path(r'^(?P<pk>\d+)/stockin/update/$',StockInUpdateView.as_view(),name='update_stockin'),
    re_path(r'^items/deleteproduct/',deleteproduct, name='delete_product'),
    re_path(r'^items/lowstock/',lowstock, name='lowstock'),
    re_path(r'^items/addoneproduct/',addoneproduct, name='addoneproduct'),
    re_path(r'^items/getproducts/',getproducts, name='getproducts'),
    re_path(r'^items/productslistbycategory/',productslistbycategory, name='productslistbycategory'),
    re_path(r'^items/categories/',categories, name='categories'),
    re_path(r'^items/addcategory/',addcategory, name='addcategory'),
    re_path(r'^items/getproductsbycategory/',getproductsbycategory, name='getproductsbycategory'),
    re_path(r'^items/searchproductsincategory/',searchproductsincategory, name='searchproductsincategory'),
    re_path(r'^items/addbulkcategory/(?P<id>\d+)',addbulkcategory, name='addbulkcategory'),
    re_path(r'^updateproduct/(?P<id>\d+)',updateproduct, name='updateproduct'),
    re_path(r'^producthistory/(?P<id>\d+)',producthistory, name='producthistory'),
    re_path(r'^addstock/(?P<id>\d+)',addstock, name='addstock'),
    re_path(r'^items/deletecategory/(?P<id>\d+)',deletecategory, name='deletecategory'),
    re_path(r'^supply/',supply, name='supply'),
    re_path(r'^addsupply/',addsupply, name='addsupply'),
    re_path(r'^reports/',reports, name='reports'),
    re_path(r'^reportnetprofit/',reportnetprofit, name='reportnetprofit'),
    re_path(r'^relve/',relve, name='relve'),
    re_path(r'^statsofrelve/',statsofrelve, name='statsofrelve'),

    re_path(r'^productsranking/',productsranking, name='productsranking'),
    re_path(r'^downranking/',downranking, name='downranking'),
    re_path(r'^addsupplier/',addsupplier, name='addsupplier'),

    # Logs
    re_path(r'^stock/logs/daily/$', DailyStockLogs.as_view(),name='daily_stock_logs'),
    re_path(r'^stock/logs/monthly/$', MonthlyStockLogs.as_view(),name='monthly_stock_logs'),
]
