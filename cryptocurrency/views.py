from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from cryptocurrency.forms import *
from django.utils import timezone
from cryptocurrency.models import *
import json
from decimal import *
import datetime

coinName = {}
coinName['BTC'] = 'Bitcoin'
coinName['ETH'] = 'Ethereum'
coinName['LTC'] = 'Litecoin'
coinName['DOGE'] = 'Dogecoin'
coinName['LINK'] = 'Chainlink'
coinName['ETC'] = 'Ethereum Classic'
coinName['EXMR'] = 'EXMRFDN'
coinName['USDT'] = 'Tether'
coinName['ZEC'] = 'Zcash'
coinName['DASH'] = 'Dash'
coinName['BCH'] = 'Bitcoin Cash'
coinName['ADA'] = 'Cardano'
coinName['MKR'] = 'Maker'
coinName['NMR'] = 'Numeraire'
coinName['KNC'] = 'Kyber Network'
coinName['ZRX'] = 'Ox'
coinName['DAI'] = 'Dai'
coinName['SOLVE'] = 'SOLVE'
coinName['LOOM'] = 'Loom Network'

# Create your views here.
@login_required
def home_action(request):
	myBalance = Balance.objects.filter(user=request.user)
	if not myBalance:
		newBalance = Balance(user = request.user, cash = 0)
		newBalance.save()
	myWatchlist = Watchlist.objects.filter(user=request.user)
	if not myWatchlist:
		newWatchList = Watchlist(user = request.user)
		newWatchList.save()
	context = {}
	context['coins'] = Cryptocurrency.objects.all()
	news = News.objects.all()
	if len(news) > 20:
		news = news[:20]
	context['news'] = news
	if request.method == 'GET':
		return render(request, 'home.html', context)
	return render(request, 'home.html', context)

