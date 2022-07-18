from django.views.decorators.csrf import csrf_exempt
import datetime
from django.conf import settings
from django.http import HttpResponse 
from django.shortcuts import get_object_or_404, redirect, render
from .forms import AddForm , Addaddress
from .models import *
import razorpay
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

# Create your views here.

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_ID, settings.RAZORPAY_SECRET)) #imported from settings.py

def index(request):
    products = Product.objects.all()
    return render(request , 'index.html'  ,{'products' : products})

def search(request):
    query = request.GET.get("query" , "")
    products = Product.objects.filter(Q(name__icontains = query))
    return render(request , 'search.html' , {'prod':products , 'query':query})

def pod_detail(request , pk):
    product = Product.objects.get(pk = pk)
    return render(request , 'detail.html' , {'product' : product} )


@login_required
def add_prod(request): #adding products x admin required created on frontend html page.
    form = AddForm()
    if request.method == 'POST':
        form = AddForm(request.POST , request.FILES) #use request.FILES when uplaoding images/files
        if form.is_valid():
            form.save()
        return redirect('/')
    else:
        form = AddForm()
    return render(request , 'addproducts.html' ,{ 'form' : form})


def add_to_cart(request , pk):
    product = Product.objects.get(pk=pk)
    order_item , created = OrderItem.objects.get_or_create(product = product , ordered = False , user = request.user)
    order_qs = Order.objects.filter(user = request.user , ordered = False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk = pk).exists():
            order_item.quantity += 1
            print(order_item.quantity)
            order_item.save()
            messages.success(request ,"Added Item On Your Cart")
            return redirect("details" , pk=pk )
        else:
            order.items.add(order_item)
            messages.success(request ,"Added Item On Your Cart")
            return redirect("details" , pk=pk )
    else:
        ordered_date = datetime.datetime.now()
        order = Order.objects.create(user = request.user , ordered = False , ordered_date = ordered_date)
        order.items.add(order_item)
        messages.success(request ,"Added Item On Your Cart")
        return redirect("details" , pk=pk )

@login_required
def cartview(request):
    if Order.objects.filter(user = request.user , ordered =False).exists():
        order = Order.objects.get(user = request.user , ordered =False)
        return render(request,  'cart.html' ,{'order' : order}) 
    
    return render(request , 'cart.html')


def addcart(request, pk):
    product = Product.objects.get(pk=pk)
    order_item , created = OrderItem.objects.get_or_create(product = product , ordered = False , user = request.user)
    order_qs = Order.objects.filter(user = request.user , ordered = False)
    if order_qs.exists():
        if order_item.quantity < product.product_available:
            order = order_qs[0]
            if order.items.filter(product__pk = pk).exists():
                order_item.quantity += 1
                print(order_item.quantity)
                order_item.save()
                return redirect(cartview)
            else:
                order.items.add(order_item)
                return redirect("details" , pk=pk )
        else:
            return redirect(cartview)
    else:
        ordered_date = datetime.datetime.now()
        order = Order.objects.create(user = request.user , ordered = False , ordered_date = ordered_date)
        order.items.add(order_item)
        return redirect("details" , pk=pk )


def minuscart(request, pk):
    item = get_object_or_404(Product , pk = pk)
    order_qs = Order.objects.filter(user = request.user , ordered = False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk = pk).exists():
            order_item = OrderItem.objects.filter(product = item , user = request.user , ordered = False)[0]
            if order_item.quantity > 1 :
                order_item.quantity -= 1
                order_item.save()
                return redirect(cartview)
            else:
                order_item.delete() #to remove from models 
                order.items.filter(product__pk = pk).delete() #used because manytomany field....
                return redirect(cartview)
        else:
            return redirect(cartview)

# def address_check(request):
#     form = Addaddress()
#     if address.objects.filter(user= request.user).exists():
#         return redirect('checkout')
#     if request.method == 'POST':
#         form = Addaddress(request.POST,user= request.user)
#         if form.is_valid:
#             form.save()
#             return redirect('checkout')
#         else:
#             form = Addaddress()
#             redirect('address')
#     return render(request , 'address.html' , {'form' : form})

