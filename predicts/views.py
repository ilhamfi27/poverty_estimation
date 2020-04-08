from django.http import JsonResponse
from django.shortcuts import render, redirect
from datasets.models import Dataset, City, DatasetProfile
from .models import Prediction, PredictionResult
from .svr import *
import json

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
    "name",
    "feature selection",
    "reguralization",
    "epsilon",
    "accuracy value",
    "error value",
]

prediction_column_names = [
    "id",
    "name",
    "feature_selection",
    "reguralization",
    "epsilon",
    "accuracy value",
    "error_value",
]

"""
PREDICTOR VIEWS
"""


def index(request):
    return render(request, 'predicts/index.html', {})


# ajax request handler
def fs_last_result(request, fs_algorithm):
    if request.method == 'GET':
        prediction = Prediction.objects.filter(feature_selection=fs_algorithm).order_by('-id')[:1]
        prediction_results = PredictionResult.objects.filter(prediction=prediction)

        pred_result = []
        the_real_data = []
        the_data = {}
        for prediction_data in prediction_results:
            real_data = Dataset.objects.get(city=prediction_data.city)

            each_pred_result = {"x": real_data.BPS_poverty_rate, "y": prediction_data.result}
            each_real_data = {"x": real_data.BPS_poverty_rate, "y": real_data.BPS_poverty_rate}

            pred_result.append(each_pred_result)
            the_real_data.append(each_real_data)

        the_data["prediction_results"] = pred_result
        the_data["real_data"] = the_real_data

        context = {}
        context['success'] = True
        context['data'] = the_data

        return JsonResponse(context, content_type="application/json")


def predictor(request):
    table_data = Prediction.objects.values_list("id",
                                                "name",
                                                "feature_selection",
                                                "reguralization",
                                                "epsilon",
                                                "accuracy_value",
                                                "error_value")

    prediction_data = [dict(zip(prediction_column_names, data)) for data in table_data]

    context = {
        'dataset_column_names': dataset_column_names,
        'chart_data': [],
        'real_data': [],
        'table_header': prediction_result_table_header,
        'prediction_data': prediction_data
    }

    if request.method == "GET":
        pass
    elif request.method == "POST":
        fs_algorithm = request.POST.get("feature_selection")
        input_C = request.POST.get("regularization") # 60.0  # ntar diambil dari form
        input_epsilon = request.POST.get("epsilon") # 0.2  # ntar diambil dari form

        C = float(input_C) if input_C != "" else 1.0
        epsilon = float(input_epsilon) if input_epsilon != "" else 0.1

        dataset_profile = DatasetProfile.objects.order_by('-valid_date')[0]
        dataset_data = Dataset.objects.defer('profile').filter(profile=dataset_profile)
        # dataset_data = Dataset.objects.all()

        best_pred, best_score, result, ten_column_predictions, y_true = \
            predict(dataset_data, fs_algorithm, C, epsilon)

        # print("RESULT", result, flush=True)
        print("BEST SCORE", best_score, flush=True)
        # print("TEN COLUMNS", ten_column_predictions, flush=True)

        context["best_rmse"] = round(best_score[0],8)
        context["best_r2"] = round(best_score[1],8)

        data_for_input = {
            "feature_selection": fs_algorithm,
            "reguralization": C,
            "epsilon": epsilon,
            "accuracy_value": best_score[0],
            "error_value": best_score[1],
            "pred_result": best_pred,
        }

        # save_to_db(data_for_input)

        pred_result = []
        real_data = []
        for i, (key, value) in enumerate(best_pred.items()):
            each_pred_result = {"x": y_true[i], "y": value}
            each_real_data = {"x": y_true[i], "y": y_true[i]}
            pred_result.append(each_pred_result)
            real_data.append(each_real_data)
        context["pred_result"] = json.dumps(pred_result)
        context["real_data"] = json.dumps(real_data)
    return render(request, 'predicts/predictor.html', context=context)


def save_to_db(data_dict):
    prediction_data = data_dict
    prediction_result_values = data_dict["pred_result"]
    prediction_data.pop("pred_result")

    prediction = Prediction.objects.create(**prediction_data)

    prediction_results = []
    for city_id, result in prediction_result_values.items():
        city = City.objects.get(pk=city_id)
        prediction_results.append(PredictionResult(
            city=city,
            prediction=prediction,
            result=result,
        ))

    prediction_result = PredictionResult.objects.bulk_create(prediction_results)


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
        the_data["reguralization"] = prediction.reguralization
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


def mapping(request):
    return render(request, 'predicts/mapping.html', {})
