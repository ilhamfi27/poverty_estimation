from django.db import models


class Prediction(models.Model):
    FEATURE_SELECTION_CHOICES = [
        ('f_score', 'F-Score'),
        ('chi_square', 'Chi-Square'),
        ('cfs', 'Correlation-based Feature Selection'),
    ]
    name = models.CharField(max_length=255, null=True, blank=True, default="")
    feature_selection = models.CharField(max_length=10, choices=FEATURE_SELECTION_CHOICES, default="", null=True,
                                         blank=True)
    regularization = models.FloatField(default=1.0, null=True, blank=True)
    epsilon = models.FloatField(default=1.0, null=True, blank=True)
    accuracy_value = models.FloatField(default=0.0, null=True, blank=True)
    error_value = models.FloatField(default=0.0, null=True, blank=True)
    ranked_index = models.TextField(default="", null=True, blank=True)
    feature_num = models.IntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'predictions'


class PredictionResult(models.Model):
    city = models.ForeignKey('datasets.City', on_delete=models.CASCADE)
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE)
    result = models.FloatField(default=0)

    class Meta:
        db_table = 'prediction_results'


class MachineLearningModel(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, default="")
    regularization = models.FloatField(default=1.0, null=True, blank=True)
    epsilon = models.FloatField(default=1.0, null=True, blank=True)
    feature_selection = models.CharField(max_length=10, default="", null=True, blank=True)
    accuracy_value = models.FloatField(default=0.0, null=True, blank=True)
    error_value = models.FloatField(default=0.0, null=True, blank=True)
    ranked_index = models.TextField(default="", null=True, blank=True)
    feature_num = models.IntegerField(default=0, null=True, blank=True)
    dumped_model = models.CharField(max_length=255, default="", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'machine_learning_models'