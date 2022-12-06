from django.shortcuts import render, redirect
from . models import Category, FoodItem, Orders
from random import randint
from django.core.mail import send_mail
from django.contrib import messages


# Menu Page
def Menu(request):
    category = Category.objects.all()
    foodItem = FoodItem.objects.all()
    context = {
        'category': category,
        'foodItem': foodItem,
    }
    return render(request, 'food/menu.html', context)


# Item Details Page
def ItemDetails(request, id):
    itemDetails = FoodItem.objects.get(id=id)
    context = {
        'itemDetails': itemDetails,
    }
    return render(request, 'food/food_details.html', context)


# Add To Cart
def AddCart(request):
    if request.method == "POST":
        food_id = request.POST.get("food_item_id")
        quantity = request.POST.get("quantity")
        items = {}

        if request.session.get("food_items"):
            items = request.session.get("food_items")

        items[food_id] = quantity
        request.session["food_items"] = items
        print(request.session["food_items"])
    return redirect('cartDetails')


# Cart Details
def CartDetails(request):
    foods = request.session.get("food_items")
    items = []
    total_price = 0
    if foods:
        for id, quantity in foods.items():
            food = FoodItem.objects.get(id=id)
            price = int(quantity) * int(food.price)
            total_price += price
            items.append({
                "id": id,
                "name": food.name,
                "quantity": quantity,
                "price": price,
                "photo": food.photo,
            })

    context = {
        "foods": items,
        "total_price": total_price,
    }
    return render(request, 'food/cart.html', context)


# Delete the item
def DeleteCardItem(request, id):
    foods = request.session.get("food_items")
    del foods[id]
    request.session["food_items"] = foods

    return redirect('cartDetails')


# OTP Page
def OtpPage(request):
    if not request.session.get("OTP"):
        otp = randint(111111, 999999)
        send_mail(
            "OTP from Coffe Wala",
            f"Your OTP to order food from Coffee Wala i s {otp}",
            "samsahu2022@gmail.com",
            [request.user.email, ],
            fail_silently=False,
        )
        request.session["OTP"] = otp
    return render(request, 'food/check_out.html')


# Place Order
def PlaceOrder(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        if request.session.get("OTP") != int(otp):
            messages.error(request, "Invalid OTP")
            return redirect("checkOut")
        else:
            foods = request.session.get("food_items")
            if foods:
                order_details = ""
                total_price = 0
                for id, quantity in foods.items():
                    food = FoodItem.objects.get(id=id)
                    price = food.price * int(quantity)
                    total_price += price
                    order_details += f"{food.name} x {quantity} "

                order = Orders(
                    user=request.user, order_details=order_details, total_price=total_price)

                order.save()

                del request.session["food_items"]
                del request.session["OTP"]

                print("Success")

    return redirect('orders')


# Orders Details
def OrdersDetails(request):
    orderDetails = Orders.objects.filter(user=request.user).order_by('-id')
    context = {
        'details': orderDetails
    }

    return render(request, 'food/order.html', context)
