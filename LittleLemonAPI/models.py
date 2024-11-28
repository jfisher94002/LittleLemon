from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.title

class MenuItem(models.Model):
	title = models.CharField(max_length=255, db_index=True)
	price = models.DecimalField(max_digits=6, decimal_places=2)
	inventory = models.SmallIntegerField()
	category = models.ForeignKey(Category, on_delete=models.PROTECT, default=1 )
	
	def __str__(self):
		return self.title

class Cart(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	#menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
	#quantity = models.SmallIntegerField()
	#unit_price = models.DecimalField(max_digits=6, decimal_places=2)
	#price = models.DecimalField(max_digits=6, decimal_places=2)	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
 
	class Meta:
		ordering = ('-created_at',)
	#	unique_together = ('menuitem', 'user')
	def __str__(self):
		return f"Cart for {self.user.username}"
  
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        unique_together = ('cart', 'menu_item')

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.title}"

class Order(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	delivery_crew = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_crew', null=True, blank=True)
	status = models.CharField(max_length=50)
	total_price = models.DecimalField(max_digits=6, decimal_places=2)
	date = models.DateField(db_index=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
 
class OrderItem(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
	quantity = models.SmallIntegerField()
	unit_price = models.DecimalField(max_digits=6, decimal_places=2)
	price = models.DecimalField(max_digits=6, decimal_places=2)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
 
	class Meta:
		ordering = ('-created_at',)
		unique_together = ('order', 'menuitem')
 
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem_id =  models.SmallIntegerField()
    rating = models.SmallIntegerField()