@login_required
def cryptocurrency_action(request, ticker):
	context = {}
	context['ticker'] = ticker
	coin = get_object_or_404(Cryptocurrency, ticker=ticker)
	context['coin'] = coin
	context['name'] = coin.name
	context['price'] = coin.price
	position = Position.objects.filter(user=request.user, currency=coin)
	if not position:
		newPosition = Position(user=request.user, currency=coin, amount=Decimal(0), canSell=Decimal(0), cost=Decimal(0))
		newPosition.save()
		position = Position.objects.filter(user=request.user, currency=coin)
	if position:
		context['hold'] = position[0].amount
		context['canSell'] = position[0].canSell
		context['cost'] = position[0].cost
	else:
		context['hold'] = 0
		context['canSell'] = 0
		context['cost'] = 0
	mybalance = get_object_or_404(Balance, user=request.user)
	context['cash'] = mybalance.cash
	topBuy = Order.objects.filter(currency=coin, order_type='Buy').order_by('-price')
	if len(topBuy) > 5:
		topBuy = topBuy[:5]
	context['topBuy'] = topBuy
	topSell = Order.objects.filter(currency=coin, order_type='Sell').order_by('price')
	if len(topSell) > 5:
		topSell = topSell[:5]
	context['topSell'] = topSell
	watchList = get_object_or_404(Watchlist, user=request.user)
	context['watchList'] = watchList
	if request.method == 'GET':
		return render(request, 'cryptocurrency.html', context)
	if 'quantity' not in request.POST or not request.POST['quantity']:
		return render(request, 'cryptocurrency.html', context)
	if 'Buy' in request.POST.get('type'):
		moneyAmount = Decimal(request.POST['quantity']) * coin.price
		if moneyAmount > mybalance.cash:
			context['error'] = "Sorry, your credit is running low."
			return render(request, 'cryptocurrency.html', context)
		if Decimal(request.POST['quantity']) > 10000000 or Decimal(request.POST['quantity']) + Decimal(context['hold']) > 10000000:
			context['error'] = "Sorry, you cannot hold more than 10000000 coins."
			return render(request, 'cryptocurrency.html', context)
		if Decimal(request.POST['moneyAmount']) == Decimal(0):
			context['error'] = "Sorry, amount of money must larger than 0."
			return render(request, 'cryptocurrency.html', context)
		sellList = Order.objects.filter(currency=coin, order_type='Sell', price__lte=coin.price, amount=Decimal(request.POST['quantity'])).filter().filter(~Q(user=request.user))
		if sellList:
			sellOrder = sellList[0]
			sellerBalance = get_object_or_404(Balance, user=sellOrder.user)
			sellerBalance.cash += sellOrder.price * sellOrder.amount
			sellerBalance.save()
			sellerPosition = get_object_or_404(Position, user=sellOrder.user, currency=coin)
			sellerPosition.amount -= sellOrder.amount
			sellerPosition.save()
			newTransaction = Transaction(user=sellOrder.user, currency=coin, transaction_type='Sell', price=sellOrder.price, amount=sellOrder.amount, date_time = timezone.now())
			newTransaction.save()
			sellOrder.delete()
			mybalance.cash -= moneyAmount
			mybalance.save()
			context['cash'] = mybalance.cash.quantize(Decimal('0.00'))
			position = Position.objects.filter(user=request.user, currency=coin)
			if position:
				totalCost = position[0].cost * position[0].amount
				newTotalCost = totalCost + moneyAmount
				position[0].amount += Decimal(request.POST['quantity'])
				position[0].canSell += Decimal(request.POST['quantity'])
				position[0].save()
				position[0].cost = newTotalCost / position[0].amount
				position[0].save()
				context['hold'] = position[0].amount
				context['canSell'] = position[0].canSell
				context['cost'] = position[0].cost.quantize(Decimal('0.00'))
			else:
				newPosition = Position(user=request.user, currency=coin, amount=Decimal(request.POST['quantity']), canSell=Decimal(request.POST['quantity']), cost=Decimal(request.POST['moneyAmount'])/Decimal(request.POST['quantity']))
				newPosition.save()
				context['hold'] = newPosition.amount
				context['canSell'] = newPosition.canSell
				context['cost'] = newPosition.cost.quantize(Decimal('0.00'))
			newTransaction = Transaction(user=request.user, currency=coin, transaction_type='Buy', price=coin.price, amount=Decimal(request.POST['quantity']), date_time = timezone.now())
			newTransaction.save()
		else:
			mybalance.cash -= moneyAmount
			mybalance.save()
			newOrder = Order(user=request.user, currency=coin, order_type='Buy', price=coin.price, amount=Decimal(request.POST['quantity']), date_time = timezone.now())
			newOrder.save()
			context['cash'] = mybalance.cash.quantize(Decimal('0.00'))
		topBuy = Order.objects.filter(currency=coin, order_type='Buy').order_by('-price')
		if len(topBuy) > 5:
			topBuy = topBuy[:5]
		context['topBuy'] = topBuy
		topSell = Order.objects.filter(currency=coin, order_type='Sell').order_by('price')
		if len(topSell) > 5:
			topSell = topSell[:5]
		context['topSell'] = topSell
	else:
		moneyAmount = Decimal(request.POST['quantity']) * coin.price
		position = Position.objects.filter(user=request.user, currency=coin)
		if position:
			if Decimal(request.POST['quantity']) > position[0].canSell:
				context['error'] = "Sorry, your don't have enough cryptocurrency."
				return render(request, 'cryptocurrency.html', context)
		else:
			context['error'] = "Sorry, your don't have enough cryptocurrency."
			return render(request, 'cryptocurrency.html', context)
		buyList = Order.objects.filter(currency=coin, order_type='Buy', price__gte=coin.price, amount=Decimal(request.POST['quantity'])).filter(~Q(user=request.user))
		if buyList:
			mybalance.cash += moneyAmount
			mybalance.save()
			context['cash'] = mybalance.cash.quantize(Decimal('0.00'))
			buyOrder = buyList[0]
			buyerPosition = get_object_or_404(Position, user=buyOrder.user, currency=coin)
			totalCost = buyerPosition.cost * buyerPosition.amount
			newTotalCost = totalCost + buyOrder.price * buyOrder.amount
			buyerPosition.amount += buyOrder.amount
			buyerPosition.canSell += buyOrder.amount
			buyerPosition.save()
			buyerPosition.cost = newTotalCost / buyerPosition.amount
			buyerPosition.save()
			newTransaction = Transaction(user=buyOrder.user, currency=coin, transaction_type='Buy', price=buyOrder.price, amount=buyOrder.amount, date_time = timezone.now())
			newTransaction.save()
			buyOrder.delete()
			position = get_object_or_404(Position, user=request.user, currency=coin)
			position.amount -= Decimal(request.POST['quantity'])
			position.canSell -= Decimal(request.POST['quantity'])
			position.save()
			if position.amount == 0:
				position.cost = Decimal(0)
				position.save()
			context['hold'] = position.amount
			context['canSell'] = position.canSell
			context['cost'] = position.cost.quantize(Decimal('0.00'))
			newTransaction = Transaction(user=request.user, currency=coin, transaction_type='Sell', price=coin.price, amount=Decimal(request.POST['quantity']), date_time = timezone.now())
			newTransaction.save()
		else:
			newOrder = Order(user=request.user, currency=coin, order_type='Sell', price=coin.price, amount=Decimal(request.POST['quantity']), date_time = timezone.now())
			newOrder.save()
			position = get_object_or_404(Position, user=request.user, currency=coin)
			position.canSell -= Decimal(request.POST['quantity'])
			position.save()
			context['canSell'] = position.canSell
			context['cost'] = position.cost.quantize(Decimal('0.00'))
		topBuy = Order.objects.filter(currency=coin, order_type='Buy').order_by('-price')
		if len(topBuy) > 5:
			topBuy = topBuy[:5]
		context['topBuy'] = topBuy
		topSell = Order.objects.filter(currency=coin, order_type='Sell').order_by('price')
		if len(topSell) > 5:
			topSell = topSell[:5]
		context['topSell'] = topSell
	return render(request, 'cryptocurrency.html', context)

