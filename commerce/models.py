from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django_countries.fields import CountryField  


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=300 , unique= True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length= 100 , unique= True)
    category = models.ForeignKey(Category , on_delete= models.CASCADE)
    desc = models.TextField()
    price = models.FloatField(default=0.0)
    product_available= models.IntegerField(default = 1)
    image = models.ImageField(upload_to = 'prods_images/')

    def __str__(self):
        return self.name

    def get_add_to_cart_url(self):
        return reverse('commerce:add_to_cart' , kwargs ={'pk' : self.pk})

class OrderItem(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    product = models.ForeignKey(Product , on_delete=models.CASCADE)
    ordered = models.BooleanField(default = False)
    quantity = models.IntegerField(default = 1 )

    def __str__(self):
        if self.ordered is False:
            return self.user.username + " order's " + self.product.name
        
        elif self.ordered is True:
            return self.user.username + " Paid For " + self.product.name

    def get_total_item_price(self):
        return self.quantity * self.product.price 

    def total_item_price(self):
        return self.get_total_item_price()

class Order(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default = False)
    order_id =  models.CharField(max_length=100 , unique =True , default=None , blank=True, null = True)
    datetime_of_payment = models.DateTimeField(auto_now_add=True)
    order_delivered = models.BooleanField(default = False)
    order_received = models.BooleanField(default = False)
    razorpay_order_id = models.CharField(max_length=500 , blank=True, null = True)
    razorpay_payment_id = models.CharField(max_length=500 , blank=True, null = True)
    razorpay_signature = models.CharField(max_length=500  , blank=True, null = True)

    def save(self , *args, **kwargs):
        if self.order_id is None and self.datetime_of_payment and self.id:
            self.order_id = self.datetime_of_payment.strftime('DNS%Y%m%d') + str(self.razorpay_order_id[-4:]) #DNS20220717ZHqU like this getting last 4 digits of razorpay id
        return super().save(*args, **kwargs)

    def __str__(self):
        if self.razorpay_signature is not None :
            return self.user.username + " --> " + "Status : TO BE DELIVERED"
        
        else:
            return self.user.username + " --> " + "Status : PENDING"

    def get_total_price(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.total_item_price()
        return total

    def get_total_count(self):
        order = Order.objects.get(pk=self.pk)
        return order.items.count()

class address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE )
    country = models.CharField(max_length=110)
    city = models.CharField(max_length=110)
    street_address = models.CharField(max_length=210)
    zip_code = models.CharField(max_length=25)
    phone_no = models.BigIntegerField(unique = True) #to hold more integer value



    def __str__(self):
        return self.user.username + "--" + "Address's"
    


    
