from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('select-user/', views.select_user, name='select_user'),
    path('entry/<str:category>/<str:entry_type>/', views.create_entry, name='create_entry'),
    path('ajax/add-charge/', views.add_charge_ajax, name='add_charge_ajax'),
    path('download/<str:filename>/', views.download_document, name='download_document'),
]
