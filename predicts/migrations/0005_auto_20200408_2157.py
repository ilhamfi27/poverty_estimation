# Generated by Django 3.0.3 on 2020-04-08 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predicts', '0004_auto_20200408_2152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prediction',
            name='feature_num',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='prediction',
            name='ranked_index',
            field=models.TextField(default=''),
        ),
    ]