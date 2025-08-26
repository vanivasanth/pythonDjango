from django.contrib import admin
from . models import Drinks, DrinksCategory, Employee

admin.site.register(Drinks)
admin.site.register(DrinksCategory)
# Register your models here.
admin.site.register(Employee)