@login_required
def back_door_action(request, ticker):
	context = {}
	context['ticker'] = ticker
	coin = get_object_or_404(Cryptocurrency, ticker=ticker)
	context['price'] = coin.price
	position = Position.objects.filter(user=request.user, currency=coin)
	if position:
		context['hold'] = position[0].amount
		context['cost'] = position[0].cost
	else:
		context['hold'] = 0
		context['cost'] = 0
	mybalance = get_object_or_404(Balance, user=request.user)
	context['cash'] = mybalance.cash
	if request.method == 'GET':
		return render(request, 'back_door.html', context)
	if 'Buy' in request.POST.get('type'):
		if Decimal(request.POST['moneyAmount']) > mybalance.cash:
			context['error'] = "Sorry, your credit is running low."
			return render(request, 'back_door.html', context)
		mybalance.cash -= Decimal(request.POST['moneyAmount'])
		mybalance.save()
		context['cash'] = mybalance.cash.quantize(Decimal('0.00'))
		position = Position.objects.filter(user=request.user, currency=coin)
		if position:
			totalCost = position[0].cost * position[0].amount
			newTotalCost = totalCost + Decimal(request.POST['moneyAmount'])
			position[0].amount += Decimal(request.POST['quantity'])
			position[0].canSell += Decimal(request.POST['quantity'])
			position[0].save()
			position[0].cost = newTotalCost / position[0].amount
			position[0].save()
			context['hold'] = position[0].amount
			context['cost'] = position[0].cost.quantize(Decimal('0.00'))
		else:
			newPosition = Position(user=request.user, currency=coin, amount=Decimal(request.POST['quantity']), canSell=Decimal(request.POST['quantity']), cost=Decimal(request.POST['moneyAmount'])/Decimal(request.POST['quantity']))
			newPosition.save()
			context['hold'] = newPosition.amount
			context['cost'] = newPosition.cost.quantize(Decimal('0.00'))
	else:
		position = Position.objects.filter(user=request.user, currency=coin)
		if position:
			if Decimal(request.POST['quantity']) > position[0].amount:
				context['error'] = "Sorry, your don't have enough cryptocurrency."
				return render(request, 'back_door.html', context)
		else:
			context['error'] = "Sorry, your don't have enough cryptocurrency."
			return render(request, 'back_door.html', context)
		mybalance.cash += Decimal(request.POST['moneyAmount'])
		mybalance.save()
		context['cash'] = mybalance.cash.quantize(Decimal('0.00'))
		position = get_object_or_404(Position, user=request.user, currency=coin)
		position.amount -= Decimal(request.POST['quantity'])
		position.save()
		if position.amount == 0:
			position.cost = 0
			position.save()
		context['hold'] = position.amount
		context['cost'] = position.cost.quantize(Decimal('0.00'))
	return render(request, 'back_door.html', context)

