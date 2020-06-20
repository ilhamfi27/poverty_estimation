from django.http import JsonResponse
from django.shortcuts import render, redirect
from datasets.models import Dataset, City, DatasetProfile, CityGeography
from django.forms.models import model_to_dict
from .models import Prediction, PredictionResult, MachineLearningModel
from .validator import validate_request, saving_model_validation
from django.contrib.auth.decorators import login_required
import predicts.svr as svr
import matplotlib.pyplot as plt
import os
import json
import io
import urllib, base64
import numpy as np
import pandas as pd
from predicts import util

dataset_column_names = [
    'city_id', 'BPS_poverty_rate', 'sum_price_car', 'avg_price_car', 'std_price_car', 'sum_sold_car',
    'avg_sold_car', 'std_sold_car', 'sum_viewer_car', 'avg_viewer_car', 'std_viewer_car', 'sum_buyer_car',
    'avg_buyer_car', 'std_buyer_car', 'sum_price_motor', 'avg_price_motor', 'std_price_motor', 'sum_sold_motor',
    'avg_sold_motor', 'std_sold_motor', 'sum_viewer_motor', 'avg_viewer_motor', 'std_viewer_motor',
    'sum_buyer_motor', 'avg_buyer_motor', 'std_buyer_motor', 'sum_price_rumah_sell', 'avg_price_rumah_sell',
    'std_price_rumah_sell', 'sum_sold_rumah_sell', 'avg_sold_rumah_sell', 'std_sold_rumah_sell',
    'sum_viewer_rumah_sell', 'avg_viewer_rumah_sell', 'std_viewer_rumah_sell', 'sum_buyer_rumah_sell',
    'avg_buyer_rumah_sell', 'std_buyer_rumah_sell', 'sum_price_rumah_rent', 'avg_price_rumah_rent',
    'std_price_rumah_rent', 'sum_sold_rumah_rent', 'avg_sold_rumah_rent', 'std_sold_rumah_rent',
    'sum_viewer_rumah_rent', 'avg_viewer_rumah_rent', 'std_viewer_rumah_rent', 'sum_buyer_rumah_rent',
    'avg_buyer_rumah_rent', 'std_buyer_rumah_rent', 'sum_price_apt_sell', 'avg_price_apt_sell',
    'std_price_apt_sell', 'sum_sold_apt_sell', 'avg_sold_apt_sell', 'std_sold_apt_sell', 'sum_viewer_apt_sell',
    'avg_viewer_apt_sell', 'std_viewer_apt_sell', 'sum_buyer_apt_sell', 'avg_buyer_apt_sell', 'std_buyer_apt_sell',
    'sum_price_apt_rent', 'avg_price_apt_rent', 'std_price_apt_rent', 'sum_sold_apt_rent', 'avg_sold_apt_rent',
    'std_sold_apt_rent', 'sum_viewer_apt_rent', 'avg_viewer_apt_rent', 'std_viewer_apt_rent', 'sum_buyer_apt_rent',
    'avg_buyer_apt_rent', 'std_buyer_apt_rent', 'sum_price_land_sell', 'avg_price_land_sell', 'std_price_land_sell',
    'sum_sold_land_sell', 'avg_sold_land_sell', 'std_sold_land_sell', 'sum_viewer_land_sell',
    'avg_viewer_land_sell', 'std_viewer_land_sell', 'sum_buyer_land_sell', 'avg_buyer_land_sell',
    'std_buyer_land_sell', 'sum_price_land_rent', 'avg_price_land_rent', 'std_price_land_rent',
    'sum_sold_land_rent', 'avg_sold_land_rent', 'std_sold_land_rent', 'sum_viewer_land_rent',
    'avg_viewer_land_rent', 'std_viewer_land_rent', 'sum_buyer_land_rent', 'avg_buyer_land_rent',
    'std_buyer_land_rent'
]

prediction_result_table_header = [
    "feature selection",
    "regularization",
    "epsilon",
    "accuracy value",
    "error value",
]

