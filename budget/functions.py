from django.db.models import Sum, Max, F, Q, Case, When, DecimalField
from pandas import DataFrame, merge
from datetime import date, datetime


COLUMNS = {
    'label': {
        'account__name': 'Account',
        'subcategory__category__name': 'Category',
        'subcategory__name': 'Subcategory',
        'io_type': 'IO'
    }
}


# make table data for add template
def MakeTableDict (model_name, user):

    table = {'cols': [], 'rows': []}

    from .models import Account, Category, Subcategory, Rule, Budget, Transaction
    # account
    if model_name == 'account':
        table['cols'] = [
            'Category', 
            'Order', 
            'ID'
        ]
        model = Account.objects.filter(user = user).values(
            'name', 
            'acc_type', 
            'value', 
            'is_active', 
            'detail', 
            'order', 
            'id'
        ).order_by(
            'order', 
            'name'
        )
    # category
    elif model_name == 'category':
        table['cols'] = [
            'Category', 
            'Order', 
            'ID']
        model = Category.objects.filter(user = user).values(
            'name', 
            'order', 
            'id'
        ).order_by(
            'order', 
            'name'
        )
    # subcategory
    elif model_name == 'subcategory':
        table['cols'] = [
            'Category', 
            'Subcategory', 
            'Share bill', 
            'Active', 
            'Seassonal', 
            'Details', 
            'Order', 
            'ID'
        ]
        model = Subcategory.objects.filter(user = user).values(
            'category__name', 
            'name', 
            'is_shared', 
            'is_active', 
            'is_seassonal', 
            'detail', 
            'order', 
            'id'
        ).order_by(
            'category__order', 
            'order', 
            'category__name', 
            'name'
        )
    # rule
    elif model_name == 'rule':
        table['cols'] = [
            'Acc.',
            'Category',
            'Subcat.', 
            'IO',
            'Rule', 
            'Category',
            'Target', 
            'IO',
            'Coeff.', 
            'Const.', 
            'Order',
            'Detail', 
            'ID'
        ]
        model = Rule.objects.filter(user=user).values(
            'account__name',
            'subcategory__category__name',
            'subcategory__name', 
            'io_type',
            'rule_type', 
            'target__category__name',
            'target__name', 
            'target_io_type',
            'coefficient', 
            'constant', 
            'order',
            'detail', 
            'id'
        ).order_by(
            'account__order',
            'account__name',
            'subcategory__category__order', 
            'subcategory__category__name', 
            'subcategory__order', 
            'subcategory__name', 
            'order'
        )
    elif model_name == 'budget':
        table['cols'] = [
            'Account', 
            'Category', 
            'Subcategory', 
            'Io type', 
            'Value', 
            'Date', 
            'ID'
        ]
        model = Budget.objects.filter(user=user).values(
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
    elif model_name == 'transaction':
        table['cols'] = [
            'Account', 
            'Category', 
            'Subcategory', 
            'Io type', 
            'Value', 
            'Date', 
            'ID'
        ]
        model = Transaction.objects.filter(user=user).values(
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

    i = 0
    for cols in model:
        row_list = []
        for row in cols:
            if row == 'id':
                is_id = True
            else:
                is_id = False
            row_list.append({'value': model[i][row], 'is_id': is_id})
        table['rows'].append(row_list)
        i += 1
    return table


def MakeCustomForm (user, custom=[]):
    custom_form = {}
    if 'account' in custom:
        from .models import Account
        custom_form['account'] = Account.objects.filter(user=user).order_by('order', 'name')
    if 'category' in custom:
        from .models import Category
        custom_form['category'] = Category.objects.filter(user=user).order_by('order', 'name')
    if 'subcategory' in custom:
        from .models import Subcategory
        custom_form['subcategory'] = Subcategory.objects.filter(user=user).order_by('category__order', 'category__name', 'order', 'name')
    if 'target' in custom:
        from .models import Subcategory
        custom_form['subcategory'] = Subcategory.objects.filter(user=user).order_by('category__order', 'category__name', 'order', 'name')
    return custom_form


# extract data from models by user and account
def ModelGroupBy (Model, user, account, year=True, month=True, day=False):
    if year and month and day:
        grouped_model = Model.objects.filter(user=user, account=account).values(
            'subcategory__is_shared',
            'io_type', 'subcategory__category__order','subcategory__category__name', 'subcategory__order','subcategory__name', 
            'date'
        ).annotate(Sum('value'))
        return DataFrame(grouped_model)
    elif year and month:
        grouped_model = Model.objects.filter(user=user, account=account).values(
            'subcategory__is_shared',
            'io_type', 'subcategory__category__order','subcategory__category__name', 'subcategory__order','subcategory__name', 
            'date__year', 'date__month'
        ).annotate(Sum('value'))
        df = DataFrame(grouped_model)
        df['date'] = df['date__year'] * 100 + df['date__month']
        return df.drop(columns=['date__year', 'date__month'])
    elif year:
        grouped_model = Model.objects.filter(user=user, account=account).values(
            'subcategory__is_shared',
            'io_type', 'subcategory__category__order','subcategory__category__name', 'subcategory__order','subcategory__name', 
            'date__year'
        ).annotate(Sum('value'))
        return DataFrame(grouped_model).rename(columns={'date__year': 'date'})
    elif month:
        grouped_model = Model.objects.filter(user=user, account=account).values(
            'subcategory__is_shared',
            'io_type', 'subcategory__category__order','subcategory__category__name', 'subcategory__order','subcategory__name', 
            'date__month'
        ).annotate(Sum('value'))
        return DataFrame(grouped_model).rename(columns={'date__month': 'date'})
    else:
        grouped_model = Model.objects.filter(user=user, account=account).values(
            'subcategory__is_shared',
            'io_type', 'subcategory__category__order','subcategory__category__name', 'subcategory__order','subcategory__name', 
        ).annotate(Sum('value'))
        return DataFrame(grouped_model)


def SettingDateFormats (year, month, day):
    if year and month and day:
        return '%Y-%m-%d', '%a%d'
    elif year and month:
        return '%Y%m', '%b%y'
    elif year and not month:
        return '%Y', '%Y'
    elif month and not year:
        return '%m', '%b'
    elif day:
        return '%Y-%m-%d', '%d'
    else:
        raise Exception('date format problem')


# calculate budget fill ratio and colors
def RatioCalc(transaction, budget):
    try:
        ratio = int(transaction / budget * 100)
    except:
        ratio = 100
    if ratio < 99:
        ratio_color = 'warning'
    elif ratio > 100:
        ratio_color = 'danger'
    else:
        ratio_color = 'success'
    return ratio, ratio_color


def SharedBill (user, month=True):

    # setting date formats
    date_format_in, date_format_out = SettingDateFormats(year=True, month=month, day=False)

    # extract and group data from budget and transaction
    from .models import Budget, Transaction
    model = {
        'budget': Budget,
        'transaction': Transaction
    }
    dataframe = {}
    for key in model:
        if month:
            dataframe[key] = DataFrame(model[key].objects.filter(
                user=user,
                subcategory__is_shared=True
            ).values(
                'date__year', 'date__month'
            ).annotate(value=Sum('value')))
            dataframe[key]['date'] = dataframe[key]['date__year'] * 100 + dataframe[key]['date__month']
            dataframe[key] = dataframe[key].drop(columns=['date__year', 'date__month'])
        else:
            dataframe[key] = DataFrame(model[key].objects.filter(
                user=user,
                subcategory__is_shared=True
            ).values(
                'date__year'
            ).annotate(value=Sum('value'))).rename(columns={'date__year': 'date'})

    # join and pivot table
    df = merge(
        dataframe['budget'], 
        dataframe['transaction'], 
        suffixes=('_budget', '_transaction'),
        how='outer',
        on=['date']
    ).fillna(0).set_index('date').rename(columns={'value_transaction': 'transaction', 'value_budget': 'budget'})
    df = df.T.sort_index(axis=1).to_dict()
    
    # layout output
    dl = []
    for date in df:
        dl.append(
            {
                'date': datetime.strptime(str(date), date_format_in).strftime(date_format_out),
                'transaction': df[date]['transaction'],
                'budget': df[date]['budget']
            }
        )
    return dl


def AvailableTypeAccount (user, month=True):

    # setting date formats
    date_format_in, date_format_out = SettingDateFormats(year=True, month=month, day=False)

    # extract and group data from budget, transaction and account
    from .models import Budget, Transaction, Account
    model = {
        'budget': Budget,
        'transaction': Transaction
    }
    dataframe = {}
    for key in model:
        if month:
            dataframe[key] = DataFrame(model[key].objects.filter(user=user).values(
                'account__acc_type', 'date__year', 'date__month'
            ).annotate(value=Sum(Case(
                When(io_type='out', then=-F('value')),
                When(io_type='in', then='value'),
                default = 0,
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )))).rename(columns={'account__acc_type': 'type'})
            dataframe[key]['date'] = dataframe[key]['date__year'] * 100 + dataframe[key]['date__month']
            dataframe[key] = dataframe[key].drop(columns=['date__year', 'date__month'])
        else:
            dataframe[key] = DataFrame(model[key].objects.filter(user=user).values(
                'account__acc_type', 'date__year'
            ).annotate(value=Sum(Case(
                When(io_type='out', then=-F('value')),
                When(io_type='in', then='value'),
                default = 0,
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )))).rename(columns={'account__acc_type': 'type', 'date__year': 'date'})
    acc = Account.objects.filter(user=user).values('acc_type', 'value')
    initial_value = {}
    for obj in acc:
        initial_value[obj['acc_type']] = obj['value']

    # join and pivot table
    df = merge(
        dataframe['budget'], 
        dataframe['transaction'], 
        suffixes=('_budget', '_transaction'),
        how='outer',
        on=['date', 'type']
    ).rename(columns={'value_transaction': 'transaction', 'value_budget': 'budget'})
    df['transaction_show'] = df['transaction'].isnull()
    date_list = df['date'].sort_values().unique()
    df = df.set_index(['date', 'type']).fillna(0).to_dict()
    
    # layout output
    dd = {
        'head': [datetime.strptime(str(date), date_format_in).strftime(date_format_out) for date in date_list],
        'body': {}
    }
    for acc_type in initial_value:
        dd['body'][acc_type] = []
        transaction_show = True
        transaction = initial_value[acc_type]
        budget = initial_value[acc_type]
        for date in date_list:
            try:
                if df['transaction_show'][(date, acc_type)]:
                    transaction_show = False
                transaction += df['transaction'][(date, acc_type)]
                budget += df['budget'][(date, acc_type)]
            except:
                pass
            dd['body'][acc_type].append(
                    {
                        'transaction_show': transaction_show,
                        'transaction': transaction, 
                        'budget': budget
                    }
                )
    return dd


# populate table with aggregated data
def DictPivotTable (user, account, acc_value, year=True, month=True, day=False):

    # setting date formats
    date_format_in, date_format_out = SettingDateFormats(year=year, month=month, day=day)

    # extract aggregated data and join budget and transaction
    from .models import Budget, Transaction
    model_columns = [
        'io_type', 'subcategory__category__order','subcategory__category__name', 'subcategory__order','subcategory__name', 
        'date'
    ]
    df = merge(
        ModelGroupBy(Budget, user, account, year=year, month=month, day=day), 
        ModelGroupBy(Transaction, user, account, year=year, month=month, day=day), 
        suffixes=('_budget', '_transaction'),
        how='outer', 
        on=model_columns
    ).set_index(model_columns).unstack('date').fillna(0).swaplevel(0, 1, axis=1).sort_index(axis=1)
    df = df.reset_index().drop(columns=['subcategory__category__order', 'subcategory__order'], level=0)
    
    # populate dict
    df_dict = {
        'cols': [], 
        'balance': [],
        'available': [], 
        'rows': {
            'in': {
                'total': [],
                'nontotal': []
            }, 
            'out': {
                'total': [],
                'nontotal': []
            }
        }
    }

    # cols
    c = 0
    for col in df.columns.values:
        if col[0] != 'io_type':
            if col[1] == '':
                dict_dummy = {
                    'is_atribute': True, 
                    'atribute': COLUMNS['label'][col[0]],
                    'sticky': c
                }
                df_dict['cols'].append(dict_dummy)
            elif col[1] == 'value__sum_transaction':
                date_label = datetime.strptime(str(col[0]), date_format_in)
                date_label = date_label.strftime(date_format_out)
                df_dict['cols'].append({'is_atribute': False, 'date': date_label})
        c += 1
    
    # balance
    balance = {
        'in': {'transaction': {}, 'budget': {}},
        'out': {'transaction': {}, 'budget': {}}
    }
    for col in df.columns.values:
        if col[0] != 'io_type':
            if col[1] == 'value__sum_transaction':
                for io_type in balance:
                    for value in balance[io_type]:
                        balance[io_type][value][col[0]] = 0
    for rows in df.values.tolist():
        c = 0
        if 'out' in rows:
            io_type = 'out'
        else:
            io_type = 'in'
        for col in df.columns.values:
            if col[0] != 'io_type':
                if col[1] == 'value__sum_transaction':
                    balance[io_type]['transaction'][col[0]] += rows[c]
                    balance[io_type]['budget'][col[0]] += rows[c-1]
            c += 1
    for io_type in balance:
        c = 0
        ratio = 0
        dict_row = []
        for col in df.columns.values:
            if col[0] != 'io_type':
                if col[1] == '':
                    dict_dummy = {
                        'is_atribute': True, 
                        'atribute': '', 
                        'sticky': c,
                        'weight': 'bold'
                    }
                    if col[0] == 'subcategory__category__name':
                        dict_dummy['atribute'] = io_type
                    dict_row.append(dict_dummy)
                elif col[1] == 'value__sum_transaction':
                    date_label = datetime.strptime(str(col[0]), date_format_in)
                    transaction = balance[io_type]['transaction'][col[0]]
                    budget = balance[io_type]['budget'][col[0]]
                    ratio, ratio_color = RatioCalc(transaction, budget)
                    dict_dummy = {
                        'is_atribute': False,
                        'transaction': transaction,
                        'budget': budget,
                        'ratio': ratio,
                        'ratio_color': ratio_color,
                        'transaction_weight': 'bold',
                        'budget_weight': 'bold',
                        'io_type': io_type,
                        'subcategory_name': 'io_type_total',
                        'year': date_label.year,
                        'month': date_label.month
                    }
                    dict_row.append(dict_dummy)
            c += 1
        df_dict['rows'][io_type]['total'].append(dict_row)
    
    # rows
    for rows in df.values.tolist():
        c = 0
        ratio = 0
        dict_row = []
        subcategory_name = ''
        for col in df.columns.values:
            if col[0] == 'io_type':
                io_type = rows[c]
            else:
                if col[0] == 'subcategory__name':
                    subcategory_name = rows[c]
                if col[1] == '':
                    dict_dummy = {
                        'is_atribute': True, 
                        'atribute': rows[c], 
                        'sticky': c,
                        'weight': 'normal'
                    }
                    dict_row.append(dict_dummy)
                elif col[1] == 'value__sum_transaction':
                    date_label = datetime.strptime(str(col[0]), date_format_in)
                    transaction, budget = rows[c], rows[c-1]
                    ratio, ratio_color = RatioCalc(transaction, budget)
                    dict_dummy = {
                        'is_atribute': False,
                        'transaction': transaction,
                        'budget': budget,
                        'ratio': ratio,
                        'ratio_color': ratio_color,
                        'transaction_weight': 'normal',
                        'budget_weight': 'light',
                        'io_type': io_type,
                        'subcategory_name': subcategory_name,
                        'year': date_label.year,
                        'month': date_label.month
                    }
                    dict_row.append(dict_dummy)
            c += 1
        if 'out' in rows:
            df_dict['rows']['out']['nontotal'].append(dict_row)
        else:
            df_dict['rows']['in']['nontotal'].append(dict_row)
    
    # balance
    dict_row = []
    for col_in, col_out in zip(df_dict['rows']['in']['total'][0], df_dict['rows']['out']['total'][0]):
        if col_in['is_atribute'] and col_out['is_atribute']:
            if col_in['atribute'] == '':
                atribute = ''
            else:
                atribute = 'balance'
            dict_dummy = {
                'is_atribute': True, 
                'atribute': atribute, 
                'sticky': col_in['sticky'],
                'weight': 'bold'
            }
            dict_row.append(dict_dummy)
        else:
            if col_in['transaction'] != 0 or col_out['transaction'] != 0:
                show = True
            else:
                show = False
            dict_dummy = {
                'is_atribute': False,
                'transaction': col_in['transaction'] - col_out['transaction'],
                'budget': col_in['budget'] - col_out['budget'],
                'transaction_weight': 'bold',
                'budget_weight': 'bold',
                'transaction_show': show
            }
            dict_row.append(dict_dummy)
    df_dict['balance'] = dict_row
    
    # available
    acc_value_transaction = acc_value
    acc_value_budget = acc_value
    dict_row = []
    for col in df_dict['balance']:
        if col['is_atribute']:
            if col['atribute'] == '':
                atribute = ''
            else:
                atribute = 'available'
            dict_dummy = {
                'is_atribute': True, 
                'atribute': atribute, 
                'sticky': col['sticky'],
                'weight': col['weight']
            }
        else:
            acc_value_transaction += col['transaction']
            acc_value_budget += col['budget']
            dict_dummy = {
                'is_atribute': False,
                'transaction': acc_value_transaction,
                'budget': acc_value_budget,
                'transaction_weight': col['transaction_weight'],
                'budget_weight': col['budget_weight'],
                'transaction_show': col['transaction_show']
            }
        dict_row.append(dict_dummy)
    df_dict['available'] = dict_row
    
    return df_dict


# populate accounts table
def DictAccountPivotTable(user, year=True, month=True, day=False):
    from .models import Account
    account_model = Account.objects.filter(user=user).values('name', 'value', 'id', 'order').order_by('order')
    dict_account = {}
    for account in account_model:
        try:
            dict_account[account['name']] = DictPivotTable(
                user=user, 
                account=account['id'], 
                acc_value=account['value'], 
                year=year, 
                month=month, 
                day=day
            )
        except:
            context = {'error_msg': 'Account without transaction and/or budget: '+account['name']+'.'}
            return render(request, 'budget/error.html', context)
    return dict_account


def PopulateMonth(user, date):
    
    # setting date format: input = string, output = date
    date = datetime.strptime(date, '%Y%b')
    year, month = date.year, date.month

    # load models
    from .models import Budget

    # non-seassonal: 
    try:
        # get last non-zero month by subcategory
        filtered_subcategories = Budget.objects.filter(
            user=user,
            subcategory__is_active=True,
            subcategory__is_seassonal=False,
            value__gt=0
        ).values(
            'account',
            'subcategory'
        ).annotate(Max('date'))
        # get id from last filtered data
        for subcategory_row in filtered_subcategories:
            filtered_ids = Budget.objects.filter(
                user=user,
                account=subcategory_row['account'],
                subcategory=subcategory_row['subcategory'],
                date=subcategory_row['date__max']
            )
            # update / insert data
            for id_row in filtered_ids:
                obj, created = Budget.objects.update_or_create(
                    user=id_row.user,
                    subcategory=id_row.subcategory,
                    account=id_row.account,
                    io_type=id_row.io_type,
                    value=id_row.value,
                    date=date(year=year, month=month, day=1)
                )
    except:
        print('erro: non-seassonal')
    
    # seassonal:
    try:
        # get id from non-zero last year data
        filtered_ids = Budget.objects.filter(
            user=user,
            subcategory__is_active=True,
            subcategory__is_seassonal=True,
            value__gt=0,
            date__year=year-1,
            date__month=month
        )
        # update / insert data
        for id_row in filtered_ids:
            obj, created = Budget.objects.update_or_create(
                user=id_row.user,
                subcategory=id_row.subcategory,
                account=id_row.account,
                io_type=id_row.io_type,
                value=id_row.value,
                date=date(year=year, month=month, day=1)
            )
    except:
        print('erro: seassonal')

    # rules:
    try:
        from datetime import timedelta
        rules = Rule.objects.order_by('order', 'subcategory__order', 'target__order')
        for rule in rules:
            current_month_target = Budget.objects.get(
                user=user, 
                account=rule.account,
                subcategory=rule.target,
                io_type=rule.target_io_type,
                date__year=year,
                date__month=month
            )
            # do: value_t = const + coeff * target_t
            value = rule.constant + rule.coefficient * current_month_target.value
            # get last month data id proportional is tagged
            if rule.rule_type == 'proportional to':
                last_month = date(year,month,1) + timedelta(days=-1)
                last_month_subcategory = Budget.objects.get(
                    user=user, 
                    account=rule.account,
                    subcategory=rule.subcategory,
                    io_type=rule.io_type,
                    date__year=last_month.year,
                    date__month=last_month.month
                )
                last_month_target = Budget.objects.get(
                    user=user, 
                    account=rule.account,
                    subcategory=rule.target,
                    io_type=rule.target_io_type,
                    date__year=last_month.year,
                    date__month=last_month.month
                )
                # do: value_t = const + (target_t / target_t-1) * coeff * value_t-1
                value = rule.constant + (current_month_target.value / last_month_target.value * rule.coefficient) * last_month_subcategory.value
            # update / insert data
            obj, created = Budget.objects.update_or_create(
                user=current_month_target.user,
                subcategory=rule.subcategory,
                account=current_month_target.account,
                io_type=current_month_target.io_type,
                date=current_month_target.date,
                value= value
            )
    except:
        print('erro: rule')


def LoadMainTable (user, month):

    # setting title
    if month:
        title = 'Monthly'
    else:
        title = 'Yearly'

    # create 'option' labels for populate Budget form
    from .models import Budget
    model = Budget.objects.values('date__year').distinct()
    populate_budget = {
        'month': [date(1,i+1,1).strftime('%b') for i in range(12)],
        'year': [i['date__year'] for i in model],
    }
    populate_budget['year'].append(populate_budget['year'][-1]+1)
    populate_budget['year'].append(populate_budget['year'][0]-1)

    # create table by account (main tables)
    account_table = DictAccountPivotTable(user=user, month=month)

    # create available table, grouping data by account type
    available = AvailableTypeAccount(user=user, month=month)

    # create shared bills table, using is_shared flag from subcategory
    shared_bill = SharedBill(user=user, month=month)

    # return context dict
    context = {
        'title': title, 
        'populate_budget': populate_budget,
        'accounts_table': account_table,
        'available': available,
        'shared_bill': shared_bill,
    }
    return context