from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    path('groups/manager/users', views.managers),
    path('groups/manager/users/<int:userId>', views.manager_user),
    path('groups/delivery-crew/users', views.delivery_crew),
    path('groups/delivery-crew/users/<int:userId>', views.delivery_crew_user),
    path('categories', views.CategoriesView.as_view()),
    path('menu-items', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('cart/menu-items', views.CartView.as_view()),
    path('orders', views.OrderView.as_view()),
    path('orders/<int:pk>', views.SingleOrderView.as_view()),
]