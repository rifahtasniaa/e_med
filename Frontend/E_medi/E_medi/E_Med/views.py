# views.py

import cv2
import numpy as np
import pytesseract
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from django.db.models import Q
from .models import Product, Category, Cart
from .models import CartItem  # Make sure to import the CartItem model

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from .models import DeliveryInfo
from django.db import transaction

from fuzzywuzzy import fuzz

# Set up the path to the Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r'C://Program Files//Tesseract-OCR//tesseract.exe'

def home(request):
    return render(request, 'home.html')

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('product_list')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def user_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Cart.objects.create(user=user)
            messages.success(request, 'Your account has been created successfully. You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def signup_success(request):
    return render(request, 'registration/signup_success.html')

@login_required
def product_list(request):
    query = request.GET.get('q')  # Get the search query from the URL parameters
    ocr_text = request.session.pop('ocr_text', None)  # Retrieve OCR text from session if available

    products = Product.objects.all()

    if query:
        # If a search query is provided, filter the products based on the query (search by name)
        products = products.filter(Q(name__icontains=query))

    return render(request, 'product_list.html', {'products': products, 'scan_prescription': True, 'ocr_text': ocr_text, 'search_query': query})

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})

@login_required
def cart_view(request):
    cart = request.user.cart
    cart_items = cart.cartitem_set.all()

    # Calculate the total price of items in the cart
    total = sum(item.get_total_price() for item in cart_items)

    return render(request, 'cart.html', {'cart': cart, 'cart_items': cart_items, 'total': total})

