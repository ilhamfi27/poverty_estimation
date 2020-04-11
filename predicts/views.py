from django.http import JsonResponse
from django.shortcuts import render, redirect
from datasets.models import Dataset, City, DatasetProfile
from .models import Prediction, PredictionResult
import predicts.svr as svr
import matplotlib.pyplot as plt
import os
import json
import io
import urllib, base64

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


class Conversion():
    def to_list(self, the_string):
        strings = the_string.split(",")
        return [int(i) for i in strings]


def index(request):
    prediction = Prediction.objects.all()
    if request.method == 'GET':
        # get model for each feature selection
        best_f_score = prediction.filter(feature_selection="f_score").order_by('-accuracy_value').first()
        best_chi_square = prediction.filter(feature_selection="chi_square").order_by('-accuracy_value').first()
        best_cfs = prediction.filter(feature_selection="cfs").order_by('-accuracy_value').first()

        # get dataset
        dataset_profile = DatasetProfile.objects.order_by('-valid_date').first()
        dataset_data = Dataset.objects.defer('profile').filter(profile=dataset_profile)

        f_score_result, f_score_true = get_results(dataset_data, best_f_score)
        chi_square_result, chi_square_true = get_results(dataset_data, best_chi_square)
        cfs_result, cfs_true = get_results(dataset_data, best_cfs)

        context = {}

        f_score_plot = draw_figure(f_score_result, f_score_true)
        chi_square_plot = draw_figure(chi_square_result, chi_square_true)
        cfs_plot = draw_figure(cfs_result, cfs_true)

        context["f_score_plot"] = f_score_plot
        context["chi_square_plot"] = chi_square_plot
        context["cfs_plot"] = cfs_plot

    return render(request, 'predicts/index.html', context=context)


def get_results(dataset_data, pred_instance):
    if pred_instance == None:
        return [], []

    result, y_true = svr.load_model(dataset_data, Conversion.to_list(Conversion, pred_instance.ranked_index),
                                    url=pred_instance.dumped_model)
    return result, y_true


# ajax request handler
def fs_last_result(request, fs_algorithm):
    if request.method == 'GET':
        prediction = Prediction.objects.filter(feature_selection=fs_algorithm).order_by('-accuracy_value').first()
        prediction_results = PredictionResult.objects.filter(prediction=prediction)

        pred_result = []
        the_real_data = []
        the_data = {}

        # print("OLD FEATURE NUM", prediction, flush=True)
        # print("OLD FEATURE INDEXES", prediction.ranked_index, flush=True)

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
        input_C = request.POST.get("regularization")  # 60.0  # ntar diambil dari form
        input_epsilon = request.POST.get("epsilon")  # 0.2  # ntar diambil dari form

        C = float(input_C) if input_C != "" else 1.0
        epsilon = float(input_epsilon) if input_epsilon != "" else 0.1

        dataset_profile = DatasetProfile.objects.order_by('-valid_date').first()
        dataset_data = Dataset.objects.defer('profile').filter(profile=dataset_profile)

        best_pred, best_score, result, ten_column_predictions, y_true, filename = \
            svr.predict(dataset_data, fs_algorithm, C, epsilon)

        # get full file path
        SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_model_file_path = SITE_ROOT + "/" + filename

        ranked_index = [str(i) for i in best_score[4]]
        ranked_index = ",".join(ranked_index)

        data_for_input = {
            "feature_selection": fs_algorithm,
            "reguralization": C,
            "epsilon": epsilon,
            "accuracy_value": best_score[0],
            "error_value": best_score[1],
            "pred_result": best_pred,
            "feature_num": best_score[2],
            "ranked_index": ranked_index,
            "dumped_model": full_model_file_path,
        }

        save_to_db(data_for_input)

        y_pred, y_true = list(best_pred.values()), y_true

        uri = draw_figure(y_pred, y_true)

        pred_result = []
        real_data = []
        for i, (key, value) in enumerate(best_pred.items()):
            each_pred_result = {"x": y_true[i], "y": value}
            each_real_data = {"x": y_true[i], "y": y_true[i]}
            pred_result.append(each_pred_result)
            real_data.append(each_real_data)
        context["best_rmse"] = round(best_score[0], 8)
        context["best_r2"] = round(best_score[1], 8)
        context["pred_result"] = json.dumps(pred_result)
        context["real_data"] = json.dumps(real_data)
        context["figure"] = uri
    return render(request, 'predicts/predictor.html', context=context)


def draw_figure(y_pred, y_true):
    if len(y_true) < 1:
        return None

    for i, x in enumerate(y_pred):
        if abs(y_true[i] - x) > 1.5:
            plt.scatter(y_true[i], x, c="r", s=15)
        else:
            plt.scatter(y_true[i], x, c="b", s=15)
    plt.plot(y_true, y_true)
    plt.plot(y_true - 1.5, y_true, c="y", linewidth="0.5")
    plt.plot(y_true + 1.5, y_true, c="y", linewidth="0.5")
    plt.xlabel("Actual Data")
    plt.ylabel("Prediction Data")

    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    return uri


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
