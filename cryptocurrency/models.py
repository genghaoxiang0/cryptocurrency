from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class News(models.Model):
	news_id = models.CharField(max_length=255)
	news_title = models.CharField(max_length=50)
	news_link = models.CharField(max_length=255)
	news_image = models.FileField(blank=True)
	news_content = models.CharField(max_length=10000)
	date_time = models.DateTimeField()
	
	class Meta:
		ordering = ('-date_time',)
	
class Cryptocurrency(models.Model):
	name = models.CharField(max_length=20)
	ticker = models.CharField(max_length=20)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	news = models.ManyToManyField(News, default=None)
	
	def __str__(self):
		return self.ticker + ': ' + str(self.price)

class Watchlist(models.Model):
	user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
	watched = models.ManyToManyField(Cryptocurrency, default=None)

class Position(models.Model):
	user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
	currency = models.ForeignKey(Cryptocurrency, default=None, on_delete=models.PROTECT)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	canSell = models.DecimalField(max_digits=10, decimal_places=2)
	cost = models.DecimalField(max_digits=10, decimal_places=2)
	
class Balance(models.Model):
	user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
	cash = models.DecimalField(max_digits=10, decimal_places=2)
	
	def __str__(self):
		return 'user=' + self.user.username + ',cash=' + str(self.cash)

class Order(models.Model):
	user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
	currency = models.ForeignKey(Cryptocurrency, default=None, on_delete=models.PROTECT)
	order_type = models.CharField(max_length=20)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	date_time = models.DateTimeField()
	
	class Meta:
		ordering = ('date_time',)
	
	def __str__(self):
		return self.user.username + ' ' + self.order_type + ' ' + str(self.amount) + ' ' + self.currency.ticker + ', price=' + str(self.price)

class Transaction(models.Model):
	user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
	currency = models.ForeignKey(Cryptocurrency, default=None, on_delete=models.PROTECT)
	transaction_type = models.CharField(max_length=20)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	date_time = models.DateTimeField()
	
	class Meta:
		ordering = ('-date_time',)
	
	def __str__(self):
		return self.user.username + ' ' + self.transaction_type + ' ' + str(self.amount) + ' ' + self.currency.ticker + ', price=' + str(self.price)

class DepositWithdraw(models.Model):
	user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
	transaction_type = models.CharField(max_length=20)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	date_time = models.DateTimeField()
	
	class Meta:
		ordering = ('-date_time',)
