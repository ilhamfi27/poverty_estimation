from datasets.models import DatasetProfile
from predicts.models import MachineLearningModel
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