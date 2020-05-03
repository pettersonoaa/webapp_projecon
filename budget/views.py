from datetime import date
from pandas import merge
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Sum, Max, Min, Count, F
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
    DictPivotTable,
    DictAccountPivotTable,
    PopulateMonth
)




@login_required
def index_view(request):
    return redirect('monthly_view')




@login_required
def monthly_view(request):
    #PopulateMonth(request.user, 2021, 1)
    model = Budget.objects.filter(
            user=request.user,
            subcategory__is_active=True,
            subcategory__is_seassonal=False,
            value__gt=0
        ).values(
            'subcategory__name'
        ).annotate(max_date=Max('date'))#.filter(date=F('max_date'))
    #print(model)
    for row in model:
        print(row)
        
    try:
        account_table, error = DictAccountPivotTable(request.user, month=True)
        if error:
            context = {'error_msg': 'Account without transaction: '+account_table+'.'}
            return render(request, 'budget/error.html', context)
        else:
            context = {'title': 'Monthly', 'accounts_table': account_table}
            return render(request, 'budget/index.html', context)
    except:
        context = {'error_msg': 'Cant render table yet: add some Account, Category, Subcategory or Transaction'}
        return render(request, 'budget/error.html', context)
    
@login_required
def yearly_view(request):
    try:
        account_table, error = DictAccountPivotTable(request.user, month=False)
        if error:
            context = {'error_msg': 'Account without transaction: '+account_table+'.'}
            return render(request, 'budget/error.html', context)
        else:
            context = {'title': 'Yearly', 'accounts_table': account_table}
            return render(request, 'budget/index.html', context)
    except:
        context = {'error_msg': 'Cant render table yet: add some Account, Category, Subcategory or Transaction'}
        return render(request, 'budget/error.html', context)
    






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
    form2['Category'] = Category.objects.filter(user=user).order_by('order', 'name')
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
    col_names = ['Category', 'Subcategory', 'Share bill', 'Active', 'Details', 'Order', 'ID']
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
    model = Account.objects.filter(user=user).values('name', 'acc_type', 'value', 'is_active', 'detail', 'order', 'id').order_by('order', 'name')
    table = MakeTableDict(model=model, col_names=['Account', 'Type', 'Initial Value', 'Active', 'Detail', 'Order', 'ID'])

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
    form2['Account'] = Account.objects.filter(user=user).order_by('order', 'name')
    form2['Subcategory'] = Subcategory.objects.filter(user=user).order_by('category__order', 'category__name', 'order', 'name')
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.user = user
        obj.account = Account.objects.get(user=user,name=request.POST['Account'])
        obj.subcategory = Subcategory.objects.get(user=user,name=request.POST['Subcategory'])
        obj.save()
        form = BudgetModelForm()
        form2['Account'] = Account.objects.filter(user=user).order_by('order', 'name')
        form2['Subcategory'] = Subcategory.objects.filter(user=user).order_by('category__order', 'category__name', 'order', 'name')
    
    # build table
    model = Budget.objects.filter(user=user).values(
        'account__name', 'subcategory__category__name', 'subcategory__name', 'io_type', 'value', 'date', 'id'
        ).order_by('-date', 'io_type', 'account__order', 'subcategory__category__order', 'subcategory__order')
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
    form2['Account'] = Account.objects.filter(user=user).order_by('order', 'name')
    form2['Subcategory'] = Subcategory.objects.filter(user=user).order_by('category__order', 'category__name', 'order', 'name')
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.user = user
        obj.account = Account.objects.get(user=user,name=request.POST['Account'])
        obj.subcategory = Subcategory.objects.get(user=user,name=request.POST['Subcategory'])
        obj.save()
        form = TransactionModelForm()
        form2['Account'] = Account.objects.filter(user=user).order_by('order', 'name')
        form2['Subcategory'] = Subcategory.objects.filter(user=user).order_by('category__order', 'category__name', 'order', 'name')

    # build table
    model = Transaction.objects.filter(user=user).values(
        'account__name', 'subcategory__category__name', 'subcategory__name', 'io_type', 'value', 'date', 'id'
        ).order_by('-date', 'io_type', 'account__order', 'subcategory__category__order', 'subcategory__order')
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

