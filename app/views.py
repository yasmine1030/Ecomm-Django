from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from .models import *
import datetime
from . utils import cookieCart, cartData, guestOrder
from django.contrib.auth import authenticate, login, logout 
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def registerPage(request):
	if request.user.is_authenticated:
		return redirect('store')
	else:
		form = CreateUserForm()
		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				form.save()
				return redirect('login')
		context = {'form' :form}
		return render(request, 'store/register.html',context)

def loginPage(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect('store')
		else:
			messages.info(request, 'username or password is incorrect')
	context = {}
	return render(request, 'store/login.html', context)
def store(request):
	data = cartData(request)
	carItems = data['carItems']
	products = Product.objects.all()
	context = {'products': products,'carItems':carItems}
	return render(request, 'store/index.html', context)
@login_required(login_url='login')
def cart(request):
	data = cartData(request)
	carItems = data['carItems']
	order = data['order']
	items = data['items']  		
	context = {'items':items, 'order':order, 'carItems':carItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	data = cartData(request)
	carItems = data['carItems']
	order = data['order']
	items = data['items'] 
	context = {'items':items, 'order':order, 'carItems':carItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('action:', action)
	print('productId:', productId)
	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)
	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)
	orderItem.save()
	if orderItem.quantity <= 0:
		orderItem.delete()
	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)
	total = float(data['form']['total'])
	order.transaction_id = transaction_id
	if total == order.get_cart_total:
		order.complete = True
	order.save()
	if order.shipping == True:
		ShippingAdress.objects.create(
			customer=customer,
			order=order,
			adress=data['shipping']['adress'],
			city=data['shipping']['city'],
			state=data['shipping']['state'],
			zipcode=data['shipping']['zipcode'],
		)
	return JsonResponse('Payment subbmitted..',safe=False) 







