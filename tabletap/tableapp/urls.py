from django.urls import path
# from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('create-menu/', views.create_menu, name='create_menu'),
    path('edit-menu/<int:menu_id>/', views.edit_menu, name='edit_menu'),
    path('delete-menu/<int:menu_id>/', views.delete_menu, name='delete_menu'),
    path('menu/<int:menu_id>/add-item/', views.add_menu_item, name='add_menu_item'),
    path('menu/category/<str:category>/', views.category_menu, name='category_menu'),
    path('qr/<int:table_id>/', views.generate_qr, name='generate_qr'),
    path('table/<int:table_id>/menu/', views.public_menu_order, name='public_menu_order'),
    path('tables/', views.table_qr_list, name='table_qr_list'),
    
    # Only keep one valid version of each path
    path('orders/', views.restaurant_orders, name='restaurant_orders'),
    path('orders/<int:order_id>/complete/', views.mark_order_completed, name='mark_order_completed'),
    path('menu/item/<int:item_id>/delete/', views.delete_menu_item, name='delete_menu_item'),
]
