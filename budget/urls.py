from django.urls import path

from . import views

urlpatterns = [
    path('', views.index_view, name='index_view'),

    path('monthly', views.monthly_view, name='monthly_view'),
    path('yearly', views.yearly_view, name='yearly_view'),

    path('add_category', views.add_category_view, name='add_category_view'),
    path('add_subcategory', views.add_subcategory_view, name='add_subcategory_view'),
    path('add_account', views.add_account_view, name='add_account_view'),
    path('add_rule', views.add_rule_view, name='add_rule_view'),
    path('add_budget', views.add_budget_view, name='add_budget_view'),
    path('add_transaction', views.add_transaction_view, name='add_transaction_view'),

    path('update_account/<int:pk>', views.update_account_view, name='update_account_view'),
    path('update_category/<int:pk>', views.update_category_view, name='update_category_view'),
    path('update_subcategory/<int:pk>', views.update_subcategory_view, name='update_subcategory_view'),
    path('update_rule/<int:pk>', views.update_rule_view, name='update_rule_view'),
    path('update_budget/<int:pk>', views.update_budget_view, name='update_budget_view'),
    path('update_transaction/<int:pk>', views.update_transaction_view, name='update_transaction_view'),

    path('delete_rule/<int:pk>', views.delete_rule_view, name='delete_rule_view'),
    path('delete_budget/<int:pk>', views.delete_budget_view, name='delete_budget_view'),
    path('delete_transaction/<int:pk>', views.delete_transaction_view, name='delete_transaction_view'),

    path('list/<model_name>/<io_type>/<subcategory_name>/<int:year>/<int:month>', views.list_view, name='list_view'),
]