from django.urls import path

from . import views

urlpatterns = [
    path('<period>', views.index_view, name='index_view'),
    path('create/<model_name>', views.create_view, name='create_view'),
    path('update/<model_name>/<int:pk>', views.update_view, name='update_view'),
    path('delete/<model_name>/<int:pk>', views.delete_view, name='delete_view'),
    path('list/<model_name>/<period>/<io_type>/<subcategory_name>/<int:year>/<int:month>', views.list_view, name='list_view'),
]