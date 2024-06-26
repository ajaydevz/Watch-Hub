import random
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import CustomUser, UserWallet
from wishlist.models import WishlistItem
from userprofile.models import Address
from store.models import Product, Variation, Coupon
from cart.models import Cart, CartItem, Order, OrderItem
from django.utils import timezone
from django.http import HttpResponseBadRequest
from django.views.decorators.cache import cache_control
from django.views.decorators.cache import never_cache

# Create your views here.
def cart_page(request):
    if "useremail" not in request.session:
        return redirect("user_login")
    tax = 0
    grand_total = 0
    total = 0
    quantity = 0
    cart_items = None

    if "useremail" in request.session:
        email = request.session["useremail"]
        user = CustomUser.objects.get(email=email)

    cart_id = _cart_id(request)  # get or generate the cart_id
    try:
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by("id")
        for cart_item in cart_items:
            total += cart_item.product.selling_price * cart_item.quantity
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "tax": tax,
        "grand_total": grand_total,
    }
    # print(cart_items.product.product_name)
    return render(request, "cart/cart.html", context)


def _cart_id(request):
    cart = request.session.session_key

    if not cart:
        cart = request.session.create()
    return cart


@login_required(login_url="user_login")
def add_cart(request, product_id):
    print("add cart from wishlist is working")
    if "useremail" in request.session:
        email = request.session["useremail"]
        user = CustomUser.objects.get(email=email)

    variant = Variation.objects.get(id=product_id)  # get the product variation
    print(variant.stock)
    if variant.stock == 0:
        print(variant.stock)
        messages.error(request, "sorry the product is out of stock")
        return redirect("product_details", variant_id=variant.id)
    # if product.stock is None:
    #     return redirect('view_shop')
    is_exist = WishlistItem.objects.filter(user=user, product_name=variant).exists()

    if is_exist:
        wishlist_item = WishlistItem.objects.get(user=user, product_name=variant)
        wishlist_item.delete()
        # return redirect('shop_page')
    else:
        pass

    cart_id = _cart_id(request)

    try:
        cart = Cart.objects.get(
            user=user
        )  # get the cart using cart_id present in the session

    except Cart.DoesNotExist:
        if "useremail" in request.session:
            email = request.session["useremail"]
        user = CustomUser.objects.get(email=email)
        if user is not None:
            cart = Cart.objects.create(cart_id=_cart_id(request), user=user)
            cart.save()

    try:
        cart_item = CartItem.objects.get(product=variant, cart=cart)
        if variant.stock <= cart_item.quantity:
            messages.error(request, "stock limit of the product reached")
            return redirect("cart_page")
        else:
            cart_item.quantity += 1
            cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=variant,
            quantity=1,
            cart=cart,
        )
        cart_item.save()
    return redirect("cart_page")


def increment_cartitem(request, product_id):
    if request.user:
        print("hi this is working perfectly")
        user = request.user
    try:
        cart = Cart.objects.get(user=user)
        print("this is also working perfectly")
    except:
        print("this is not working perfectly")
    product = get_object_or_404(Variation, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)

    if cart_item.quantity < product.stock:
        cart_item.quantity = cart_item.quantity + 1
        quantity = cart_item.quantity
        cart_item_total = product.selling_price * quantity
        cart_item.save()

        total = 0
        try:
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by(
                "id"
            )
            for cart_item in cart_items:
                total += cart_item.product.selling_price * cart_item.quantity
                # quantity += cart_item.quantity
            tax = (2 * total) / 100
            grand_total = total + tax
        except ObjectDoesNotExist:
            pass
        return JsonResponse(
            {
                "quantity": quantity,
                "cart_item_total": cart_item_total,
                "total": total,
                "tax": tax,
                "grand_total": grand_total,
                "messages": "success",
            }
        )

    else:
        quantity = cart_item.quantity
        cart_item_total = product.selling_price * quantity
        cart_item.save()

        total = 0
        try:
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by(
                "id"
            )
            for cart_item in cart_items:
                total += cart_item.product.selling_price * cart_item.quantity
                # quantity += cart_item.quantity
            tax = (2 * total) / 100
            grand_total = total + tax
        except ObjectDoesNotExist:
            pass
        return JsonResponse(
            {
                "quantity": quantity,
                "cart_item_total": cart_item_total,
                "total": total,
                "tax": tax,
                "grand_total": grand_total,
                "messages": "error",
            }
        )


