from django.urls import path
from . import views

app_name = 'predicts'
urlpatterns = [
    path('', views.index, name='index'),
    path('predictor/', views.predictor, name='predictor'),
    path('predict_list/', views.predict_list, name='predict_list'),
    path('ml_model/', views.ml_model, name='ml_model'),
    path('prediction_result/<int:prediction_id>/', views.prediction_result, name='prediction_result'),
]
