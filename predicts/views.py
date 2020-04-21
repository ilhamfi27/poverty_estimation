from django.http import JsonResponse
from django.shortcuts import render, redirect
from datasets.models import Dataset, City, DatasetProfile, CityGeography
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
                                                 "regularization",
                                                 "epsilon",
                                                 "accuracy_value",
                                                 "error_value")
    dataset_profiles = DatasetProfile.objects.values("id",
                                                 "valid_date",
                                                 "total_row")

    print(dataset_profiles, flush=True)

    prediction_data = [dict(zip(prediction_column_names, data)) for data in predictions]


    context = {
        'dataset_column_names': dataset_column_names,
        'chart_data': [],
        'real_data': [],
        'table_header': prediction_result_table_header,
        'prediction_data': prediction_data,
        'dataset_profiles_data': dataset_profiles,
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

        # convert string input to float
        # to prevent error
        regularization = float(regularization) if regularization != None and regularization != "" else 1.0
        epsilon = float(epsilon) if epsilon != None and epsilon != "" else 0.1

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

            result, city_result, y_true = svr.load_model(
                                dataframe=training_dataframe,
                                features=Conversion.to_list(Conversion, model.ranked_index),
                                url=model.dumped_model)

            ranked_feature = model.ranked_index.split(",")
            feature_names = dataset_column_names[2:]
            sorted_feature = [humanize_feature_name(feature_names[int(i)]) for i in ranked_feature]

            poverty_each_city = []
            geojson_features = []
            for city, poverty_rate in city_result.items():
                city = City.objects.get(pk=city)
                geojson = CityGeography.objects.filter(city=city).first()
                data = {
                    "city": city.name,
                    "province": city.province,
                    "poverty_rate": poverty_rate,
                    "latitude": city.latitude,
                    "longitude": city.longitude,
                }
                poverty_each_city.append(data)

                if geojson is not None:
                    feature = {
                        "type": "Feature",
                        "properties": {
                            "region": geojson.city.name,
                            "province": geojson.city.province,
                            "poverty_rate": poverty_rate,
                        },
                        "geometry": json.loads(geojson.area_geometry)
                    }
                    geojson_features.append(feature)

            region_geojson = {
                "type": "FeatureCollection",
                "features": geojson_features
            }

            response["success"] = True
            response["new_model"] = True
            response["r2"] = model.accuracy_value
            response["rmse"] = model.error_value
            response["regularization"] = model.regularization
            response["epsilon"] = model.epsilon
            response["feature_num"] = model.feature_num
            response["sorted_feature"] = sorted_feature
            response["result_chart"] = draw_figure(result, y_true)
            response["result_cities"] = poverty_each_city
            response["region_geojson"] = region_geojson
            return JsonResponse(response, content_type="application/json")
        else:
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
                .ranked index
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
                "regularization": regularization,
                "epsilon": epsilon,
                "accuracy_value": best_score[0],
                "error_value": best_score[1],
                "pred_result": best_pred[1],
                "feature_num": best_score[2],
                "ranked_index": ranked_index,
                "dumped_model": full_model_file_path,
            }
            # save model
            save_model_to_db(data_for_input)

            feature_names = dataset_column_names[2:]
            sorted_feature = [humanize_feature_name(feature_names[i]) for i in best_score[4]]

            poverty_each_city = []
            geojson_features = []
            for city, result in best_pred[1].items():
                city = City.objects.get(pk=city)
                geojson = CityGeography.objects.filter(city=city).first()
                data = {
                    "city": city.name,
                    "province": city.province,
                    "poverty_rate": result,
                    "latitude": city.latitude,
                    "longitude": city.longitude,
                }
                poverty_each_city.append(data)

                if geojson is not None:
                    feature = {
                        "type": "Feature",
                        "properties": {
                            "region": geojson.city.name,
                            "province": geojson.city.province,
                            "poverty_rate": result,
                        },
                        "geometry": json.loads(geojson.area_geometry)
                    }
                    geojson_features.append(feature)

            region_geojson = {
                "type": "FeatureCollection",
                "features": geojson_features
            }

            response["success"] = True
            response["new_model"] = True
            response["r2"] = best_score[0]
            response["rmse"] = best_score[1]
            response["regularization"] = regularization
            response["epsilon"] = epsilon
            response["feature_num"] = best_score[2]
            response["sorted_feature"] = sorted_feature
            response["result_chart"] = draw_figure(best_pred[0], y_true)
            response["result_cities"] = poverty_each_city
            response["region_geojson"] = region_geojson
            return JsonResponse(response, content_type="application/json")


def humanize_feature_name(feature):
    aggregation = {
        "avg": "average of",
        "sum": "sum of",
        "std": "standard deviation of",
    }
    s = feature.split("_")
    obj = s[2:]
    result = s[0].replace(s[0], aggregation[s[0]]) + " " + " ".join(obj) + " " + s[1]
    return result


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


def mapping(request):
    return render(request, 'predicts/mapping.html', {})


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
