from django.urls import path
from . import views

app_name = 'datasets'
urlpatterns = [
    path('new/', views.new, name='new'),
    path('list/', views.list, name='list'),
]
