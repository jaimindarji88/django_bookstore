from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils import timezone
import paypalrestsdk

from models import Book, Cart, BookOrder


def index(request):
    return render(request, 'template.html')


def store(request):
    books = Book.objects.all()
    context = {
        'books': books,
    }

    return render(request, 'base.html', context)


def book_details(request, book_id):
    context = {
        'book': Book.objects.get(pk=book_id)
    }

    return render(request, 'store/detail.html', context=context)

def add_to_cart(request, book_id):
    if request.user.is_authenticated():
        try:
            book = Book.objects.get(pk=book_id)
        except ObjectDoesNotExist:
            pass
        else:
            try:
                cart = Cart.objects.get(user=request.user, active=True)
            except ObjectDoesNotExist:
                cart = Cart.objects.create(
                    user=request.user
                )
                cart.save()
            cart.add_to_cart(book_id)
        return redirect('cart')
    else:
        return redirect('index')

def remove_from_cart(request, book_id):
    if request.user.is_authenticated():
        try:
            book = Book.objects.get(pk=book_id)
        except ObjectDoesNotExist:
            pass
        else:
            cart = Cart.objects.get(user=request.user, active=True)
            cart.remove_from_cart(book_id)
        return redirect('cart')
    else:
        return redirect('index')

def cart(request):
    if request.user.is_authenticated():
        cart = Cart.objects.filter(user=request.user.id, active=True)
        orders = BookOrder.objects.filter(cart=cart)
        total = 0
        count = 0
        for order in orders:
            total += (order.book.price * order.quantity)
            count += order.quantity
        context = {
            'cart': orders,
            'total': total,
            'count': count
        }
        return render(request, 'store/cart.html', context)
    else:
        return redirect('index')

def checkout(request, processor):
    if request.user.is_authenticated():
        cart = Cart.objects.filter(user=request.user.id, active=True)
        orders = BookOrder.objects.filter(cart=cart)
        if processor == 'paypal':
            redirect_url = checkout_paypal(request, cart,orders)
            return redirect(redirect_url)
    else:
        return redirect('index')



# need paypal developer account to get the account_id and account_secret for use with the paypal api
id = '***REMOVED***'
secret = '***REMOVED***'


def checkout_paypal(request, cart, orders):
    if request.user.is_authenticated():
        items = []
        total = 0
        for order in orders:
            total += (order.book.price * order.quantity)
            book = order.book
            item = {
                'name': book.title,
                'sku': book.id,
                'price': str(book.price),
                'quantity': order.quantity,
                'currency': 'USD'
            }
            items.append(item)

        paypalrestsdk.configure({
            'mode': "sandbox",
            "client_id": id,
            'client_secret': secret
        })
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls":{
                "return_url": "http://localhost:8000/store/process/paypal",
                "cancel_url": 'http://localhost:8000/store'
            },
            "transactions":[{
                "item_list":{
                    "items": items
                },
                "amount":{
                    "total": str(total),
                    "currency": "USD"
                },
                "description":"Mystery Books order"
            }]
        })
        if payment.create():
            cart_instance = cart.get()
            cart_instance.payment_id = payment.id
            cart_instance.save()
            for link in payment.links:
                if link.method == 'REDIRECT':
                    redirect_url = str(link.href)
                    return redirect_url
        else:
            return reverse("order_error")
    else:
        return redirect('index')

def order_error(request):
    if request.user.is_authenticated():
        return render(request, 'store/order_error.html')
    else:
        return redirect('index')

def process_order(request, processor):
    if request.user.is_authenticated():
        if processor == 'paypal':
            payment_id = request.GET.get('paymentId')
            cart = Cart.objects.filter(payment_id=payment_id)
            orders = BookOrder.objects.filter(cart=cart)
            total = 0
            for order in orders:
                total += (order.book.price * order.quantity)
                context = {
                    'cart': orders,
                    'total': total
                }
            return render(request, 'store/process_order.html', context)
    else:
        return redirect('index')


def complete_order(request, processor):
    if request.user.is_authenticated():
        cart = Cart.objects.get(user=request.user.id, active=True)
        if processor == 'paypal':
            payment = paypalrestsdk.Payment.find(cart.payment_id)
            if payment.execute({"payer_id": payment.payer.payer_info.payer_id}):
                message = "Success: {0}".format(payment.payer.payer_info.payer_id)
                cart.active = False
                cart.oder_date = timezone.now()
                cart.save()
            else:
                message = "ERROR: {0}".format('error')
            context = {
                'message': message
            }
            return render(request, 'store/order_complete.html', context)
    else:
        return redirect('index')