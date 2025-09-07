from django.db import models
from django.utils import timezone

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, default="")
    price = models.FloatField(default=0)
    subcategory = models.CharField(max_length=100, default="")
    desc = models.CharField(max_length=500)
    pub_date = models.DateField()
    image = models.ImageField(upload_to="shop/images", default="")

    def __str__(self):
        return self.product_name


class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25)
    email = models.CharField(max_length=50, default="")
    message = models.CharField(default=300, max_length=500)

    def __str__(self):
        return self.name


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    items_json = models.CharField(max_length=5000)
    name = models.CharField(max_length=90)
    email = models.CharField(max_length=111)
    phone = models.CharField(max_length=15, default="")
    amount = models.FloatField(default=0)

    address1 = models.CharField(max_length=111, default="")
    address2 = models.CharField(max_length=111, blank=True, null=True)
    city = models.CharField(max_length=111)
    state = models.CharField(max_length=111)
    zip_code = models.CharField(max_length=20)

    def __str__(self):
        return f"Order {self.order_id} by {self.name}"


class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    update_desc = models.CharField(max_length=5000)
    timestamp = models.DateTimeField(default=timezone.now)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='updates'
    )


    def __str__(self):
        return f"Update {self.update_id} for Order {self.order.order_id}"