prediction_column_names = [
    "id",
    "name",
    "feature_selection",
    "regularization",
    "epsilon",
    "accuracy_value",
    "error_value",
]

model_column_header = [
    'id',
    'name',
    'feature_selection',
    'accuracy_value',
    'error_value',
    'epsilon',
    'regularization',
]

"""
PREDICTOR VIEWS
"""


class Conversion():
    def to_list(self, the_string):
        strings = the_string.split(",")
        return [int(i) for i in strings]

@login_required
def index(request):
    if request.method == 'GET':
        lang = request.GET.get("lang")
        if lang == "id":
            template = 'predicts/index_idn.html'
        else:
            template = 'predicts/index.html'
    return render(request, template)


@login_required
def predict_list(request):
    if request.method == "GET":
        predictions = Prediction.objects.values_list("id",
                                                     "name",
                                                     "feature_selection",
                                                     "regularization",
                                                     "epsilon",
                                                     "accuracy_value",
                                                     "error_value")

        prediction_data = [dict(zip(prediction_column_names, data)) for data in predictions]
        context = {
            'table_header': prediction_result_table_header,
            'prediction_data': prediction_data,
        }

        return render(request, 'predicts/list.html', context=context)


@login_required
def predictor(request):
    ml_model = MachineLearningModel.objects.values_list("id",
                                                        "name",
                                                        "feature_selection",
                                                        "accuracy_value",
                                                        "error_value")
    dataset_profiles = DatasetProfile.objects.values("id",
                                                     "name",
                                                     "type",
                                                     "valid_date",
                                                     "total_row")

    saved_ml_model = [dict(zip(("id", "name", "feature_selection", "accuracy_value", "error_value"), data)) for data in
                      ml_model]
    print(saved_ml_model, flush=True)

    context = {
        'dataset_column_names': dataset_column_names,
        'chart_data': [],
        'real_data': [],
        'table_header': prediction_result_table_header,
        'saved_ml_model': saved_ml_model,
        'dataset_profiles_data': dataset_profiles,
    }

    if request.method == "GET":
        return render(request, 'predicts/predictor.html', context=context)


@login_required
def ml_model(request):
    ml_model = MachineLearningModel.objects.values_list("id",
                                                        "name",
                                                        "feature_selection",
                                                        "accuracy_value",
                                                        "error_value",
                                                        "epsilon",
                                                        "regularization")

    saved_ml_model = [dict(zip(("id",
                                "name",
                                "feature_selection",
                                "accuracy_value",
                                "error_value",
                                "epsilon",
                                "regularization"), data)) for data in ml_model]
    print(saved_ml_model, flush=True)

    context = {
        'table_header': model_column_header,
        'saved_ml_model': saved_ml_model,
    }

    if request.method == "GET":
        return render(request, 'predicts/saved_model_list.html', context=context)


# ==========================
# private functions
# ==========================

def get_results(dataset_data, pred_instance):
    if pred_instance == None:
        return [], []

    result = svr.load_model(dataset_data, Conversion.to_list(Conversion, pred_instance.ranked_index),
                            url=pred_instance.dumped_model)
    return result


# ajax request handler
def save_model(request):
    """
    TODO
    1. kumpulin variable yang dibutuhkan buat nyimpen model ML
    2. simpen di session storage browser
    3. buat operasi penyimpanan model ke database.
    4. ubah nama model yang disimpan tambahkan _saved (opsional)
    """
    if not saving_model_validation(request):
        response = {}
        response["message"] = ["Failed to save due to incompatible data input"]
        return JsonResponse(response, content_type="application/json", status=400)

    if request.method == "POST":
        dumped_model = request.POST.get("dumped_model")
        feature_num = request.POST.get("feature_num")
        feature_selection = request.POST.get("feature_selection")
        new_model_name = request.POST.get("new_model_name")
        r2 = request.POST.get("r2")
        ranked_index = request.POST.get("ranked_index")
        rmse = request.POST.get("rmse")

        data_for_input = {
            "name": new_model_name,
            "feature_selection": feature_selection,
            "accuracy_value": r2,
            "error_value": rmse,
            "feature_num": feature_num,
            "ranked_index": ranked_index,
            "dumped_model": dumped_model,
        }
        # save model
        new_model = save_model_to_db(data_for_input)

        context = {}
        context["name"] = new_model_name
        context["accuracy"] = r2
        context["id"] = 20
        context["saved"] = True
        return JsonResponse(context, content_type="application/json")


