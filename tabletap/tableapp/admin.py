from django.contrib import admin

# Register my models here.
from .models import Restaurant, Menu, MenuItem, Order, OrderItem, Table

admin.site.register(Restaurant)
admin.site.register(Menu)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Table)