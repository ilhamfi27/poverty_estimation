from datasets.models import DatasetProfile
from predicts.models import MachineLearningModel
from predicts.models import Prediction
from predicts.models import PredictionResult
from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError


class DatasetProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, allow_blank=False)
    valid_date = serializers.DateField(required=True)

    class Meta:
        model = DatasetProfile
        fields = '__all__'


class ModelMachineLearningSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)

    class Meta:
        model = MachineLearningModel
        fields = "__all__"


class PredictionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)

    class Meta:
        model = Prediction
        fields = "__all__"


class PredictonResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionResult
        fields = "__all__"