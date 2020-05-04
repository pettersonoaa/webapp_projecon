from django.conf import settings
from django.db import models, connection

ACC_TYPE_CHOICES = [
    ('cash', 'cash'),
    ('investment', 'investment'),
    ('pension', 'pension')
]

IO_TYPE_CHOICES = [
    ('in', 'in'),
    ('out', 'out')
]

RULE_TYPE_CHOICES = [
    ('equal to', 'equal to'),
    ('proportional to', 'proportional to')
]

# geting access to user database models
User = settings.AUTH_USER_MODEL

# Tables
class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=60)
    order = models.IntegerField(null=True, blank=True)
    detail = models.TextField(max_length=100, null=True, blank=True)
    def __str__(self):
        return self.name

class Subcategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=60)
    is_shared = models.BooleanField(default=False, verbose_name='Share bill')
    is_active = models.BooleanField(default=True, verbose_name='Active')
    is_seassonal = models.BooleanField(default=False, verbose_name='Seassonal')
    order = models.IntegerField(null=True, blank=True)
    detail = models.TextField(max_length=100, null=True, blank=True)
    def __str__(self):
        return self.name

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=60)
    acc_type = models.CharField(max_length=60, default='cash', choices=ACC_TYPE_CHOICES, verbose_name='Type')
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Initial Value')
    is_active = models.BooleanField(default=True, verbose_name='Active')
    order = models.IntegerField(null=True, blank=True)
    detail = models.TextField(max_length=100, null=True, blank=True)
    def __str__(self):
        return self.name

class Rule(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    account = models.ForeignKey('Account', on_delete=models.SET_NULL, null=True)
    subcategory = models.ForeignKey('Subcategory', on_delete=models.SET_NULL, null=True)
    io_type = models.CharField(max_length=3, default='out', choices=IO_TYPE_CHOICES, verbose_name='Subcategory In-Out')
    rule_type = models.CharField(max_length=60, default='equal', choices=RULE_TYPE_CHOICES, verbose_name='Rule')
    target = models.ForeignKey('Subcategory', on_delete=models.SET_NULL, null=True, related_name='target')
    target_io_type = models.CharField(max_length=3, default='out', choices=IO_TYPE_CHOICES, verbose_name='Target In-Out')
    coefficient = models.DecimalField(max_digits=10, decimal_places=4, default=1, verbose_name='Coefficient Value')
    constant = models.DecimalField(max_digits=16, decimal_places=4, default=0, verbose_name='Constant Value')
    order = models.IntegerField(null=True, blank=True)
    detail = models.TextField(max_length=100, null=True, blank=True)

class Budget(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    subcategory = models.ForeignKey('Subcategory', on_delete=models.SET_NULL, null=True)
    account = models.ForeignKey('Account', on_delete=models.SET_NULL, null=True)
    io_type = models.CharField(max_length=3, default='out', choices=IO_TYPE_CHOICES, verbose_name='In-Out')
    value = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    
class Transaction(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    subcategory = models.ForeignKey('Subcategory', on_delete=models.SET_NULL, null=True)
    account = models.ForeignKey('Account', on_delete=models.SET_NULL, null=True)
    io_type = models.CharField(max_length=3, default='out', choices=IO_TYPE_CHOICES, verbose_name='In-Out')
    value = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()


