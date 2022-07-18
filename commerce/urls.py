from django.urls import path
from . import views


urlpatterns = [
    path('', views.index , name = 'home'  ),
    path('search' , views.search , name= 'search'),
    path('add_product' , views.add_prod , name='add'),
    path('product/<int:pk>' , views.pod_detail , name ='details'),
    path('add_to_cart/<int:pk>' , views.add_to_cart , name='add-to-cart'),
    path("cart_view" , views.cartview , name='cartview'),
    path('item-add/<int:pk>' , views.addcart , name='cart-add'),
    path('item-minus/<int:pk>' , views.minuscart , name='cart-minus'),
    path('address' , views.address_check , name ='address'),
    path('checkout' , views.checkout , name ='checkout'),
    path('handler' , views.handler , name ='handler'),
] 