@login_required
def watchlist_action(request):
	context = {}
	watchlist = get_object_or_404(Watchlist, user=request.user)
	context['coins'] = []
	context['news'] = []
	for item in Cryptocurrency.objects.all():
		if item in watchlist.watched.all():
			context['coins'].append(item)
			context['news'] += item.news.all()[0:5]
	if request.method == 'GET':
		return render(request, 'watchlist.html', context)
	return render(request, 'watchlist.html', context)

@login_required
def deposit_action(request):
	context = {}
	mybalance = get_object_or_404(Balance, user=request.user)
	context['cash'] = mybalance.cash
	context['depositWithdraw'] = DepositWithdraw.objects.all()
	if request.method == 'GET':
		return render(request, 'deposit.html', context)
	if 'amount' not in request.POST or not request.POST['amount']:
		return render(request, 'deposit.html', context)
	if 'Deposit' in request.POST.get('type'):
		if int(request.POST['amount']) > 1000000:
			context['error'] = "Sorry, the limit for each deposit is 1000000."
			return render(request, 'deposit.html', context)
		if int(request.POST['amount']) + int(mybalance.cash) > 100000000:
			context['error'] = "Sorry, your deposit is too high."
			return render(request, 'deposit.html', context)
		mybalance.cash += int(request.POST['amount'])
		mybalance.save()
		context['cash'] = mybalance.cash
		newRecord = DepositWithdraw(user = request.user, transaction_type = 'Deposit', amount = int(request.POST['amount']), date_time = timezone.now())
		newRecord.save()
		context['depositWithdraw'] = DepositWithdraw.objects.all()
	else:
		if int(request.POST['amount']) > mybalance.cash:
			context['error'] = "Sorry, your credit is running low."
			return render(request, 'deposit.html', context)
		mybalance.cash -= int(request.POST['amount'])
		mybalance.save()
		context['cash'] = mybalance.cash
		newRecord = DepositWithdraw(user = request.user, transaction_type = 'Withdraw', amount = int(request.POST['amount']), date_time = timezone.now())
		newRecord.save()
		context['depositWithdraw'] = DepositWithdraw.objects.all()
	return render(request, 'deposit.html', context)

@login_required
def history_action(request):
	context = {}
	myTransactions = Transaction.objects.filter(user = request.user)
	context['transactions'] = myTransactions
	if request.method == 'GET':
		return render(request, 'history.html', context)
	return render(request, 'history.html', context)

@login_required
def update_price(request):
	if request.method != 'POST':
		return _my_json_error_response("You must use a POST request", status=404)
	coin = Cryptocurrency.objects.filter(ticker = request.POST['ticker'])
	if coin:
		coin[0].price = request.POST['price']
		coin[0].save()
	else:
		newcoin = Cryptocurrency(name=coinName[request.POST['ticker']], ticker=request.POST['ticker'], price=request.POST['price'])
		newcoin.save()
	return HttpResponse()

@login_required
def update_news(request):
	if request.method != 'POST':
		return _my_json_error_response("You must use a POST request", status=404)
	article = News.objects.filter(news_id = request.POST['news_id'])

	if article:
		pass
	else:
		s =  request.POST['news_time']
		t =  datetime.datetime.fromtimestamp(float(s)/1000.)
		newArticle = News(news_id=request.POST['news_id'], news_title=request.POST['news_title'], news_link=request.POST['news_link'], news_image=request.POST['news_image'], news_content=request.POST['news_body'], date_time=t)
		newArticle.save()

	coin = Cryptocurrency.objects.filter(ticker = request.POST['ticker'])
	if  coin:
		coin[0].news.add(News.objects.get(news_id = request.POST['news_id']))
	return HttpResponse()

