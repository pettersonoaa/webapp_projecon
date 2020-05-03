from django.db.models import Sum, Max
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
            'io_type', 'subcategory__category__order','subcategory__category__name', 'subcategory__order','subcategory__name', 
            'date'
        ).annotate(Sum('value'))
        return DataFrame(grouped_model)
    elif year and month:
        grouped_model = Model.objects.filter(user=user, account=account).values(
            'io_type', 'subcategory__category__order','subcategory__category__name', 'subcategory__order','subcategory__name', 
            'date__year', 'date__month'
        ).annotate(Sum('value'))
        df = DataFrame(grouped_model)
        df['date'] = df['date__year'] * 100 + df['date__month']
        return df.drop(columns=['date__year', 'date__month'])
    elif year:
        grouped_model = Model.objects.filter(user=user, account=account).values(
            'io_type', 'subcategory__category__order','subcategory__category__name', 'subcategory__order','subcategory__name', 
            'date__year'
        ).annotate(Sum('value'))
        return DataFrame(grouped_model).rename(columns={'date__year': 'date'})
    elif month:
        grouped_model = Model.objects.filter(user=user, account=account).values(
            'io_type', 'subcategory__category__order','subcategory__category__name', 'subcategory__order','subcategory__name', 
            'date__month'
        ).annotate(Sum('value'))
        return DataFrame(grouped_model).rename(columns={'date__month': 'date'})
    else:
        grouped_model = Model.objects.filter(user=user, account=account).values(
            'io_type', 'subcategory__category__order','subcategory__category__name', 'subcategory__order','subcategory__name', 
        ).annotate(Sum('value'))
        return DataFrame(grouped_model)

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

# populate table with aggregated data
def DictPivotTable (user, account, acc_value, year=True, month=True, day=False):

    # setting date formats
    if year and month and day:
        date_format_in, date_format_out = '%Y-%m-%d', '%a%d'
    elif year and month:
        date_format_in, date_format_out = '%Y%m', '%b%y'
    elif year:
        date_format_in, date_format_out = '%Y', '%Y'
    elif month:
        date_format_in, date_format_out = '%m', '%b'

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
            dict_account[account['name']] = DictPivotTable(user=user, account=account['id'], acc_value=account['value'], year=year, month=month, day=day)
        except:
            return account['name'], True
    return dict_account, False

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
            'subcategory'
        ).annotate(Max('date'))

        # get id from last filtered data
        for subcategory_row in filtered_subcategories:
            filtered_ids = Budget.objects.filter(
                user=user,
                subcategory=subcategory_row['subcategory'],
                date=subcategory_row['date__max']
            ).values('id')

            # update / insert data
            for id_row in filtered_ids:
                obj = Budget.objects.get(pk=id_row['id'])
                obj, created = Budget.objects.update_or_create(
                    user=obj.user,
                    subcategory=obj.subcategory,
                    account=obj.account,
                    io_type=obj.io_type,
                    value=obj.value,
                    date=date(year=year, month=month, day=1)
                )
    except:
        pass
    
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
        ).values('id')

        # update / insert data
        for id_row in filtered_ids:
            obj = Budget.objects.get(pk=id_row['id'])
            obj, created = Budget.objects.update_or_create(
                user=obj.user,
                subcategory=obj.subcategory,
                account=obj.account,
                io_type=obj.io_type,
                value=obj.value,
                date=date(year=year, month=month, day=1)
            )
    except:
        pass
