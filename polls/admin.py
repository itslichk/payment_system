from django.contrib import admin
from .models import User, Product, Transaction, Coupon, AccessCode

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'description')
    search_fields = ('name',)

admin.site.register(User)
admin.site.register(Product, ProductAdmin)
admin.site.register(Transaction)
admin.site.register(Coupon)
admin.site.register(AccessCode)
