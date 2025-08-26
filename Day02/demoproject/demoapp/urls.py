from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('menu/', views.menu, name="menu"),
    path('about/', views.about, name="about"),
    path('book/', views.book, name="book"),
    path('drink/<str:drink_name>', views.drink, name="drink_name"),
]