from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dataset_insert/', views.dataset_insert, name='dataset_insert'),
    path('dataset_list/', views.dataset_list, name='dataset_list'),
    path('predictor/', views.predictor, name='predictor'),
    path('predict_mapping/', views.predict_mapping, name='predict_mapping'),
]
