from datasets.models import DatasetProfile
from predicts.models import MachineLearningModel
from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError


class DatasetProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, allow_blank=False)
    valid_date = serializers.DateField(required=True)
    source_file = serializers.FileField(required=True)

    class Meta:
        model = DatasetProfile
        fields = ('id', 'name', 'valid_date', 'source_file', 'created_at', 'updated_at')


class ModelMachineLearningSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)

    class Meta:
        model = MachineLearningModel
        fields = "__all__"