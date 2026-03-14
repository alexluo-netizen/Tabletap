from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse
import qrcode
from io import BytesIO
from .models import Restaurant, Table, Menu, MenuItem, Order, OrderItem
from .forms import MenuItemForm, MenuForm

# Public View for Table to Scan and Order
from django.views.decorators.csrf import csrf_exempt

# QR Code Generator for Each Table
from django.contrib.auth.decorators import login_required, user_passes_test

from django.views.decorators.http import require_POST

def index(request):
    return render(request, 'home.html')

def landing(request):
    return render(request, 'landing.html')

#auth
def is_restaurant_owner(user):
    return user.groups.filter(name="restaurant_owner").exists()

@login_required(login_url='account_login')
@user_passes_test(is_restaurant_owner)
def create_menu(request):
    restaurant = get_object_or_404(Restaurant, owner=request.user)

    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            # Check if a menu with the same title exists for this restaurant
            if Menu.objects.filter(restaurant=restaurant, title__iexact=title).exists():
                form.add_error('title', 'A menu with this name already exists.')
            else:
                menu = form.save(commit=False)
                menu.restaurant = restaurant
                menu.save()
                return redirect('owner_dashboard')
    else:
        form = MenuForm()

    return render(request, 'create_menu.html', {'form': form})

@login_required(login_url='account_login')
@user_passes_test(is_restaurant_owner)
def owner_dashboard(request):
    try:
        restaurant = Restaurant.objects.get(owner=request.user)
        menus = Menu.objects.filter(restaurant=restaurant)

        # Build menu and item mapping
        menus_with_items = []
        for menu in menus:
            items = MenuItem.objects.filter(menu=menu)
            menus_with_items.append((menu, items))
    except Restaurant.DoesNotExist:
        menus_with_items = []

    return render(request, "owner_dashboard.html", {"menus_with_items": menus_with_items})

@login_required(login_url='account_login')
@user_passes_test(is_restaurant_owner)
def edit_menu(request, menu_id):
    menu = Menu.objects.get(id=menu_id, restaurant__owner=request.user)
    if request.method == 'POST':
        form = MenuForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            return redirect('owner_dashboard')
    else:
        form = MenuForm(instance=menu)
    return render(request, 'create_menu.html', {'form': form})  # reuse template

@login_required(login_url='account_login')
@user_passes_test(is_restaurant_owner)
def delete_menu(request, menu_id):
    menu = Menu.objects.get(id=menu_id, restaurant__owner=request.user)
    menu.delete()
    return redirect('owner_dashboard')

@login_required(login_url='account_login')
@user_passes_test(is_restaurant_owner)
def add_menu_item(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id, restaurant__owner=request.user)
    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.menu = menu
            menu_item.save()
            return redirect('owner_dashboard')
    else:
        form = MenuItemForm()
    return render(request, 'add_menu_item.html', {'form': form, 'menu': menu})

@login_required
@user_passes_test(is_restaurant_owner)
def delete_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id, menu__restaurant__owner=request.user)
    item.delete()
    return redirect('owner_dashboard')

@login_required
@user_passes_test(lambda u: u.groups.filter(name='restaurant_owner').exists())
def category_menu(request, category):
    try:
        restaurant = Restaurant.objects.get(owner=request.user)
        menus = Menu.objects.filter(restaurant=restaurant)
        items = MenuItem.objects.filter(menu__in=menus, category__iexact=category)
    except Restaurant.DoesNotExist:
        items = []

    return render(request, 'category_menu.html', {
        'category': category,
        'items': items
    })

# create a view of public menu
def public_menu_view(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menus = Menu.objects.filter(restaurant=restaurant).prefetch_related('menuitem_set')
    return render(request, 'public_menu.html', {
        'restaurant': restaurant,
        'menus': menus
    })

@login_required
@user_passes_test(is_restaurant_owner)
def generate_qr(request, table_id):
    table = get_object_or_404(Table, id=table_id, restaurant__owner=request.user)
    url = request.build_absolute_uri(reverse('public_menu_order', args=[table.id]))
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    buffer.seek(0)
    return HttpResponse(buffer.getvalue(), content_type='image/png')

@csrf_exempt
def public_menu_order(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    menus = Menu.objects.filter(restaurant=table.restaurant)

    if request.method == 'POST':
        order = Order.objects.create(table=table)
        for item_id, qty in request.POST.items():
            if item_id.startswith('item_'):
                item = get_object_or_404(MenuItem, id=int(item_id.replace('item_', '')))
                OrderItem.objects.create(order=order, menu_item=item, quantity=int(qty))
        return render(request, 'thank_you.html', {'order': order})

    return render(request, 'public_menu_order.html', {'table': table, 'menus': menus})

@login_required
@user_passes_test(is_restaurant_owner)
def table_qr_list(request):
    restaurant = get_object_or_404(Restaurant, owner=request.user)
    tables = Table.objects.filter(restaurant=restaurant)
    return render(request, 'table_qr_list.html', {'tables': tables})

@login_required
@user_passes_test(is_restaurant_owner)
def view_orders(request):
    restaurant = get_object_or_404(Restaurant, owner=request.user)
    orders = Order.objects.filter(table__restaurant=restaurant).order_by('-created_at')
    return render(request, 'view_orders.html', {'orders': orders})

@require_POST
@login_required
@user_passes_test(is_restaurant_owner)
def mark_order_completed(request, order_id):
    order = get_object_or_404(Order, id=order_id, table__restaurant__owner=request.user)
    order.is_completed = True
    order.save()
    return redirect('restaurant_orders')

@login_required
@user_passes_test(is_restaurant_owner)
def restaurant_orders(request):
    restaurant = get_object_or_404(Restaurant, owner=request.user)
    orders = Order.objects.filter(table__restaurant=restaurant).prefetch_related('items', 'items__menu_item')
    return render(request, 'restaurant_orders.html', {'orders': orders})