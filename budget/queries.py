from datetime import date, datetime
import pandas, sqlalchemy



# Custom Queries
def CustomQuery(sql):
    return pandas.read_sql(sql=sql, con='sqlite:///db.sqlite3')

def PivotTable(user_id, date_format_in='%Y%m', date_format_out='%b%y'):

    # extract budget and transaction information from user in session
    if date_format_in == '%Y%m':
        budget_id_select = 'budgets.id AS budget_id,'
        budget_id_groupby = ',budgets.id'
    else:
        budget_id_select = ''
        budget_id_groupby = ''

    query_transaction="""
        SELECT
            transactions.date_ym AS Date,
            accounts.name AS Account,
            transactions.io_type AS IO,
            categories.name AS Category,
            subcategories.name AS Subcategory,
            sum(transactions.value) AS transaction_sum
        FROM (
            SELECT 
                budget_transaction.*,
                strftime('"""+str(date_format_in)+"""', budget_transaction.date) AS date_ym
            FROM budget_transaction
            WHERE budget_transaction.user_id = """+str(user_id)+"""
        ) transactions
        LEFT JOIN (
            SELECT budget_account.* FROM budget_account 
            WHERE budget_account.user_id = """+str(user_id)+"""
        ) accounts ON transactions.account_id=accounts.id
        LEFT JOIN (
            SELECT budget_category.* FROM budget_category 
            WHERE budget_category.user_id = """+str(user_id)+"""
        ) categories ON transactions.category_id=categories.id
        LEFT JOIN (
            SELECT budget_subcategory.* FROM budget_subcategory 
            WHERE budget_subcategory.user_id = """+str(user_id)+"""
        ) subcategories ON transactions.subcategory_id=subcategories.id
        GROUP BY
            transactions.date_ym,
            accounts.name,
            transactions.io_type,
            categories.name,
            subcategories.name
    """
    query_budget="""
        SELECT
            budgets.date_ym AS Date,
            accounts.name AS Account,
            budgets.io_type AS IO,
            categories.name AS Category,
            subcategories.name AS Subcategory,
            """+budget_id_select+"""
            sum(budgets.value) AS budget_value
        FROM (
            SELECT 
                budget_budget.*,
                strftime('"""+str(date_format_in)+"""', budget_budget.date) AS date_ym
            FROM budget_budget
            WHERE budget_budget.user_id = """+str(user_id)+"""
        ) budgets
        LEFT JOIN (
            SELECT budget_account.* FROM budget_account 
            WHERE budget_account.user_id = """+str(user_id)+"""
        ) accounts ON budgets.account_id=accounts.id
        LEFT JOIN (
            SELECT budget_category.* FROM budget_category 
            WHERE budget_category.user_id = """+str(user_id)+"""
        ) categories ON budgets.category_id=categories.id
        LEFT JOIN (
            SELECT budget_subcategory.* FROM budget_subcategory 
            WHERE budget_subcategory.user_id = """+str(user_id)+"""
        ) subcategories ON budgets.subcategory_id=subcategories.id
        GROUP BY
            budgets.date_ym,
            accounts.name,
            budgets.io_type,
            categories.name,
            subcategories.name
            """+budget_id_groupby+"""
    """
    fixed_columns = ['Account', 'IO', 'Category', 'Subcategory']
    df = pandas.merge(
            CustomQuery(query_transaction), 
            CustomQuery(query_budget), 
            how='outer', 
            on=['Date']+fixed_columns
        )
    
    df = pandas.pivot_table(
            df,
            fill_value=0,
            index=fixed_columns,
            columns='Date'
        ).swaplevel(0, 1, axis=1).sort_index(axis=1).reset_index()

    # populate dict
    df_dict = {'cols': [],'rows': []}

    # cols
    for col in df.columns.values:
        if col[0] in fixed_columns:
            df_dict['cols'].append({'is_atribute': True, 'atribute': col[0], 'sticky': col[0]})
        elif col[1] == 'transaction_sum':
            date_label = datetime.strptime(col[0], date_format_in)
            date_label = date_label.strftime(date_format_out)
            df_dict['cols'].append({'is_atribute': False, 'date': date_label})
    
    # rows
    for rows in df.values.tolist():
        c = 0
        ratio = 0
        dict_row = []
        for col in df.columns.values:
            if col[0] in fixed_columns:
                dict_row.append({'is_atribute': True, 'atribute': rows[c], 'sticky': col[0]})
            elif col[1] == 'transaction_sum':
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
                    'budget_id': rows[c-2],
                    'ratio': ratio,
                    'ratio_color': ratio_color,
                    'ratio_style': 'width:'+str(ratio)+'%;'
                }
                dict_row.append(dict_dummy)
            c += 1
        df_dict['rows'].append(dict_row)

    return df_dict