def draw_figure(predicted, real):
    if len(real) < 1:
        return None

    real = np.array(real)
    for i, x in enumerate(predicted):
        if abs(real[i] - x) > 1.5:
            plt.scatter(real[i], x, c="r", s=15)
        else:
            plt.scatter(real[i], x, c="b", s=15)
    plt.plot(real, real, c="b")
    plt.plot(real - 1.5, real, c="y", linewidth="0.5")
    plt.plot(real + 1.5, real, c="y", linewidth="0.5")
    plt.xlabel("Actual Data")
    plt.ylabel("Prediction Data")

    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    return uri


def save_prediction_to_db(data_dict):
    prediction_data = data_dict
    prediction_result_values = data_dict["pred_result"]

    prediction_data.pop("pred_result")
    prediction = Prediction(**prediction_data)
    prediction.save()

    prediction_results = []
    for city_id, result in prediction_result_values.items():
        city = City.objects.get(pk=city_id)
        prediction_results.append(PredictionResult(
            city=city,
            prediction=prediction,
            result=result,
        ))

    prediction_result = PredictionResult.objects.bulk_create(prediction_results)

    return prediction


def save_model_to_db(data_dict):
    ml_model = MachineLearningModel(**data_dict)
    ml_model.save()

    return ml_model


def save_dataset_to_db(source_file):
    dataframe = pd.read_excel(source_file)
    dataframe_data = np.nan_to_num(dataframe.iloc[0:, :].values)
    dataset_profile = DatasetProfile.objects.create(total_row=len(dataframe_data))

    for row in dataframe_data:
        row_data = []
        for cell in row:
            row_data.append(cell)
        zipped_data = dict(zip(dataset_column_names, row_data))

        # make city id integer instead of float
        zipped_data['city_id'] = int(zipped_data['city_id'])
        zipped_data['profile'] = dataset_profile

        Dataset.objects.create(**zipped_data)


# ajax request handler
def prediction_result(request, prediction_id):
    if request.method == 'GET':
        prediction = Prediction.objects.get(pk=prediction_id)
        prediction_results = PredictionResult.objects.filter(prediction_id=prediction_id)

        pred_result = []
        the_real_data = []
        the_data = {}
        for prediction_data in prediction_results:
            real_data = Dataset.objects.get(city=prediction_data.city)

            each_pred_result = {"x": real_data.BPS_poverty_rate, "y": prediction_data.result}
            each_real_data = {"x": real_data.BPS_poverty_rate, "y": real_data.BPS_poverty_rate}

            pred_result.append(each_pred_result)
            the_real_data.append(each_real_data)

        the_data["name"] = prediction.name
        the_data["feature_selection"] = prediction.feature_selection
        the_data["regularization"] = prediction.regularization
        the_data["epsilon"] = prediction.epsilon
        the_data["created_at"] = prediction.created_at
        the_data["updated_at"] = prediction.updated_at
        the_data["accuracy_value"] = prediction.accuracy_value
        the_data["error_value"] = prediction.error_value

        the_data["prediction_results"] = pred_result
        the_data["real_data"] = the_real_data

        context = {}
        context['success'] = True
        context['data'] = the_data

        return JsonResponse(context, content_type="application/json")


# ajax request handler
def get_model_detail(request):
    if request.method == "GET":
        model_id = request.GET.get('id')
        model = MachineLearningModel.objects.filter(pk=model_id).first()
        model_response = model_to_dict(model)

        model_response['accuracy_value'] = '{0:.3g}'.format(model_response['accuracy_value'])
        model_response['error_value'] = '{0:.3g}'.format(model_response['error_value'])

        context = {}
        context['success'] = True
        context['data'] = model_response

        return JsonResponse(context, content_type="application/json")
