import json
from . models import *

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
        
    print('Cart:',cart)
    items = []
    order ={'get_cart_total':0 ,'get_cart_items':0,'shipping':False}
    cartItems = order['get_cart_items']
    for i in cart:
        try:
            cartItems += cart[i]['quantity']
            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'] )
            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageURL,
                },
                'quantity':cart[i]['quantity'],
                'get_total':total
            }
            items.append(item)
            if product.digital == False:
                order['shipping'] = True
        except:
            pass
    return {'items':items,'order':order,'cartItems':cartItems}


def cartData(request):
    if request.user.is_authenticated :
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
    return {'items':items,'order':order,'cartItems':cartItems}

    
def guestOrder(request, data):
    print('User is not logged in..')
        
    print('COOKIES:', request.COOKIES)
    username = data['form']['username']
    print(username)
    email = data['form']['email']
    print(email)
    lname = data['form']['lname']
    fname = data['form']['fname']
    password = data['form']['password']
    cpassword = data['form']['cpassword']
    cookieData = cookieCart(request)
    items = cookieData['items']
    
    
    
    # user, created = User.objects.get_or_create(
    #     email=email,
    # )
    # user.name = name
    # user.save()
    
    try:
        user = User.objects.get(email=email)
        user.first_name = fname  # Update the user's name
        user.save()  # Save the changes
    except User.DoesNotExist:
   
        user = User.objects.create_user(email=email, username=username,first_name=fname,last_name=lname) #password=password doesnt store or hash password properly.
        user.set_password(password)
        user.save()
    
    customer, created = Customer.objects.get_or_create(
        email=email,user=user,
        )
    customer.name = fname
    customer.password = password
    # customer.user=username      #No chance for user selection as onetoonefield
    customer.save()
    
        
    order = Order.objects.create(
        customer=customer,
        complete=False,
        )
    
    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        
        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity']
            )
        
    return customer, order