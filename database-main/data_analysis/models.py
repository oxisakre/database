from django.db import models

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_number = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.description

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    order_number = models.CharField(max_length=255, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=100, null=True, blank=True, default="None")
    platform = models.CharField(max_length=100, null=True, blank=True, default="None")
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    products = models.ManyToManyField(Product, through='OrderProduct')
    shipping_method = models.CharField(max_length=255, null=True, blank=True, default="None")
    comments = models.TextField(null=True, blank=True)  # Nuevo campo para comentarios
    is_new_customer = models.BooleanField(default=False)  # Nuevo campo para indicar si es un cliente nuevo

    def __str__(self):
        return self.order_number

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    net_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.order.order_number} - {self.product.description}'
