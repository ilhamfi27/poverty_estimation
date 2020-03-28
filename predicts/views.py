from django.shortcuts import render, redirect
from datasets.models import Dataset, City
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


"""
PREDICTOR VIEWS
"""
def index(request):
    return render(request, 'predicts/index.html', {})


def predictor(request):
    context = {
        'dataset_column_names': dataset_column_names,
        'chart_data': [],
        'real_data': [],
    }
    if request.method == "GET":
        pass
    elif request.method == "POST":
        fs_algorithm = request.POST.get("feature_selection")
        C = 60.0 # ntar diambil dari form
        epsilon = 0.2 # ntar diambil dari form

        dataset_data = Dataset.objects.all()

        best_pred, best_score, result, ten_column_predictions, y_true = \
            predict(dataset_data, fs_algorithm, C, epsilon)

        data_for_input = {
            "feature_selection": fs_algorithm,
            "reguralization": C,
            "epsilon": epsilon,
            "accuracy_value": best_score[0],
            "error_value":  best_score[1],
            "pred_result": best_pred,
        }

        save_to_db(data_for_input)

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

    print(data_dict, flush=True)


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


def mapping(request):
    return render(request, 'predicts/mapping.html', {})