@login_required
def ocr_scan(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        ocr_text = process_image_ocr(image)
        request.session['ocr_text'] = ocr_text  # Store OCR text in the session
    return redirect('product_list')

def process_image_ocr(image):
    # Convert the uploaded image to OpenCV format
    img = cv2.imdecode(np.fromstring(image.read(), np.uint8), cv2.IMREAD_COLOR)

    # Apply image enhancement techniques here (e.g., unsharp masking, adaptive histogram equalization)
    # Example enhancement applied: unsharp masking
    blurred = cv2.GaussianBlur(img, (0, 0), 10)
    sharpened = cv2.addWeighted(img, 1.5, blurred, -0.5, 0)

    # Crop the region of interest from the improved image
    r = cv2.selectROI(sharpened)
    cropped_image = sharpened[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]

    # Perform OCR using pytesseract on the cropped image
    ocr_text = pytesseract.image_to_string(cropped_image)

    # Close the OpenCV windows after OCR process
    cv2.destroyAllWindows()

    return ocr_text

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    request.user.cart.add_to_cart(product)
    return redirect('product_list')

@login_required
def cart_all(request):
    user_cart = request.user.cart
    cart_items = user_cart.cartitem_set.all()
    for item in cart_items:
        user_cart.remove_from_cart(item.product)
    return redirect('cart_view')

@login_required
def cart_list(request):
    cart = request.user.cart
    cart_items = cart.cartitem_set.all()

    # Calculate the total price of items in the cart
    total = sum(item.get_total_price() for item in cart_items)

    return render(request, 'cart_list.html', {'cart': cart, 'cart_items': cart_items, 'total': total})

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def update_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    action = request.POST.get('action')
    
    if action == 'add':
        request.user.cart.add_to_cart(product)
    elif action == 'remove':
        request.user.cart.remove_from_cart(product)

    return redirect('cart_list')

@login_required
def add_from_ocr(request):
    if request.method == 'POST':
        ocr_text = request.POST.get('ocr_text')
        if ocr_text:
            product_names = ocr_text.strip().split('\n')
            matching_products = []
            for product_name in product_names:
                max_ratio = 0
                best_match = None
                for product in Product.objects.all():
                    ratio = fuzz.token_set_ratio(product_name, product.name)
                    if ratio > max_ratio:
                        max_ratio = ratio
                        best_match = product
                if max_ratio >= 60:  # Adjust the threshold as per your requirement
                    matching_products.append(best_match)

            return render(request, 'ocr_product_list.html', {'products': matching_products})

    return redirect('product_list')



@login_required
def add_selected_to_cart(request):
    if request.method == 'POST':
        selected_product_ids = request.POST.getlist('selected_products')
        selected_products = Product.objects.filter(pk__in=selected_product_ids)
        for product in selected_products:
            request.user.cart.add_to_cart(product)
    return redirect('product_list')

@login_required
def add_all_to_cart(request):
    if request.method == 'POST':
        products = Product.objects.all()
        cart = request.user.cart
        for product in products:
            cart.add_to_cart(product)
    return redirect('cart_list')



@login_required
def buy_products(request):
    # Redirect to the delivery_info page
    return redirect('delivery_info')

@login_required
@transaction.atomic
def delivery_info(request):
    user = request.user
    cart = user.cart
    cart_items = cart.cartitem_set.all()
    delivery_infos = DeliveryInfo.objects.filter(user=user)
    default_info = delivery_infos.filter(is_default=True).first()

   

    if request.method == 'POST':
        # Handle the case when the user submits the delivery information form
        full_name = request.POST['full_name']
        address = request.POST['address']
        city = request.POST['city']
        country = request.POST['country']
        phone_number = request.POST['phone_number']  # Add this line
        email = request.POST['email']  # Add this line

        # Create or update the delivery information for the user
        if default_info:
            default_info.full_name = full_name
            default_info.address = address
            default_info.city = city
            default_info.country = country
            default_info.phone_number = phone_number  # Add this line
            default_info.email = email  # Add this line
            default_info.save()
        else:
            DeliveryInfo.objects.create(user=user, full_name=full_name, address=address, city=city, country=country, phone_number=phone_number, email=email)

        # Handle cart clearing and inventory update
        try:
            with transaction.atomic():
                for item in cart_items:
                    product = item.product

                    # Check if there's enough quantity in inventory
                    if product.quantity >= item.quantity:
                        # Update the inventory quantity
                        product.quantity -= item.quantity
                        product.save()
                    else:
                        # If not enough quantity, raise an exception
                        raise Exception("Not enough quantity in inventory")

                # Clear the cart after a successful purchase
                cart_items.delete()
                messages.success(request, 'Purchase successful. Your cart has been cleared.')

            # Redirect to the payment page
            return redirect('payment')  # Replace 'payment' with the URL name of your payment view

        except Exception as e:
            # If there's an exception (e.g., not enough quantity in inventory), handle it
            messages.error(request, f'Error: {str(e)}')
            return redirect('delivery_info')

    return render(request, 'delivery_info.html', {'default_info': default_info, 'delivery_infos': delivery_infos})

# views.py

@login_required
def edit_delivery_info(request, pk=None):
    user = request.user

    if pk:
        delivery_info = DeliveryInfo.objects.filter(user=user, pk=pk).first()
    else:
        delivery_info = None

    if request.method == 'POST':
        full_name = request.POST['full_name']
        address = request.POST['address']
        city = request.POST['city']
        country = request.POST['country']
        phone_number = request.POST['phone_number']
        email = request.POST['email']

        # Create or update the delivery information for the user
        if delivery_info:
            delivery_info.full_name = full_name
            delivery_info.address = address
            delivery_info.city = city
            delivery_info.country = country
            delivery_info.phone_number = phone_number
            delivery_info.email = email
            delivery_info.save()
        else:
            DeliveryInfo.objects.create(user=user, full_name=full_name, address=address, city=city, country=country, phone_number=phone_number, email=email)

        return redirect('delivery_history')

    return render(request, 'edit_delivery_info.html', {'delivery_info': delivery_info})
@login_required
def delivery_history(request):
    user = request.user
    delivery_infos = DeliveryInfo.objects.filter(user=user).exclude(is_default=True)

    return render(request, 'delivery_history.html', {'delivery_infos': delivery_infos})



@login_required
def select_from_history(request):
    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address_id')
        if selected_address_id:
            selected_address = get_object_or_404(DeliveryInfo, pk=selected_address_id)
            # Store the selected delivery information in the session
            request.session['selected_delivery_info'] = {
                'full_name': selected_address.full_name,
                'address': selected_address.address,
                'city': selected_address.city,
                'country': selected_address.country,
                'phone_number': selected_address.phone_number,
                'email': selected_address.email,
            }
            # Handle cart clearing and inventory update
            try:
                with transaction.atomic():
                    user_cart = request.user.cart
                    cart_items = user_cart.cartitem_set.all()
                    for item in cart_items:
                        product = item.product

                        # Check if there's enough quantity in inventory
                        if product.quantity >= item.quantity:
                            # Update the inventory quantity
                            product.quantity -= item.quantity
                            product.save()
                        else:
                            # If not enough quantity, raise an exception
                            raise Exception("Not enough quantity in inventory")

                    # Clear the cart after a successful purchase
                    cart_items.delete()
                    messages.success(request, 'Purchase successful. Your cart has been cleared.')

                # Redirect to the payment page with a success message
                messages.success(request, 'Purchase successful. Your cart has been cleared.')
                return redirect('payment')  # Replace 'payment' with the URL name of your payment view

            except Exception as e:
                # If there's an exception (e.g., not enough quantity in inventory), handle it
                messages.error(request, f'Error: {str(e)}')
                return redirect('delivery_info')

    return redirect('delivery_info')


@login_required
def payment_view(request):
    # Perform the payment process logic here (e.g., connecting to the payment gateway, making transactions, etc.)
    # For now, let's assume payment was successful and show a simple payment confirmation message.

    # Handle cart clearing and inventory update
    try:
        with transaction.atomic():
            user_cart = request.user.cart
            cart_items = user_cart.cartitem_set.all()
            for item in cart_items:
                product = item.product

                # Check if there's enough quantity in inventory
                if product.quantity >= item.quantity:
                    # Update the inventory quantity
                    product.quantity -= item.quantity
                    product.save()
                else:
                    # If not enough quantity, raise an exception
                    raise Exception("Not enough quantity in inventory")

            # Clear the cart after a successful purchase
            cart_items.delete()

            # Redirect to the payment confirmation page
            return render(request, 'payment.html', {'success_message': 'Purchase successful. Your cart has been cleared.'})

    except Exception as e:
        # If there's an exception (e.g., not enough quantity in inventory), handle it
        messages.error(request, f'Error: {str(e)}')
        return redirect('delivery_info')

@login_required
def remove_delivery_info(request, delivery_info_id):
    user = request.user
    delivery_info = get_object_or_404(DeliveryInfo, pk=delivery_info_id, user=user)

    # Add logic to remove the delivery_info object (e.g., delete it)
    delivery_info.delete()

    # Redirect back to the delivery_info page
    return redirect('delivery_info')  # Replace 'delivery_info' with the actual URL name of your delivery_info view


def send_cash_on_delivery_email(request):
    if request.method == 'POST':
        # You can retrieve the user's email address from the request or user object
        print("Form submitted")  # Print statement for debugging

        user_email = request.session.get('selected_delivery_info', {}).get('email')
        print("User Email:", user_email)
        print("Is User Authenticated:", request.user.is_authenticated)
        # Prepare the context for the email template
        context = {
            'user': request.user,
            'delivery_info': request.session.get('selected_delivery_info', {}),
            'user_email': user_email,  # Add this line
        }

        # Render the email template with the context
        email_html_message = render_to_string('purchase_confirmation_email.html', context)
        email_plain_message = strip_tags(email_html_message)

        # Send the email
        subject = 'Cash on Delivery Confirmation'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user_email]

        try:
            send_mail(subject, email_plain_message, from_email, recipient_list, html_message=email_html_message, fail_silently=False)
            messages.success(request, 'Cash on Delivery confirmation email sent successfully.')
        except Exception as e:
            messages.error(request, f'Error sending email: {str(e)}')

        return redirect('payment_confirmation')  # Redirect to the payment confirmation page

def payment_confirmation(request):
    return render(request, 'payment_confirmation.html')