def decrement_cartitem(request, product_id):
    if "useremail" in request.session:
        email = request.session["useremail"]
        user = CustomUser.objects.get(email=email)

    cart = Cart.objects.get(user=user)
    product = get_object_or_404(Variation, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        quantity = cart_item.quantity
        cart_item_total = product.selling_price * quantity
        cart_item.save()
        total = 0
        try:
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by(
                "id"
            )
            for cart_item in cart_items:
                total += cart_item.product.selling_price * cart_item.quantity
                # quantity += cart_item.quantity
            tax = (2 * total) / 100
            grand_total = total + tax
        except ObjectDoesNotExist:
            pass
        return JsonResponse(
            {
                "quantity": quantity,
                "cart_item_total": cart_item_total,
                "total": total,
                "tax": tax,
                "grand_total": grand_total,
                "status": "success",
            }
        )

    else:
        quantity = cart_item.quantity
        cart_item_total = product.selling_price * quantity
        cart_item.delete()
        total = 0
        try:
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by(
                "id"
            )
            for cart_item in cart_items:
                total += cart_item.product.selling_price * cart_item.quantity
                # quantity += cart_item.quantity
            tax = (2 * total) / 100
            grand_total = total + tax
        except ObjectDoesNotExist:
            pass
        return JsonResponse(
            {
                "quantity": quantity,
                "cart_item_total": cart_item_total,
                "total": total,
                "tax": tax,
                "grand_total": grand_total,
                "status": "error",
            }
        )
        # cart_item.delete()

    # return redirect('cart_page')


def remove_cart_item(request, product_id):
    if "useremail" in request.session:
        email = request.session["useremail"]
        user = CustomUser.objects.get(email=email)

    cart = Cart.objects.get(user=user)
    product = get_object_or_404(Variation, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)

    cart_item.delete()

    return redirect("cart_page")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def checkout_page(request):
    if request.method == "POST":
        if "useremail" in request.session:
            email = request.session[
                "useremail"
            ]  # getting the email of the user from the session
            user = CustomUser.objects.get(email=email)
            wallet = user.wallet
            user_id = user.id

            selected_address_id = request.POST.get("selectedAddress")

            print(selected_address_id)
            print(selected_address_id)
            print(selected_address_id)
            if selected_address_id is None:
                # default_address=Address.objects.get(user_id=user_id,is_default=True)
                # selected_address_id=default_address.id
                messages.error(request, "Please select an address first!!")
                return redirect("address_checkout")

            print(selected_address_id)
            address = Address.objects.get(
                id=selected_address_id
            )  # using the user id getting all addresses associated with that user

            tax = 0
            quantity = 0
            cart_items = None
            grand_total = 0
            total = 0
            coupons = None
            cart_id = _cart_id(request)  # get or generate the cart_id
            try:
                print(".........")
                cart = Cart.objects.get(user=user)
                cart_items = CartItem.objects.filter(cart=cart, is_active=True)
                for cart_item in cart_items:
                    total += cart_item.product.selling_price * cart_item.quantity
                    quantity += cart_item.quantity
                tax = (2 * total) / 100
                grand_total = total + tax

                # Get today's date
                today = timezone.now().date()
                coupons = Coupon.objects.filter(
                    minimum_amount__lte=grand_total,
                    valid_to__gte=today,
                    is_available=True,
                )

            except ObjectDoesNotExist:
                print(".......///////////////////////////")
                pass

            context = {
                "coupons": coupons,
                "address": address,
                "tax": tax,
                "grand_total": grand_total,
                "quantity": quantity,
                "cart_items": cart_items,
                "total": total,
                "wallet": wallet,
            }

            return render(request, "cart/checkout.html", context)
    else:
        email = request.session[
            "useremail"
        ]  # getting the email of the user from the session
        user = CustomUser.objects.get(email=email)
        user_id = user.id
        tax = 0
        quantity = 0
        cart_items = None
        grand_total = 0
        total = 0
        coupons = None
        cart_id = _cart_id(request)  # get or generate the cart_id
        try:
            print("aaaaaaaaaaaaaaaa")
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            for cart_item in cart_items:
                total += cart_item.product.selling_price * cart_item.quantity
                quantity += cart_item.quantity
            tax = (2 * total) / 100
            grand_total = total + tax
            coupons = Coupon.objects.filter(minimum_amount__lte=grand_total)
            print("bbbbbbbbbbbbb")
        except ObjectDoesNotExist:
            print("cccccccccccccccccc")
            pass

        context = {
            "coupons": coupons,
            "tax": tax,
            "grand_total": grand_total,
            "quantity": quantity,
            "cart_items": cart_items,
            "total": total,
            "wallet": wallet,
        }

        return render(request, "cart/checkout.html", context)


def address_checkout(request):
    if "useremail" in request.session:
        email = request.session["useremail"]
        user = CustomUser.objects.get(email=email)
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        # Check if the quantity in the cart is greater than available stock
        for cart_item in cart_items:
            orderproduct = Variation.objects.filter(id=cart_item.product.id).first()

            if cart_item.quantity > orderproduct.stock:
                # Display a message to the user
                messages.error(
                    request,
                    f"Sorry, only {orderproduct.stock} quantity of {orderproduct.product.product_name} is available.",
                )

                # Redirect the user to the cart or any other appropriate page
                return redirect(
                    "cart_page"
                )  # Replace 'cart' with the actual URL name of your cart page

        # Proceed to address selection logic
        address = Address.objects.filter(user_id=user.id, is_default=False)

        for i in address:
            print(i.recipient_name)

        try:
            default_address = Address.objects.get(user_id=user.id, is_default=True)
        except Address.DoesNotExist:
            default_address = None

        context = {
            "address": address,
            "default_address": default_address,
        }

        return render(request, "cart/address_selection.html", context)


def add_address_checkout(request, user_id):
    if request.method == "POST":
        if request.user:
            customer = request.user

        house_no = request.POST.get("house_no")
        recipient_name = request.POST.get("RecipientName")
        street_name = request.POST.get("street_name")
        village_name = request.POST.get("Village")
        postal_code = request.POST.get("postal_code")
        district = request.POST.get("district")
        state = request.POST.get("state")
        country = request.POST.get("country")

        try:
            recipient_name_checking = Address.objects.get(recipient_name=recipient_name)
        except Address.DoesNotExist:
            recipient_name_checking = None

        if recipient_name_checking:
            print("recipient name checking is working and its fine")
            messages.error(
                request, "An address with this recipient name already exists."
            )
            return redirect("address_checkout")

        # Check the quantity in the cart against the available stock
        cart = Cart.objects.get(user=customer)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            orderproduct = Variation.objects.filter(id=cart_item.product.id).first()

            if cart_item.quantity > orderproduct.stock:
                # Display a message to the user
                messages.error(
                    request,
                    f"Sorry, only {orderproduct.stock} quantity of {orderproduct.product.product_name} is available.",
                )

                # Redirect the user to the cart or any other appropriate page
                return redirect(
                    "cart"
                )  # Replace 'cart' with the actual URL name of your cart page

        # Proceed to add the address logic
        address = Address(
            user_id=customer,
            house_no=house_no,
            recipient_name=recipient_name,
            street_name=street_name,
            village_name=village_name,
            postal_code=postal_code,
            district=district,
            state=state,
            country=country,
        )

        address_exists = Address.objects.filter(user_id=customer).exists()

        if not address_exists:
            address.is_default = True

        address.save()
        return redirect("address_checkout")


def place_order(request):

    print(request.POST)
    if request.method == "POST":
        email = request.session["useremail"]
        user = CustomUser.objects.get(email=email)

        # the coupen id is taking from the dict request.POST.get or the request.POST['name']
        coupen_id = request.POST.get("coupen_id")
        # get the object
        if coupen_id:
            try:
                # Try to get the Coupon object
                coupen_id = Coupon.objects.get(id=coupen_id)
            except Coupon.DoesNotExist:
                # Handle the case where the Coupon object is not found
                return HttpResponseBadRequest("Coupon not found")
        else:
            # Handle the case where coupen_id is not provided
            coupen_id = None  # You can set it to None or any default value

        

        selected_address_id = request.POST.get("selected_address")

        address = Address.objects.get(id=selected_address_id)

        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            orderproduct = Variation.objects.filter(id=cart_item.product.id).first()

            if cart_item.quantity > orderproduct.stock:
                # Display a message to the user
                messages.error(
                    request,
                    f"Sorry, only {orderproduct.stock} quantity of {orderproduct.product.product_name} is available.",
                )

                # Redirect the user to the cart or any other appropriate page
                return redirect(
                    "cart_page"
                )  # Replace 'cart' with the actual URL name of your cart page

        order = Order()
        order.user = user
        order.coupon_applied = coupen_id
        order.address = address
        print(address.id)
        cart = Cart.objects.get(user=user)
        try:
            cart_item = CartItem.objects.filter(cart=cart, is_active=True)
        except:
            cart_item = CartItem.objects.filter(cart=cart, is_active=True)

        cart_total_price = 0
        for item in cart_item:
            cart_total_price = (
                cart_total_price + item.product.selling_price * item.quantity
            )
        tax = (2 * cart_total_price) / 100
        try:
            if request.session["grand_total"]:
                order.total_price = float(request.session["grand_total"])
                # del request.session['grand_total']
            else:
                order.total_price = cart_total_price + tax
        except:
            order.total_price = cart_total_price + tax
        trackno = "wthb" + str(random.randint(1111111, 9999999))
        while Order.objects.filter(tracking_no=trackno) is None:
            trackno = "wthb" + str(random.randint(1111111, 9999999))
        order.tracking_no = trackno

        payment_mode = request.POST.get("payment_mode")

        if payment_mode == "Paid by Razorpay":
            order.payment_mode = request.POST.get("payment_mode")
            order.payment_id = request.POST.get("payment_id")
        elif payment_mode == "wallet":
            print("welcom to wallet")
            try:
                if request.session["grand_total"]:
                    grand_total = float(request.session["grand_total"])
                    order.total_price = float(request.session["grand_total"])
                    del request.session["grand_total"]
                else:
                    grand_total = cart_total_price + tax
            except:
                print(tax)
                grand_total = cart_total_price + tax
            userwallet = UserWallet(
                user=user, amount=grand_total, transaction="debited"
            )
            userwallet.save()

            user.wallet = user.wallet - grand_total
            user.save()
            order.payment_mode = request.POST.get("payment_mode")
            order.payment_id = request.POST.get("payment_id")
        else:
            order.payment_mode = "cod" 
            order.payment_id = " "
        order.save()

        neworderitems = CartItem.objects.filter(cart=cart, is_active=True)
        for item in neworderitems:
            OrderItem.objects.create(
                order=order,
                variant=item.product,
                product=item.product.product,
                price=item.product.selling_price,
                quantity=item.quantity,
            )
            # reduce the product quantity from available stock
            orderproduct = Variation.objects.filter(id=item.product.id).first()
            orderproduct.stock = orderproduct.stock - item.quantity
            orderproduct.save()
        Cart.objects.filter(cart_id=item.cart.cart_id).delete()
        # messages.success(request, "Your order has been placed successfully")
        
        payMode = request.POST.get("payment")
        if payMode == "Paid by Razorpay":
            return redirect("order_success")
        elif payMode == "wallet":
            print("hey wallet")
            return JsonResponse({"status": "Your order has been placed successfully"})
        else:
            pass

        return redirect("order_success")


def RazorpayCheck(request):
    try:
        user = request.user
        print("User:", user)
        
        try:
            user = CustomUser.objects.get(email=user)
        except ObjectDoesNotExist:
            # Handle the case where the user does not exist
            return JsonResponse({'error': 'User not found'}, status=400)

        try:
            cart = Cart.objects.get(user=user)
        except ObjectDoesNotExist:
            # Handle the case where the cart does not exist
            return JsonResponse({'error': 'Cart not found'}, status=400)

        cart_items = CartItem.objects.filter(cart=cart)
        total_price = 0
        
        for item in cart_items:
            print("Selling Price:", item.product.selling_price)
            total_price += item.product.selling_price * item.quantity
        tax = (2*total_price)/100
        
        try:
            if request.session['grand_total']:
                coupon = float(request.session['grand_total'])
                total_price = coupon
            else:
                coupon = 0
                total_price = float(total_price) + float(tax)
        except:
            coupon = 0
            total_price = float(total_price) + float(tax)
        

        return JsonResponse({
            'total_price': total_price,
            
        
        })

    except Exception as e:
        # Handle other unexpected exceptions
        print("Error:", e)
        return JsonResponse({'error': 'Internal Server Error'}, status=500)


# views.py


def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = "Cancelled"
    order.save()

    # Now, you can handle the product quantity update
    update_product_quantity(order)


def update_product_quantity(order):
    # Retrieve the order items and increment the product quantities in stock
    order_items = OrderItem.objects.filter(order=order)
    for order_item in order_items:
        product_variant = order_item.variant
        product_variant.stock += order_item.quantity
        product_variant.save()


def OrderSuccess(request):
    return render(request, "cart/thankyou.html")


def ApplyCoupon(request):
    
    if request.method == 'POST':
        coupon_code = request.POST.get('key1')

        try:
            # Attempt to get the order with the specified coupon code
            order_id = Order.objects.get(user=request.user, coupon_applied__code=coupon_code)
            return JsonResponse({"Message": "The coupon is already used"})
        except Order.DoesNotExist:
            # The order does not exist, proceed with coupon application logic
            pass
        except Exception as e:
            # Handle other exceptions (optional, for debugging purposes)
            print(f"An error occurred: {e}")

        grand_total = request.POST.get('key2')
        grand_totals = float(grand_total)

        try:
            coupon = Coupon.objects.get(code=coupon_code, is_available=True)
            coupen_id = coupon.id
        except Coupon.DoesNotExist:
            # Handle the case where the coupon does not exist
            return JsonResponse({"error": "Invalid coupon code"})
        except Exception as e:
            # Handle other exceptions (optional, for debugging purposes)
            print(f"An error occurred: {e}")
            return JsonResponse({"error": "An error occurred while applying the coupon"})

        discount_amount = coupon.discount
        total = grand_totals - discount_amount
        request.session['grand_total'] = total

        return JsonResponse({"total": f"{total}", "discount_amount": f"{discount_amount}", "coupen_id": f"{coupen_id}"})
