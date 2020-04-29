from datetime import date
from pandas import merge
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Sum, Max, Min, Count
from .models import (
    Category, 
    Subcategory, 
    Account, 
    Budget, 
    Transaction
)
from .forms import (
    CategoryModelForm, 
    SubcategoryModelForm, 
    AccountModelForm, 
    BudgetModelForm, 
    TransactionModelForm,

    UpdateBudgetModelForm,
    UpdateTransactionModelForm,

    DeleteBudgetModelForm,
    DeleteTransactionModelForm
) 
from .functions import (
    MakeTableDict,
    ModelGroupBy,
    DictPivotTable
)




@login_required
def index_view(request):
    return redirect('monthly_view')




@login_required
def monthly_view(request):
    #GET_DATE_FROM_USER = ['202003', '202004']
    context = {
        'title': 'Monthly',
        'pivot_table': DictPivotTable(request.user, month=True)
    }
    return render(request, 'budget/index.html', context)

@login_required
def yearly_view(request):
    context = {
        'title': 'Yearly',
        'pivot_table': DictPivotTable(request.user, month=False)
    }
    return render(request, 'budget/index.html', context)






@login_required
def add_category_view(request):

    # get logged user
    user = request.user

    # build form
    form = CategoryModelForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.user = user
        obj.save()
        form = CategoryModelForm()
    
    # build table
    model = Category.objects.filter(user=user).values('name', 'order', 'id').order_by('order', 'name')
    table = MakeTableDict(model=model, col_names=['Category', 'Order', 'ID'])

    # render
    context = {
        'title': 'Category', 
        'form': form, 
        'table': table,
        'update_url': 'update_category_view'
    }
    return render(request, 'budget/add.html', context=context)

@login_required
def add_subcategory_view(request):

    # get logged user
    user = request.user

    # build form
    form = SubcategoryModelForm(request.POST or None)
    form2 = {}
    key_label = 'Category'
    form2['Category'] = Category.objects.filter(user=user)
    if request.method == 'POST':
        obj = form.save(commit=False)
        obj.user = user
        obj.category = Category.objects.get(user=user,name=request.POST['Category'])
        obj.save()
        form = SubcategoryModelForm()
        form2['Category'] = Category.objects.filter(user=user)
    
    # build table
    model = Subcategory.objects.filter(user=user).values(
        'category__name', 'name', 'is_shared', 'is_active', 'detail', 'order', 'id'
        ).order_by('category__order', 'order', 'category__name', 'name')
    col_names = ['Category', 'Subcategory', 'Share bills', 'Active bill', 'Details', 'Order', 'ID']
    table = MakeTableDict(model=model, col_names=col_names)

    # render
    context = {
        'title': 'Subcategory', 
        'form': form, 
        'form2': form2, 
        'table': table,
        'update_url': 'update_subcategory_view'
    }
    return render(request, 'budget/add.html', context=context)

@login_required
def add_account_view(request):

    # get logged user
    user = request.user

    # build form
    form = AccountModelForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.user = user
        obj.save()
        form = AccountModelForm()
    
    # build table
    model = Account.objects.filter(user=user).values('name', 'order', 'id').order_by('order', 'name')
    table = MakeTableDict(model=model, col_names=['Account', 'Order', 'ID'])

    # render
    context = {
        'title': 'Account', 
        'form': form, 
        'table': table,
        'update_url': 'update_account_view'
    }
    return render(request, 'budget/add.html', context=context)

@login_required
def add_budget_view(request):

    # get logged user
    user = request.user

    # build form
    form = BudgetModelForm(request.POST or None)
    form2 = {}
    form2['Account'] = Account.objects.filter(user=user)
    form2['Subcategory'] = Subcategory.objects.filter(user=user)
    if request.method == 'POST':
        obj = form.save(commit=False)
        obj.user = user
        obj.account = Account.objects.get(user=user,name=request.POST['Account'])
        obj.subcategory = Subcategory.objects.get(user=user,name=request.POST['Subcategory'])
        obj.category = Subcategory.objects.get(user=user,name=request.POST['Subcategory']).category
        obj.save()
        form = BudgetModelForm()
        form2['Account'] = Account.objects.filter(user=user)
        form2['Subcategory'] = Subcategory.objects.filter(user=user)
    
    # build table
    model = Budget.objects.filter(user=user).values(
        'account__name', 'category__name', 'subcategory__name', 'io_type', 'value', 'date', 'id'
        ).order_by('-date', 'io_type', 'account__order', 'category__order', 'subcategory__order')
    col_names = ['Account', 'Category', 'Subcategory', 'Io type', 'Value', 'Date', 'ID']
    table = MakeTableDict(model=model, col_names=col_names)

    #render
    context = {
        'title': 'Budget', 
        'form': form, 
        'form2': form2, 
        'table': table,
        'update_url': 'update_budget_view',
        'delete_url': 'delete_budget_view'
    }
    return render(request, 'budget/add.html', context=context)

