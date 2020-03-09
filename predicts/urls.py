from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dataset_insert/', views.dataset_insert, name='dataset_insert'),
]
