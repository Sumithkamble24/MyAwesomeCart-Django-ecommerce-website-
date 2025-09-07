from email.policy import default
from math import ceil
from operator import truediv

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from .models import Product, Contact, Order, OrderUpdate
from django.views.decorators.csrf import csrf_exempt

from .Paytm.Checksum import generate_checksum, verify_checksum
import json
import random
import requests
import time
from django.conf import settings

# Paytm credentials
PAYTM_MID = 'DIY12386817555501617'
MERCHANT_KEY = 'bKMfNxPPf_QdZppa'
PAYTM_WEBSITE = 'WEBSTAGING'
PAYTM_CHANNEL_ID = 'WEB'
PAYTM_INDUSTRY_TYPE_ID = 'Retail'
# PAYTM_CALLBACK_URL = 'http://127.0.0.1:8000/shop/handlerequest/'

# Home Page
def index(request):
    all_products = []
    catprods = Product.objects.values('category', 'product_id')
    cats = {item['category'] for item in catprods}

    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))

        # Chunk products into groups of 4 for carousel
        product_chunks = [prod[i:i+4] for i in range(0, n, 4)]

        all_products.append([cat, product_chunks, range(1, nSlides)])

    context = {"all_products": all_products}
    return render(request, 'shop/index.html', context)


def searchMatch(query, item):
    query = query.lower()
    return query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower()




# Search Page

def search(request):
    query = request.GET.get('search', '').strip()  # Get search text
    allProds = []
    message = ""

    if len(query) >= 2:  # Only search if query length >= 2
        catprods = Product.objects.values('category', 'product_id')
        cats = {item['category'] for item in catprods}

        for cat in cats:
            prodtemp = Product.objects.filter(category=cat)
            prod = [item for item in prodtemp if searchMatch(query, item)]

            if len(prod) != 0:
                n = len(prod)
                nSlides = n // 4 + ceil((n / 4) - (n // 4))
                allProds.append([prod, range(1, nSlides), nSlides])

        if not allProds:
            message = "No products found matching your search."
    else:
        message = "Please enter at least 2 characters to search."

    params = {'allProds': allProds, 'msg': message}
    return render(request, 'shop/search.html', params)






# About Page
def about(request):
    return render(request, 'shop/about.html')

# Contact Page
def contact(request):
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        message = request.POST.get('message', '')
        if name and email and message:
            contact = Contact(name=name, email=email, message=message)
            contact.save()
            return render(request, 'shop/contact.html', {"success": True})
    return render(request, 'shop/contact.html')


@csrf_exempt
def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get("orderId")
        email = request.POST.get("email")

        try:
            order = Order.objects.get(order_id=orderId, email=email)
            updates = OrderUpdate.objects.filter(order=order).order_by("timestamp")

            # Parse items_json (ensure it’s valid JSON)
            try:
                items = json.loads(order.items_json)
            except Exception:
                items = {}

            response = {
                "status": "success",
                "orderDetails": {
                    "orderId": order.order_id,
                    "name": order.name,
                    "email": order.email,
                    "phone": order.phone,
                    "address": f"{order.address1}, {order.address2}, {order.city}, {order.state}, {order.zip_code}",
                    "items": items,   # ✅ send parsed JSON, not raw string
                },
                "updates": [
                    {"text": u.update_desc, "time": u.timestamp.strftime("%Y-%m-%d %H:%M")}
                    for u in updates
                ]
            }
            return JsonResponse(response)

        except Order.DoesNotExist:
            return JsonResponse({"status": "failed", "message": "No order found"})

    return render(request, "shop/tracker.html")


# Product View Page
def prodView(request, myid):
    try:
        product = Product.objects.get(product_id=myid)
    except Product.DoesNotExist:
        product = None
    return render(request, 'shop/prodView.html', {'product': product})



# Checkout Page
def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', "")
        amount = request.POST.get('amount', '')
        name = request.POST.get('name', "")
        email = request.POST.get('email', "")
        address1 = request.POST.get('address1', "")
        address2 = request.POST.get('address2', "")
        city = request.POST.get('city', "")
        state = request.POST.get('state', "")
        zip_code = request.POST.get('zip_code', "")
        phone = request.POST.get('phone', "")




        order = Order(

            items_json=items_json,
            amount=amount,
            name=name,
            email=email,
            address1=address1,
            address2=address2,
            city=city,
            state=state,
            zip_code=zip_code,
            phone=phone,

        )
        order.save()
        update=OrderUpdate(order=order, update_desc="Order has been placed")
        update.save()

        callback_url = f"{settings.PAYTM_CALLBACK_BASE_URL}/shop/handlerequest/"

        param_dict = {
            'MID': PAYTM_MID,
            'ORDER_ID': str(order.order_id),
            'TXN_AMOUNT': str(amount),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID': PAYTM_INDUSTRY_TYPE_ID,
            'WEBSITE': PAYTM_WEBSITE,
            'CHANNEL_ID': PAYTM_CHANNEL_ID,
            'CALLBACK_URL': callback_url,

        }
        param_dict['CHECKSUMHASH'] = generate_checksum(param_dict, MERCHANT_KEY)

        return render(request, "shop/paytm.html", {'param_dict':param_dict})

    return render(request, "shop/checkout.html")


# Handle Paytm Response
@csrf_exempt
def handlerequest(request):
    form = request.POST
    response_dict = {}
    checksum = ""
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict.get('RESPCODE') == '01':
            print('order successful')
        else:
            print('order was not successful because ' + response_dict.get('RESPMSG', 'Unknown error'))

    return render(request, "shop/paymentstatus.html", {'response': response_dict})
