from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to little lemon restaurant")
    
def about(request):
    return HttpResponse("About us")

def menu(request):
    return HttpResponse("Menu for Little Lemon")

def book(request):
    return HttpResponse("Make a booking")

def drink(request, drink_name):
    drinks={"mocha":"type of coffee", 
            "tea":"type of beverage",
            "lemonade":"type of refreshment"}
    choice_of_drink = drinks[drink_name]   
    returntext =  f"<h2> {drink_name} </h2>" + choice_of_drink 
    return HttpResponse(returntext)


# Create your views here.
