import api.views as v
from django.urls import path, include
from django.conf.urls import url
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^dataset_profile/(?P<pk>\d+)', v.DatasetProfileDetail.as_view()),
    url(r'^dataset_profile/', v.DatasetProfileList.as_view()),
    url(r'^dataset/(?P<pk>\d+)', v.DatasetDetail.as_view()),
    url(r'^ml_model/(?P<pk>\d+)', v.ModelDetail.as_view()),
    url(r'^ml_model/', v.ModelList.as_view()),
    url(r'^predict/', v.Predictor.as_view()),
]