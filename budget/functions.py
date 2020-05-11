from django.db.models import Sum, Max, F
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
def MakeTableDict (model, col_names=[]):
    table = {
        'cols': col_names,
        'rows': []
    }
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
            ).annotate(Sum('value')))
            dataframe[key]['date'] = dataframe[key]['date__year'] * 100 + dataframe[key]['date__month']
            dataframe[key] = dataframe[key].drop(columns=['date__year', 'date__month'])
        else:
            dataframe[key] = DataFrame(model[key].objects.filter(
                user=user,
                subcategory__is_shared=True
            ).values(
                'date__year'
            ).annotate(Sum('value'))).rename(columns={'date__year': 'date'})

    df = merge(
        dataframe['budget'], 
        dataframe['transaction'], 
        suffixes=('_budget', '_transaction'),
        how='outer',
        on=['date']
    ).fillna(0).set_index('date').sort_index(axis=1, ascending=False).rename(columns={'value__sum_transaction': 'transaction', 'value__sum_budget': 'budget'})
    df = df.T.to_dict()
    
    dl = []
    for date in df:
        date_label = datetime.strptime(str(date), date_format_in)
        date_label = date_label.strftime(date_format_out)
        dl.append(
            {
                'date': date_label,
                'transaction': df[date]['transaction'],
                'budget': df[date]['budget']
            }
        )
    return dl

# populate table with aggregated data
def DictPivotTable (user, account, acc_value, year=True, month=True, day=False):

    # setting date formats
    date_format_in, date_format_out = SettingDateFormats(year=year, month=month, day=day)

    # extract aggregated data
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
                        'budget_weight': 'bold'
                    }
                    dict_row.append(dict_dummy)
            c += 1
        df_dict['rows'][io_type]['total'].append(dict_row)
    
    # rows
    for rows in df.values.tolist():
        c = 0
        ratio = 0
        dict_row = []
        for col in df.columns.values:
            if col[0] != 'io_type':
                if col[1] == '':
                    dict_dummy = {
                        'is_atribute': True, 
                        'atribute': rows[c], 
                        'sticky': c,
                        'weight': 'normal'
                    }
                    dict_row.append(dict_dummy)
                elif col[1] == 'value__sum_transaction':
                    transaction, budget = rows[c], rows[c-1]
                    ratio, ratio_color = RatioCalc(transaction, budget)
                    dict_dummy = {
                        'is_atribute': False,
                        'transaction': transaction,
                        'budget': budget,
                        'ratio': ratio,
                        'ratio_color': ratio_color,
                        'transaction_weight': 'normal',
                        'budget_weight': 'light'
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

def PopulateMonth(user, year, month):
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
