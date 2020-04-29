from django.conf import settings
from django.db import models, connection


IO_TYPE_CHOICES = [
    ('in', 'in'),
    ('out', 'out')
]

# geting access to user database models
User = settings.AUTH_USER_MODEL

# Tables
class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=60)
    detail = models.TextField(max_length=100, null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return self.name

class Subcategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=60)
    is_shared = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    detail = models.TextField(max_length=100, null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return self.name

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=60)
    detail = models.TextField(max_length=100, null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return self.name

class Budget(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    subcategory = models.ForeignKey('Subcategory', on_delete=models.SET_NULL, null=True)
    account = models.ForeignKey('Account', on_delete=models.SET_NULL, null=True)
    io_type = models.CharField(max_length=3, default='out', choices=IO_TYPE_CHOICES)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    
class Transaction(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    subcategory = models.ForeignKey('Subcategory', on_delete=models.SET_NULL, null=True)
    account = models.ForeignKey('Account', on_delete=models.SET_NULL, null=True)
    io_type = models.CharField(max_length=3, default='out', choices=IO_TYPE_CHOICES)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    