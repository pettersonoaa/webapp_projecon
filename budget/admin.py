from django.contrib import admin

from .models import (
    Category,
    Subcategory,
    Account,
    Budget,
    Transaction
)

admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Account)
admin.site.register(Budget)
admin.site.register(Transaction)