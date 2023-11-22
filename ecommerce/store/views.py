from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
import datetime
import random
from . utils import cookieCart, cartData, guestOrder

from django.contrib.auth import authenticate, login,logout
from django.shortcuts import render, redirect
from .models import Customer
from django.contrib import messages

# Create your views here.
def store(request):
    is_authenticated = request.user.is_authenticated
    data = cartData(request)
    cartItems = data['cartItems']
    products = Product.objects.all()
    context = {'products':products,'cartItems':cartItems,'is_authenticated': is_authenticated}
    return render(request, 'store/store.html', context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items':items, 'order':order,'cartItems':cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items,'order':order,'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']

	print('Action:', action)
	print('ProductId:', productId)
	
	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer = customer, complete = False)		
	
	orderItem, created = OrderItem.objects.get_or_create(order=order,product=product)
	
	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)
	orderItem.save()
	
	if orderItem.quantity <= 0:
		orderItem.delete()
	
	return JsonResponse('Item was added', safe=False)


def processOrder(request):
	timestamp = datetime.datetime.now().timestamp()
	random_number = random.randint(0, 1000)  # Adjust the range as needed
	transaction_id = f"{timestamp}-{random_number}"
	print(transaction_id)
	data = json.loads(request.body)
	
	if request.user.is_authenticated:
		customer = request.user.customer
		order,created = Order.objects.get_or_create(customer=customer, complete = False)
		
		
	else:
		customer, order = guestOrder(request, data)
  
	total = float(data['form']['total'])
	order.transaction_id = transaction_id
		
	if total ==float(order.get_cart_total):
		order.complete = True
	order.save()
	if order.shipping == True:
			ShippingAddress.objects.create(
				customer=customer,
				order=order,
				address=data['shipping']['address'],
				city=data['shipping']['city'],
				state=data['shipping']['state'],
				zipcode=data['shipping']['zipcode'],
				# country=data['shipping']['country'],
			)
	return JsonResponse('Payment Complete', safe=False)

from django.contrib.auth.hashers import check_password
def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email,password)
        try:
            # Fetch the user based on the username
            user = User.objects.get(email=email)
            
            # Compare the hashed password with the provided password
            if check_password(password, user.password):
                messages.success(request,"Logged in successfully!!")
                login(request,user)
                
                return redirect('store')
	
            else:
                print("Password doesn't match")
                messages.error(request,"Password doesn't match!!!")
                return redirect('signin')
        except User.DoesNotExist:
            print("User doesnt exist")
            messages.error(request,"User doesnt exist!!!!")
            return redirect('signin')
    return render(request, 'store/signin.html')


# def signin(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')
        
#         try:
#             # Fetch the user based on the username
#             user = User.objects.get(email=email)
            
#             # Check if the provided password matches the user's password
#             if check_password(password, user.password):
#                 login(request, user)
#                 messages.success(request,"Logged in successfully!!")
#                 return redirect('store')
#             else:
#                 print("Password doesn't match")
#                 # Password doesn't match, render template with a message
#                 return render(request, 'signin.html', {'error_message': 'Invalid password'})
        
#         except User.DoesNotExist:
#             print("User doesn't exist")
#             # User doesn't exist, render template with a message
#             return render(request, 'signin.html', {'error_message': 'User does not exist'})

#     return render(request, 'store/signin.html')


def signout(request):
    logout(request)
    messages.success(request,"Logged out successfully!!")
    return redirect('store')