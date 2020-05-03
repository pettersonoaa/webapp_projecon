from django.forms import (
    ModelForm, 
    HiddenInput, 
    SelectDateWidget, 
    TextInput
)
from .models import (
    Category, 
    Subcategory, 
    Account, 
    Rule,
    Budget, 
    Transaction
)

class CategoryModelForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'order', 'detail']
        widgets = {
            'detail': TextInput(attrs={'size': 20})
        }

class SubcategoryModelForm(ModelForm):
    class Meta:
        model = Subcategory
        fields = ['name', 'is_shared', 'is_active', 'is_seassonal', 'order', 'detail']
        widgets = {
            'detail': TextInput(attrs={'size': 20})
        }

class AccountModelForm(ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'acc_type', 'value', 'is_active', 'order', 'detail']
        widgets = {
            'detail': TextInput(attrs={'size': 20})
        }

class RuleModelForm(ModelForm):
    class Meta:
        model = Rule
        fields = ['rule_type', 'coefficient_value', 'constant_value', 'order', 'detail']
        widgets = {
            'detail': TextInput(attrs={'size': 20})
        }
        
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
        widgets = {
            'date': SelectDateWidget(empty_label="Nothing")
        }



class UpdateBudgetModelForm(ModelForm):
    class Meta:
        model = Budget
        fields = ['id', 'user', 'subcategory', 'account', 'io_type', 'value', 'date']
        widgets = {
            'id': HiddenInput(),
            'user': HiddenInput()
        }

class UpdateTransactionModelForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'subcategory', 'account', 'io_type', 'value', 'date']
        widgets = {
            'id': HiddenInput(),
            'user': HiddenInput()
        }



class DeleteRuleModelForm(ModelForm):
    class Meta:
        model = Rule
        fields = ['subcategory', 'rule_type', 'target', 'coefficient_value', 'constant_value', 'order', 'detail']
        widgets = {
            'id': HiddenInput(),
            'user': HiddenInput(),
            'subcategory': HiddenInput(),
            'rule_type': HiddenInput(),
            'target': HiddenInput(),
            'coefficient_value': HiddenInput(),
            'constant_value': HiddenInput(),
            'order': HiddenInput(),
            'detail': HiddenInput()
        }

class DeleteBudgetModelForm(ModelForm):
    class Meta:
        model = Budget
        fields = ['id', 'user', 'subcategory', 'account', 'io_type', 'value', 'date']
        widgets = {
            'id': HiddenInput(),
            'user': HiddenInput(),
            'subcategory': HiddenInput(),
            'account': HiddenInput(),
            'io_type': HiddenInput(),
            'value': HiddenInput(),
            'date': HiddenInput()
        }

class DeleteTransactionModelForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'subcategory', 'account', 'io_type', 'value', 'date']
        widgets = {
            'id': HiddenInput(),
            'user': HiddenInput(),
            'subcategory': HiddenInput(),
            'account': HiddenInput(),
            'io_type': HiddenInput(),
            'value': HiddenInput(),
            'date': HiddenInput()
        }
 