@login_required
def balance_and_position_action(request):
	context = {}
	positions = Position.objects.filter(user=request.user)
	context['positions'] = positions
	totalValue = Decimal(0)
	for position in positions:
		if position.amount > 0:
			totalValue += position.amount * position.currency.price
	context['totalValue'] = totalValue.quantize(Decimal('0.00'))
	orders = Order.objects.filter(user=request.user)
	context['orders'] = orders
	if request.method == 'GET':
		return render(request, 'balance_and_position.html', context)
	try:
		cancelledOrder = Order.objects.get(id=int(request.POST['button']))
	except:
		context['error'] = 'This transaction is already completed'
		return render(request, 'balance_and_position.html', context)
	if cancelledOrder.user != request.user:
		return render(request, 'balance_and_position.html', context)
	if cancelledOrder.order_type == 'Buy':
		myBalance = Balance.objects.get(user=request.user)
		myBalance.cash += cancelledOrder.price * cancelledOrder.amount
		myBalance.cash = myBalance.cash.quantize(Decimal('0.00'))
		myBalance.save()
		cancelledOrder.delete()
	else:
		myPosition = Position.objects.get(user=request.user, currency=cancelledOrder.currency)
		myPosition.canSell += cancelledOrder.amount
		myPosition.save()
		cancelledOrder.delete()
	return render(request, 'balance_and_position.html', context)

@login_required
def watch_action(request, ticker):
	context = {}
	context['ticker'] = ticker
	coin = get_object_or_404(Cryptocurrency, ticker=ticker)
	context['coin'] = coin
	context['name'] = coin.name
	context['price'] = coin.price
	position = Position.objects.filter(user=request.user, currency=coin)
	if position:
		context['hold'] = position[0].amount
		context['canSell'] = position[0].canSell
		context['cost'] = position[0].cost
	else:
		context['hold'] = 0
		context['canSell'] = 0
		context['cost'] = 0
	mybalance = get_object_or_404(Balance, user=request.user)
	context['cash'] = mybalance.cash
	topBuy = Order.objects.filter(currency=coin, order_type='Buy').order_by('-price')
	if len(topBuy) > 5:
		topBuy = topBuy[:5]
	context['topBuy'] = topBuy
	topSell = Order.objects.filter(currency=coin, order_type='Sell').order_by('price')
	if len(topSell) > 5:
		topSell = topSell[:5]
	context['topSell'] = topSell
	watchList = get_object_or_404(Watchlist, user=request.user)
	watchList.watched.add(coin)
	context['watchList'] = watchList
	return render(request, 'cryptocurrency.html', context)

@login_required
def unwatch_action(request, ticker):
	context = {}
	context['ticker'] = ticker
	coin = get_object_or_404(Cryptocurrency, ticker=ticker)
	context['coin'] = coin
	context['name'] = coin.name
	context['price'] = coin.price
	position = Position.objects.filter(user=request.user, currency=coin)
	if position:
		context['hold'] = position[0].amount
		context['canSell'] = position[0].canSell
		context['cost'] = position[0].cost
	else:
		context['hold'] = 0
		context['canSell'] = 0
		context['cost'] = 0
	mybalance = get_object_or_404(Balance, user=request.user)
	context['cash'] = mybalance.cash
	topBuy = Order.objects.filter(currency=coin, order_type='Buy').order_by('-price')
	if len(topBuy) > 5:
		topBuy = topBuy[:5]
	context['topBuy'] = topBuy
	topSell = Order.objects.filter(currency=coin, order_type='Sell').order_by('price')
	if len(topSell) > 5:
		topSell = topSell[:5]
	context['topSell'] = topSell
	watchList = get_object_or_404(Watchlist, user=request.user)
	watchList.watched.remove(coin)
	context['watchList'] = watchList
	return render(request, 'cryptocurrency.html', context)

@login_required
def search_action(request):
	context = {}
	context['coins'] = []
	if 'searchContent' not in request.POST:
		return render(request, 'search.html', context)
	for item in Cryptocurrency.objects.all():
		if request.POST['searchContent'].upper() in item.name.upper() or request.POST['searchContent'].upper() in item.ticker:
			context['coins'].append(item)
	if request.method == 'GET':
		return render(request, 'search.html', context)
	return render(request, 'search.html', context)
