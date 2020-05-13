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
    PopulateBudgetDate,
    PopulateMonth,
    DictAccountPivotTable,
    AvailableTypeAccount,
    SharedBill
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
    
    # set parameters
    user = request.user
    if period == 'yearly':
        month = False
    else:
        month = True
        period = 'monthly'
    context = {
        'title': period,
        'io_type_is_unstacked': True
    }

    # request POST
    if request.method == 'POST':
        if 'stack_io_type' in request.POST:
            context['io_type_is_unstacked'] = False
        elif 'unstack_io_type' in request.POST:
            context['io_type_is_unstacked'] = True
        elif 'populate_budget' in request.POST:
            populate_date = request.POST['populate_year'] + request.POST['populate_month']
            PopulateMonth(user=user, populate_date=populate_date)

    # create 'option' labels for populate Budget form
    try:
        context['populate_budget'] = PopulateBudgetDate(user=user)
    except:
        context = {'error_msg': 'Cant render table yet: add some Budget first'}
        return render(request, 'budget/error.html', context)

    try:
        # create tables by account (main tables)
        context['accounts_table'] = DictAccountPivotTable(user=user, month=month)

        # create available table, grouping data by account type
        context['available'] = AvailableTypeAccount(user=user, month=month)
    except:
        context = {'error_msg': 'Cant render table yet: add some Account, Category, Subcategory or Transaction'}
        return render(request, 'budget/error.html', context)

    # create shared bills table, using is_shared flag from subcategory
    try:
        context['shared_bill'] = SharedBill(user=user, month=month)
    except:
        pass

    return render(request, 'budget/index.html', context)


@login_required
def create_view(request, model_name):

    # set parameters
    user = request.user
    context = {
        'title': model_name,
        'delete_button': ALLOW_DELETE_BUTTON[model_name]
    }
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
    
    context['form'] = form
    if needs_custom:
        context['custom_form'] = custom_form

    # build table
    try:
        model = MODEL[model_name].objects.filter(user=user)
        context['table'] = MakeTableDict(model_name=model_name, model=model)
    except:
        pass

    return render(request, 'budget/add.html', context=context)


@login_required
def update_view(request, model_name, pk):

    # set parameters
    context = {'title': model_name}

    # get model and form
    model = get_object_or_404(MODEL[model_name], pk=pk)
    context['form'] = FORM[model_name](request.POST or None, instance=model)

    # request POST
    if request.method == 'POST':
        context['form'].save()
        return redirect ('index_view', period='monthly')
        #return redirect('create_view', model_name=model_name)

    return render(request, 'budget/update.html', context=context)


@login_required
def delete_view(request, model_name, pk):

    # setting parameters
    context = {'title': model_name}

    # get model and form
    model = get_object_or_404(MODEL[model_name], pk=pk)
    context['form'] = FORM['delete_'+model_name](request.POST or None, instance=model)

    # request POST
    if request.method == 'POST':
        model.delete()
        return redirect ('index_view', period='monthly')
    
    return render(request, 'budget/delete.html', context=context)


@login_required
def list_view(request, model_name, period, io_type, subcategory_name, year, month):

    # initialize and filter model
    model = MODEL[model_name].objects.filter(
        user=request.user,
        io_type=io_type,
        date__year=year
    )

    # add month filter
    if period != 'yearly':
        model = model.filter(
            date__month=month
        )

    # add subcategory filter
    if subcategory_name != 'io_type_total':
        model = model.filter(
            subcategory__name=subcategory_name
        )

    # make table to render
    table = MakeTableDict(model_name=model_name, model=model)
    
    # render
    context = {
        'title': model_name, 
        'table': table,
        'delete_button': ALLOW_DELETE_BUTTON[model_name]
    }
    return render(request, 'budget/add.html', context=context)