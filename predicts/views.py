from django.http import JsonResponse
from django.shortcuts import render, redirect
from datasets.models import Dataset, City, DatasetProfile
from django.forms.models import model_to_dict
from .models import Prediction, PredictionResult
from .validator import validate_request
import predicts.svr as svr
import matplotlib.pyplot as plt
import os
import json
import io
import urllib, base64
import numpy as np
import pandas as pd

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
    "accuracy_value",
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
    # get dataset
    dataset_profile = DatasetProfile.objects.order_by('-valid_date').first()
    dataset_data = Dataset.objects.filter(profile=dataset_profile)
    bps_poverty_rate = dataset_data.values_list('BPS_poverty_rate')

    if request.method == 'GET':
        best_prediction = Prediction.objects.order_by('-accuracy_value').first()
        best_result, city_result = get_results(dataset_data, best_prediction)
        list_bps_poverty_rate = [i[0] for i in bps_poverty_rate]

        prediction_result = PredictionResult.objects.filter(prediction=best_prediction)

        context = {}
        context['best_plot'] = draw_figure(best_result, list_bps_poverty_rate)
        context['prediction_result'] = prediction_result

    return render(request, 'predicts/index.html', context=context)


def get_results(dataset_data, pred_instance):
    if pred_instance == None:
        return [], []

    result = svr.load_model(dataset_data, Conversion.to_list(Conversion, pred_instance.ranked_index),
                            url=pred_instance.dumped_model)
    return result


# ajax request handler
def mapping_result(request):
    if request.method == 'GET':
        # get dataset
        best_prediction = Prediction.objects.order_by('-accuracy_value').first()
        prediction_result = PredictionResult.objects.filter(prediction=best_prediction)

        response = []
        for result in prediction_result:
            data = {}
            data['city_id'] = result.city.id
            data['city_name'] = result.city.name
            data['latitude'] = result.city.latitude
            data['longitude'] = result.city.longitude
            data['poverty_rate'] = result.result

            response.append(data)

        context = {}
        context['success'] = True
        context['data'] = response

        return JsonResponse(context, content_type="application/json")


