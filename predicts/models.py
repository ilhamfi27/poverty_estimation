from django.db import models


class Prediction(models.Model):
    FEATURE_SELECTION_CHOICES = [
        ('f_score', 'F-Score'),
        ('chi_square', 'Chi-Square'),
        ('cfs', 'Correlation-based Feature Selection'),
    ]
    name = models.CharField(max_length=100, null=True, blank=True, default="")
    feature_selection = models.CharField(max_length=10, choices=FEATURE_SELECTION_CHOICES, default="")
    regularization = models.FloatField(default=1.0)
    epsilon = models.FloatField(default=1.0)
    accuracy_value = models.FloatField(default=0.0)
    error_value = models.FloatField(default=0.0)
    ranked_index = models.TextField(default="")
    feature_num = models.IntegerField(default=0)
    dumped_model = models.CharField(max_length=255, default="")
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