@login_required #decorator for anynomous user
def address_check(request):
    if address.objects.filter(user= request.user).exists():
        return redirect('checkout')
    if request.method == 'POST':
        country = request.POST.get("country")
        city = request.POST.get("city")
        street_address = request.POST.get("street")
        zip_code = request.POST.get("zip_code")
        phone = request.POST.get("phone_no")
        if address.objects.filter(phone_no = phone).exists():
            messages.error(request ,"OOPS, PHONE NUMBER ALREADY EXISTS ON OUR DATABASE. TRY ANOTHER ONE.")
        
        else:
            adress = address.objects.create(user = request.user , country = country , city =city , street_address=street_address,zip_code =zip_code ,phone_no =phone)
            adress.save()
            return redirect('checkout')
    else:
        redirect('address')

    return render(request , 'address.html')

@login_required
def checkout(request):
    try:
        order = Order.objects.get(user=request.user , ordered =False)
        adres = address.objects.get(user=request.user)
        order_amount = order.get_total_price() #calling function from model
        order_currency = 'INR'
        order_receipt = order.order_id
        notes = {
            'city' :  adres.city ,
            'street_address' : adres.street_address ,
            'zip_code' : adres.zip_code ,
            'phone_no' : adres.phone_no
            }
        razorpay_order = razorpay_client.order.create(dict(
            amount = order_amount * 100 , 
            currency = order_currency,
            receipt = order_receipt,
            notes = notes ,
            payment_capture = '0'
        ))
        print(razorpay_order['id']) #as razorpay is throwing multiple order id we saving it later
        # order.razorpay_order_id = razorpay_order['id']
        # order.save()
        return render(request , 'checkout.html' , {'adres':adres ,'order' : order , 'order_id':razorpay_order['id'] , 'orderId': order.order_id, 'final_price' : order_amount , 'razorpay_merchant_id' : settings.RAZORPAY_ID })
    
    except Order.DoesNotExist:
        return HttpResponse("404 ERROR")

@csrf_exempt
def handler(request):
    if request.method == 'POST':
            payment_id = request.POST.get("razorpay_payment_id" , "") #razorpay is giving us some info
            order_id = request.POST.get("razorpay_order_id" , "") 
            signature = request.POST.get("razorpay_signature" , "")
            params_dict = {"razorpay_order_id" : order_id ,"razorpay_payment_id" :payment_id , "razorpay_signature" : signature}
            order = Order.objects.get(user=request.user , ordered = False) #getting user order model and saving payment_id
            order.razorpay_order_id = order_id
            order.save()
            orderitem = OrderItem.objects.filter(user=request.user , ordered = False)
            try:
                order_db = Order.objects.get(razorpay_order_id = order_id)
                print("Order Has FOund")
            except:
                print("Not Found Order")
                return HttpResponse("505 NOT FOUND")
            order_db.razorpay_payment_id = payment_id
            order_db.razorpay_signature = signature
            order_db.save()
            adr = address.objects.get(user= request.user)
            result = razorpay_client.utility.verify_payment_signature(params_dict) #will verify/matches above field
            if result == True :
                amount = order_db.get_total_price()
                amount = amount * 100 #cause razorpay uses paisa system
                payment_status = razorpay_client.payment.capture(payment_id , amount)
                print("STATSAUYTSA :" , payment_status)
                if payment_status is not None:
                    print(payment_status , " : Status ") # to print out whole payment status
                    order_db.ordered = True #finally ordered = True after receiving payment
                    order_db.save()
                    for items in orderitem: #iterating every items ordered
                        items.ordered = True
                        items.save()
                    return render(request , 'complete.html' ,{'order' : order_db , "pay" : payment_status ,'ad':adr}) #passing for frontend use
                else:
                    order_db.ordered = False
                    order_db.save()
                    return redirect('checkout.html')
            else:
                return HttpResponse("PAYMENT NOT MATCHED!!!")
    else:
        return HttpResponse("OOPS! SOMETHING MISPLACED")