@login_required
def add_transaction_view(request):

    # get logged user
    user = request.user

    # build form
    form = TransactionModelForm(request.POST or None)
    form2 = {}
    form2['Account'] = Account.objects.filter(user=user)
    form2['Subcategory'] = Subcategory.objects.filter(user=user)
    if request.method == 'POST':
        obj = form.save(commit=False)
        obj.user = user
        obj.account = Account.objects.get(user=user,name=request.POST['Account'])
        obj.subcategory = Subcategory.objects.get(user=user,name=request.POST['Subcategory'])
        obj.category = Subcategory.objects.get(user=user,name=request.POST['Subcategory']).category
        try:
            obj.budget = Budget.objects.get(
                            user=user,category=obj.category,subcategory=obj.subcategory,
                            account=obj.account,io_type=obj.io_type,date=date(obj.date.year, obj.date.month, 1)
                        )
        except:
            Budget.objects.create(
                            user=user,category=obj.category,subcategory=obj.subcategory,
                            account=obj.account,io_type=obj.io_type,date=date(obj.date.year, obj.date.month, 1),
                            value=obj.value
            )
        obj.save()
        form = TransactionModelForm()
        form2['Account'] = Account.objects.filter(user=user)
        form2['Subcategory'] = Subcategory.objects.filter(user=user)

    # build table
    model = Transaction.objects.filter(user=user).values(
        'account__name', 'category__name', 'subcategory__name', 'io_type', 'value', 'date', 'id'
        ).order_by('-date', 'io_type', 'account__order', 'category__order', 'subcategory__order')
    col_names = ['Account', 'Category', 'Subcategory', 'Io type', 'Value', 'Date', 'ID']
    table = MakeTableDict(model=model, col_names=col_names)

    # render
    context = {
        'title': 'Transaction', 
        'form': form, 
        'form2': form2, 
        'table': table,
        'update_url': 'update_transaction_view',
        'delete_url': 'delete_transaction_view'
    }
    return render(request, 'budget/add.html', context=context)





@login_required
def update_account_view(request, pk):
    model = get_object_or_404(Account, pk=pk)
    form = AccountModelForm(request.POST or None, instance=model)
    if request.method == 'POST':
        form.save()
        return redirect('add_account_view')
    context = {
        'title': 'Account',
        'form': form
    }
    return render(request, 'budget/update.html', context=context)

@login_required
def update_category_view(request, pk):
    model = get_object_or_404(Category, pk=pk)
    form = CategoryModelForm(request.POST or None, instance=model)
    if request.method == 'POST':
        form.save()
        return redirect('add_category_view')
    context = {
        'title': 'Category',
        'form': form
    }
    return render(request, 'budget/update.html', context=context)

@login_required
def update_subcategory_view(request, pk):
    model = get_object_or_404(Subcategory, pk=pk)
    form = SubcategoryModelForm(request.POST or None, instance=model)
    if request.method == 'POST':
        form.save()
        return redirect('add_subcategory_view')
    context = {
        'title': 'Subcategory',
        'form': form
    }
    return render(request, 'budget/update.html', context=context)

@login_required
def update_budget_view(request, pk):
    model = get_object_or_404(Budget, pk=pk)
    form = UpdateBudgetModelForm(request.POST or None, instance=model)
    if request.method == 'POST':
        form.save()
        return redirect('add_budget_view')
    context = {
        'title': 'Budget',
        'form': form
    }
    return render(request, 'budget/update.html', context=context)

@login_required
def update_transaction_view(request, pk):
    model = get_object_or_404(Transaction, pk=pk)
    form = UpdateTransactionModelForm(request.POST or None, instance=model)
    if request.method == 'POST':
        form.save()
        return redirect('add_transaction_view')
    context = {
        'title': 'Transaction',
        'form': form
    }
    return render(request, 'budget/update.html', context=context)





@login_required
def delete_budget_view(request, pk):
    model = get_object_or_404(Budget, pk=pk)
    form = DeleteBudgetModelForm(request.POST or None, instance=model)
    if request.method == 'POST':
        model.delete()
        return redirect('add_budget_view')
    context = {
        'title': 'Budget',
        'form': form
    }
    return render(request, 'budget/delete.html', context=context)

@login_required
def delete_transaction_view(request, pk):
    model = get_object_or_404(Transaction, pk=pk)
    form = DeleteBudgetModelForm(request.POST or None, instance=model)
    if request.method == 'POST':
        model.delete()
        return redirect('add_transaction_view')
    context = {
        'title': 'Transaction',
        'form': form
    }
    return render(request, 'budget/delete.html', context=context)