def predictor(request):
    predictions = Prediction.objects.values_list("id",
                                                 "name",
                                                 "feature_selection",
                                                 "reguralization",
                                                 "epsilon",
                                                 "accuracy_value",
                                                 "error_value")
    dataset_profiles = DatasetProfile.objects.all()

    prediction_data = [dict(zip(prediction_column_names, data)) for data in predictions]
    dataset_profiles_data = [model_to_dict(data) for data in dataset_profiles]

    context = {
        'dataset_column_names': dataset_column_names,
        'chart_data': [],
        'real_data': [],
        'table_header': prediction_result_table_header,
        'prediction_data': prediction_data,
        'dataset_profiles_data': dataset_profiles_data,
    }

    if request.method == "GET":
        return render(request, 'predicts/predictor.html', context=context)
    elif request.method == "POST":
        new_model = request.POST.get("new_model")
        new_dataset = request.POST.get("new_dataset")
        existing_model = request.POST.get("existing_model")
        feature_selection = request.POST.get("feature_selection")
        regularization = request.POST.get("regularization")
        epsilon = request.POST.get("epsilon")
        existing_dataset = request.POST.get("existing_dataset")
        dataset_source = request.POST.get("dataset_source")
        dataset_predict = request.POST.get("dataset_predict")

        # convert string input to float
        # to prevent error
        regularization = float(regularization) if regularization != None else 1.0
        epsilon = float(epsilon) if epsilon != None else 0.1

        print("new_model", new_model, flush=True)
        print("new_dataset", new_dataset, flush=True)
        print("existing_model", existing_model, flush=True)
        print("feature_selection", feature_selection, flush=True)
        print("regularization", regularization, flush=True)
        print("epsilon", epsilon, flush=True)
        print("existing_dataset", existing_dataset, flush=True)
        print("dataset_source", dataset_source, flush=True)
        print("dataset_predict", dataset_predict, flush=True)

        response = {}
        if not validate_request(request):
            response["success"] = False
            response["message"] = "Bad Request"
            return JsonResponse(response, content_type="application/json")

        dataset_predict = request.FILES['dataset_predict']
        training_dataframe = pd.read_excel(dataset_predict)

        # get model -
        # get dataset testing -
        # predict! -
        if new_model != "on":
            model = Prediction.objects.get(pk=existing_model)

            result = svr.load_model(dataframe=training_dataframe,
                                    features=Conversion.to_list(Conversion, model.ranked_index),
                                    url=model.dumped_model)
            print("REGRESSOR RESULT", result, flush=True)
        else:
            """
            TODO
            get new model parameters -
                + feature_selection -
                + regularization -
                + epsilon -
            get dataset training
                from existing dataset -
                from new dataset -
                    save new dataset to db
                    save trained model to db
            get dataset testing -
            """
            if new_dataset != "on":
                dataset_profile = DatasetProfile.objects.get(pk=existing_dataset)
                dataset_data = Dataset.objects.filter(profile=dataset_profile)
                dataset_source = None
            else:
                dataset_source = request.FILES['dataset_source']
                save_dataset_to_db(dataset_source)
                dataset_data = None

            """
            1. best prediction => hasil prediksi poverty rate (dictionary, key => city_id)
            2. detail => detail best score (array)
                .best_score => r2
                .lowest_score => rmse
                .jumlah fitur dengan terbaik
                .model terbaik
            3. result => detail hasil r2 dari 10 fitur hingga 96 fitur (array)
                -> [fitur, r2, rmse]
            4. hasil percobaan prediksi per 10 fitur (array)
            5. actual poverty rate
            6. filename
            """
            best_pred, best_score, result, ten_column_predictions, y_true, full_model_file_path = \
                svr.predict(dataset=dataset_data, dataframe=dataset_source, fs_algorithm=feature_selection,
                            C=regularization, epsilon=epsilon)

            regressor = best_score[3]

            result = svr.load_model(dataframe=training_dataframe,
                                    features=best_score[4],
                                    regressor=regressor)

            ranked_index = [str(i) for i in best_score[4]]
            ranked_index = ",".join(ranked_index)

            data_for_input = {
                "feature_selection": feature_selection,
                "reguralization": regularization,
                "epsilon": epsilon,
                "accuracy_value": best_score[0],
                "error_value": best_score[1],
                "pred_result": best_pred,
                "feature_num": best_score[2],
                "ranked_index": ranked_index,
                "dumped_model": full_model_file_path,
            }
            # save model
            save_model_to_db(data_for_input)

            print("NEW REGRESSOR RESULT", result, flush=True)

        return JsonResponse({}, content_type="application/json")

        # best_pred, best_score, result, ten_column_predictions, y_true, filename = \
        #     svr.predict(dataset_data, fs_algorithm, C, epsilon)
        #
        # # get full file path
        # SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # full_model_file_path = SITE_ROOT + "/" + filename
        #
        # ranked_index = [str(i) for i in best_score[4]]
        # ranked_index = ",".join(ranked_index)
        #
        # data_for_input = {
        #     "feature_selection": fs_algorithm,
        #     "reguralization": C,
        #     "epsilon": epsilon,
        #     "accuracy_value": best_score[0],
        #     "error_value": best_score[1],
        #     "pred_result": best_pred,
        #     "feature_num": best_score[2],
        #     "ranked_index": ranked_index,
        #     "dumped_model": full_model_file_path,
        # }

        # save_to_db(data_for_input)
        #
        # y_pred, y_true = list(best_pred.values()), y_true

        # uri = draw_figure(y_pred, y_true)

        # pred_result = []
        # real_data = []
        # for i, (key, value) in enumerate(best_pred.items()):
        #     each_pred_result = {"x": y_true[i], "y": value}
        #     each_real_data = {"x": y_true[i], "y": y_true[i]}
        #     pred_result.append(each_pred_result)
        #     real_data.append(each_real_data)
        # context["best_rmse"] = round(best_score[0], 8)
        # context["best_r2"] = round(best_score[1], 8)
        # context["pred_result"] = json.dumps(pred_result)
        # context["real_data"] = json.dumps(real_data)
        # context["figure"] = uri


def draw_figure(predicted, real):
    print(type(predicted), type(real), flush=True)
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


def save_model_to_db(data_dict):
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
