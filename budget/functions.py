from django.db.models import Sum
from pandas import DataFrame, merge
from datetime import date, datetime

COLUMNS_LABEL = {
    'account__name': 'Account',
    'category__name': 'Category',
    'subcategory__name': 'Subcategory',
    'io_type': 'IO',
}

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
    return  table

def ModelGroupBy (Model, user, year=True, month=True, day=False):
    if year and month and day:
        grouped_model = Model.objects.filter(user=user).values(
            'account__order' ,'category__order', 'subcategory__order',
            'account__name', 'io_type', 'category__name', 'subcategory__name',
            'date'
        ).annotate(Sum('value'))
        return DataFrame(grouped_model)
    elif year and month:
        grouped_model = Model.objects.filter(user=user).values(
            'account__order' ,'category__order', 'subcategory__order',
            'account__name', 'io_type', 'category__name', 'subcategory__name',
            'date__year', 'date__month'
        ).annotate(Sum('value'))
        df = DataFrame(grouped_model)
        df['date'] = df['date__year'] * 100 + df['date__month']
        return df.drop(columns=['date__year', 'date__month'])
    elif year:
        grouped_model = Model.objects.filter(user=user).values(
            'account__order' ,'category__order', 'subcategory__order',
            'account__name', 'io_type', 'category__name', 'subcategory__name',
            'date__year'
        ).annotate(Sum('value'))
        return DataFrame(grouped_model).rename(columns={'date__year': 'date'})
    elif month:
        grouped_model = Model.objects.filter(user=user).values(
            'account__order' ,'category__order', 'subcategory__order',
            'account__name', 'io_type', 'category__name', 'subcategory__name',
            'date__month'
        ).annotate(Sum('value'))
        return DataFrame(grouped_model).rename(columns={'date__month': 'date'})
    else:
        grouped_model = Model.objects.filter(user=user).values(
            'account__order' ,'category__order', 'subcategory__order',
            'account__name', 'io_type', 'category__name', 'subcategory__name'
        ).annotate(Sum('value'))
        return DataFrame(grouped_model)
        

def DictPivotTable (user, year=True, month=True, day=False):

    # extract aggregated data
    from .models import Budget, Transaction
    model_columns = [
        'account__order' ,'category__order', 'subcategory__order',
        'account__name','io_type','category__name','subcategory__name', 'date'
    ]
    df = merge(
        ModelGroupBy(Budget, user, year=year, month=month, day=day), 
        ModelGroupBy(Transaction, user, year=year, month=month, day=day), 
        suffixes=('_budget', '_transaction'),
        how='outer', 
        on=model_columns
    ).set_index(model_columns).unstack('date').fillna(0)
    df = df.swaplevel(0, 1, axis=1).sort_index(axis=1).reset_index().rename(columns=COLUMNS_LABEL)
    df = df.drop(columns=['account__order' ,'category__order', 'subcategory__order'])

    # populate dict
    df_dict = {'cols': [],'rows': []}
    if year and month and day:
        date_format_in, date_format_out = '%Y-%m-%d', '%a%d'
    elif year and month:
        date_format_in, date_format_out = '%Y%m', '%b%y'
    elif year:
        date_format_in, date_format_out = '%Y', '%Y'
    elif month:
        date_format_in, date_format_out = '%m', '%b'

    # cols
    for col in df.columns.values:
        if col[1] == '':
            df_dict['cols'].append({'is_atribute': True, 'atribute': col[0], 'sticky': col[0]})
        elif col[1] == 'value__sum_transaction':
            date_label = datetime.strptime(str(col[0]), date_format_in)
            date_label = date_label.strftime(date_format_out)
            df_dict['cols'].append({'is_atribute': False, 'date': date_label})
    
    # rows
    for rows in df.values.tolist():
        c = 0
        ratio = 0
        dict_row = []
        for col in df.columns.values:
            if col[1] == '':
                dict_row.append({'is_atribute': True, 'atribute': rows[c], 'sticky': col[0]})
            elif col[1] == 'value__sum_transaction':
                try:
                    ratio = int(rows[c] / rows[c-1] * 100)
                except:
                    ratio = 100
                if ratio < 99:
                    ratio_color = 'warning'
                elif ratio > 100:
                    ratio_color = 'danger'
                else:
                    ratio_color = 'success'
                dict_dummy = {
                    'is_atribute': False,
                    'transaction': rows[c],
                    'budget': rows[c-1],
                    'ratio': ratio,
                    'ratio_color': ratio_color,
                }
                dict_row.append(dict_dummy)
            c += 1
        df_dict['rows'].append(dict_row)

    return df_dict

