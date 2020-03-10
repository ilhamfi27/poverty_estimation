from django.urls import path
from . import views

app_name = 'predicts'
urlpatterns = [
    path('', views.index, name='index'),
    path('predictor/', views.predictor, name='predictor'),
    path('mapping/', views.mapping, name='mapping'),
]
