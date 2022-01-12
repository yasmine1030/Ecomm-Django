from django.shortcuts import render

def store(request):
	context= {}
	return render(request, 'store/index.html', context)

def cart(request):
	context= {}
	return render(request, 'store/cart.html', context)

def checkout(request):
	context= {}
	return render(request, 'store/home.html', context)
