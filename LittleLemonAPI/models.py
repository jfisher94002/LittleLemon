from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=['price']),
        ]

class Category(models.Model):
	slug = models.SlugField()
	title = models.CharField(max_length=255, db_index=True)

	def __str__(self):
		return self.title

class MenuItem(models.Model):
	title = models.CharField(max_length=255, db_index=True)
	price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
	featured = models.BooleanField(db_index=True)
	category = models.ForeignKey(Category, on_delete=models.PROTECT)
	def __str__(self):
		return self.title

class Cart(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
	quantity = models.SmallIntegerField()
	unit_price = models.DecimalField(max_digits=6, decimal_places=2)
	price = models.DecimalField(max_digits=6, decimal_places=2)	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
 
	class Meta:
		ordering = ('-created_at',)
		unique_together = ('menuitem', 'user')
  
class Order(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	delivery_crew = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='delivery_crew')
	status = models.CharField(max_length=50)
	total = models.DecimalField(max_digits=6, decimal_places=2)
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
 