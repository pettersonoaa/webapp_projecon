from datetime import date, datetime
from pandas import merge
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Sum, Max, Min, Count, F

from .models import (
    Category, 
    Subcategory, 
    Account, 
    Rule,
    Budget, 
    Transaction
)
MODEL = {
    'account': Account,
    'category': Category,
    'subcategory': Subcategory,
    'rule': Rule,
    'budget': Budget,
    'transaction': Transaction
}

from .forms import (
    CategoryModelForm, 
    SubcategoryModelForm, 
    AccountModelForm, 
    RuleModelForm,
    BudgetModelForm, 
    TransactionModelForm,

    DeleteRuleModelForm,
    DeleteBudgetModelForm,
    DeleteTransactionModelForm
) 
FORM = {
    'account': AccountModelForm,
    'category': CategoryModelForm,
    'subcategory': SubcategoryModelForm,
    'rule': RuleModelForm,
    'budget': BudgetModelForm,
    'transaction': TransactionModelForm,

    'delete_rule': DeleteRuleModelForm,
    'delete_budget': DeleteBudgetModelForm,
    'delete_transaction': DeleteTransactionModelForm,
}

from .functions import (
    MakeTableDict,
    MakeCustomForm,
    PopulateMonth,
    LoadMainTable
)

ALLOW_DELETE_BUTTON = {
    'account': False,
    'category': False,
    'subcategory': False,
    'rule': True,
    'budget': True,
    'transaction': True
}

CUSTOM_FORM_LIST = {
    'subcategory': ['category'],
    'rule': ['account', 'subcategory', 'target'],
    'budget': ['account', 'subcategory'],
    'transaction': ['account', 'subcategory']
}


@login_required
def index_view(request, period):
    
    # setting parameters
    if period == 'yearly':
        month = False
    else:
        month = True
    user = request.user
    io_type_is_unstacked = True

    # request POST
    if request.method == 'POST':
        if 'stack_io_type' in request.POST:
            io_type_is_unstacked = False
        elif 'unstack_io_type' in request.POST:
            io_type_is_unstacked = True
        elif 'populate_budget' in request.POST:
            date = request.POST['populate_year'] + request.POST['populate_month']
            PopulateMonth(user=user, date=date)

    # render tables
    try:
        context = LoadMainTable(user=user, month=month)
        context['io_type_is_unstacked'] = io_type_is_unstacked
        return render(request, 'budget/index.html', context)
    except:
        context = {'error_msg': 'Cant render table yet: add some Account, Category, Subcategory or Transaction'}
        return render(request, 'budget/error.html', context)
    #return redirect('monthly_view')


@login_required
def create_view(request, model_name):

    # get logged user
    user = request.user

    # set custom parameters
    if model_name in CUSTOM_FORM_LIST:
        needs_custom = True
    else:
        needs_custom = False

    # build form and custom form if necessary
    form = FORM[model_name](request.POST or None)
    if needs_custom:
        custom_form = MakeCustomForm(user, CUSTOM_FORM_LIST[model_name])

    # request POST
    if request.method == 'POST' and form.is_valid():

        # save data into Models
        obj = form.save(commit=False)
        obj.user = user
        if needs_custom:
            # save data from custom form: obj.field_name = request.POST[field_name]
            for field_name in CUSTOM_FORM_LIST[model_name]:
                setattr(obj, field_name, MODEL[field_name].objects.get(user=user, name=request.POST[field_name]))
        obj.save()

        # reload form and custom form if necessary cleanned
        form = FORM[model_name]()
        if needs_custom:
            custom_form = MakeCustomForm(user, CUSTOM_FORM_LIST[model_name])

    # build table
    table = MakeTableDict(model_name=model_name, user=user)

    # render
    context = {
        'title': model_name, 
        'form': form, 
        'table': table,
        'delete_button': ALLOW_DELETE_BUTTON[model_name]
    }
    if needs_custom:
        context['form2'] = custom_form
    return render(request, 'budget/add.html', context=context)


@login_required
def update_view(request, model_name, pk):

    # get model and form
    model = get_object_or_404(MODEL[model_name], pk=pk)
    form = FORM[model_name](request.POST or None, instance=model)

    # request POST
    if request.method == 'POST':
        form.save()
        return redirect('add_'+model_name+'_view')
    
    # render
    context = {
        'title': model_name,
        'form': form
    }
    return render(request, 'budget/update.html', context=context)


@login_required
def delete_view(request, model_name, pk):

    # get model and form
    model = get_object_or_404(MODEL[model_name], pk=pk)
    form = FORM['delete_'+model_name](request.POST or None, instance=model)

    # request POST
    if request.method == 'POST':
        model.delete()
        return redirect('add_'+model_name+'_view')
    
    # render
    context = {
        'title': model_name,
        'form': form
    }
    return render(request, 'budget/delete.html', context=context)


@login_required
def list_view(request, model_name, io_type, subcategory_name, year, month):

    user = request.user
    Model = {
        'transaction': Transaction,
        'budget': Budget
    }
    
    # initialize model
    model = Model[model_name].objects

    if subcategory_name != 'io_type_total':
        model = model.filter(subcategory__name=subcategory_name)
    
    model = model.filter(
        io_type=io_type,
        date__year=year,
        date__month=month
    ).values(
        'account__name', 
        'subcategory__category__name', 
        'subcategory__name', 
        'io_type', 
        'value', 
        'date', 
        'id'
    ).order_by(
        '-date', 
        'io_type', 
        'account__order', 
        'subcategory__category__order', 
        'subcategory__order'
    )
    col_names = [
        'Account', 
        'Category', 
        'Subcategory', 
        'Io type', 
        'Value', 
        'Date', 
        'ID'
    ]
    table = MakeTableDict(model=model, col_names=col_names)
    
    # render
    context = {
        'title': model_name, 
        #'form': form, 
        #'form2': form2, 
        'table': table,
        'update_url': 'update_'+model_name+'_view',
        'delete_button': True,
        'delete_url': 'delete_'+model_name+'_view'
    }
    return render(request, 'budget/add.html', context=context)