from django.forms import ModelForm, HiddenInput, SelectDateWidget
from .models import Category, Subcategory, Account, Budget, Transaction


class CategoryModelForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'detail']

class SubcategoryModelForm(ModelForm):
    class Meta:
        model = Subcategory
        fields = ['name', 'detail', 'is_shared']

class AccountModelForm(ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'detail']

class BudgetModelForm(ModelForm):
    class Meta:
        model = Budget
        fields = ['io_type', 'value', 'date']
        widgets = {
            'date': SelectDateWidget(empty_label="Nothing")
        }

class TransactionModelForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ['io_type', 'value', 'date']



class UpdateBudgetModelForm(ModelForm):
    class Meta:
        model = Budget
        fields = ['id', 'user', 'category', 'subcategory', 'account', 'io_type', 'value', 'date']
        widgets = {
             'id': HiddenInput(),
             'user': HiddenInput(),
             'category': HiddenInput(),
             'subcategory': HiddenInput(),
             'account': HiddenInput(),
             'io_type': HiddenInput(),
             'date': HiddenInput()
        }

class UpdateTransactionModelForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'category', 'subcategory', 'account', 'io_type', 'value', 'date']
        widgets = {
             'id': HiddenInput(),
             'user': HiddenInput(),
             'category': HiddenInput(),
             'subcategory': HiddenInput(),
             'account': HiddenInput(),
             'io_type': HiddenInput(),
             'date': HiddenInput()
        }



class DeleteBudgetModelForm(ModelForm):
    class Meta:
        model = Budget
        fields = ['id', 'user', 'category', 'subcategory', 'account', 'io_type', 'value', 'date']
        widgets = {
             'id': HiddenInput(),
             'user': HiddenInput(),
             'category': HiddenInput(),
             'subcategory': HiddenInput(),
             'account': HiddenInput(),
             'io_type': HiddenInput(),
             'value': HiddenInput(),
             'date': HiddenInput()
        }

class DeleteTransactionModelForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'category', 'subcategory', 'account', 'io_type', 'value', 'date']
        widgets = {
             'id': HiddenInput(),
             'user': HiddenInput(),
             'category': HiddenInput(),
             'subcategory': HiddenInput(),
             'account': HiddenInput(),
             'io_type': HiddenInput(),
             'value': HiddenInput(),
             'date': HiddenInput()
        }