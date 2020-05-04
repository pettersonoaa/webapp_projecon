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
        fields = '__all__'
        widgets = {
            'id': HiddenInput(),
            'user': HiddenInput(),
            'detail': TextInput(attrs={'size': 20})
        }

class SubcategoryModelForm(ModelForm):
    class Meta:
        model = Subcategory
        fields = '__all__'
        widgets = {
            'id': HiddenInput(),
            'user': HiddenInput(),
            'category': HiddenInput(),
            'detail': TextInput(attrs={'size': 20})
        }

class AccountModelForm(ModelForm):
    class Meta:
        model = Account
        fields = '__all__'
        widgets = {
            'id': HiddenInput(),
            'user': HiddenInput(),
            'detail': TextInput(attrs={'size': 20})
        }

class RuleModelForm(ModelForm):
    class Meta:
        model = Rule
        fields = '__all__'
        widgets = {
            'id': HiddenInput(),
            'user': HiddenInput(),
            'account': HiddenInput(),
            'subcategory': HiddenInput(),
            'target': HiddenInput(),
            'detail': TextInput(attrs={'size': 20})
        }
        
class BudgetModelForm(ModelForm):
    class Meta:
        model = Budget
        fields = '__all__'
        widgets = {
            'id': HiddenInput(),
            'user': HiddenInput(),
            'account': HiddenInput(),
            'subcategory': HiddenInput(),
            'detail': TextInput(attrs={'size': 20})
        }

class TransactionModelForm(ModelForm):
    class Meta:
        model = Transaction
        fields = '__all__'
        widgets = {
            'id': HiddenInput(),
            'user': HiddenInput(),
            'account': HiddenInput(),
            'subcategory': HiddenInput(),
            'detail': TextInput(attrs={'size': 20})
        }




class DeleteRuleModelForm(ModelForm):
    class Meta:
        model = Rule
        fields = '__all__'
        widgets = {
            'id': HiddenInput(),
            'user': HiddenInput(),
            'account': HiddenInput(),
            'subcategory': HiddenInput(),
            'io_type': HiddenInput(),
            'rule_type': HiddenInput(),
            'target': HiddenInput(),
            'target_io_type': HiddenInput(),
            'coefficient': HiddenInput(),
            'constant': HiddenInput(),
            'order': HiddenInput(),
            'detail': HiddenInput()
        }

class DeleteBudgetModelForm(ModelForm):
    class Meta:
        model = Budget
        fields = '__all__'
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
        fields = '__all__'
        widgets = {
            'id': HiddenInput(),
            'user': HiddenInput(),
            'subcategory': HiddenInput(),
            'account': HiddenInput(),
            'io_type': HiddenInput(),
            'value': HiddenInput(),
            'date': HiddenInput()
        }
 