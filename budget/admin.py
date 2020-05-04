from django.contrib import admin

from .models import (
    Account,
    Category,
    Subcategory,
    Rule,
    Budget,
    Transaction
)

admin.site.register(Account)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Rule)
admin.site.register(Budget)
admin.site.register(Transaction)