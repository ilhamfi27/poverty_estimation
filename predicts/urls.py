from django.urls import path
from . import views

app_name = 'predicts'
urlpatterns = [
    path('', views.index, name='index'),
    path('predictor/', views.predictor, name='predictor'),
    path('mapping/', views.mapping, name='mapping'),
    path('prediction_result/<int:prediction_id>/', views.prediction_result, name='prediction_result'),
    path('predict_list/', views.predict_list, name='predict_list'),
    path('api/mapping_result/', views.mapping_result, name='mapping_result'),
    path('api/get_model_detail/', views.get_model_detail, name='get_model_detail'),
    path('api/save_model/', views.save_model, name='save_model'),

]
