import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, urllib, base64, io
from datetime import datetime
from rest_framework import views
from rest_framework.response import Response
from rest_framework import status as st
from rest_framework import mixins, generics
from rest_framework.response import Response
from django.forms.models import model_to_dict
from predicts.models import MachineLearningModel, Prediction, PredictionResult
from datasets.models import DatasetProfile, CityGeography, City, Dataset
from api.serializers import DatasetProfileSerializer, ModelMachineLearningSerializer, PredictionSerializer, \
    PredictonResultSerializer
from api.validator import *
from final_task.util import Conversion
import final_task.util as util
from predicts import svr

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


class DatasetProfileList(views.APIView):

    def post(self, request, format=None):
        print(request.data, flush=True)
        serializer = DatasetProfileSerializer(data=request.data)

        if serializer.is_valid():
            name = request.data["name"]
            valid_date = request.data["valid_date"]
            type = request.data["type"]
            source_file = request.FILES['source_file']

            file_extension = repr(str(source_file).split('.')[-1])
            dataframe = pd.read_excel(source_file)
            dataframe_data = np.nan_to_num(dataframe.iloc[0:, :].values)
            total_row = len(dataframe_data)

            dataset_profile = DatasetProfile.objects.create(name=name, valid_date=valid_date, total_row=total_row,
                                                            type=type)

            source_data = []
            for row in dataframe_data:
                row_data = []
                for cell in row:
                    row_data.append(cell)
                zipped_data = dict(zip(dataset_column_names, row_data))

                # make city id integer instead of float
                zipped_data['city_id'] = int(zipped_data['city_id'])
                zipped_data['profile'] = dataset_profile

                self.dataset_insert(zipped_data)

            serialized = serializer.data
            serialized['id'] = dataset_profile.id
            serialized['created_at'] = dataset_profile.created_at
            serialized['type'] = dataset_profile.type
            return Response(serialized, status=st.HTTP_201_CREATED)

        return Response(serializer.errors, status=st.HTTP_400_BAD_REQUEST)

    def dataset_insert(self, data):
        return Dataset.objects.create(**data)


class DatasetProfileDetail(mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           generics.GenericAPIView):
    queryset = DatasetProfile.objects.all()
    serializer_class = DatasetProfileSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class DatasetDetail(views.APIView):
    queryset = DatasetProfile.objects.all()
    serializer_class = DatasetProfileSerializer

    def get(self, request, *args, **kwargs):
        dataset_profile = self.queryset.get(pk=kwargs['pk'])
        table_data = Dataset.objects.filter(profile=dataset_profile)

        dataset_data = [model_to_dict(data) for data in table_data]

        response = {
            'dataset_data': dataset_data
        }
        return Response(response, status=st.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        dataset_profile = self.queryset.get(pk=kwargs['pk'])
        Dataset.objects.filter(profile=dataset_profile).delete()
        dataset_profile.delete()
        return Response(status=st.HTTP_200_OK)


class ModelDetail(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  generics.GenericAPIView):
    queryset = MachineLearningModel.objects.all()
    serializer_class = ModelMachineLearningSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ModelList(mixins.CreateModelMixin,
                generics.GenericAPIView):
    queryset = MachineLearningModel.objects.all()
    serializer_class = ModelMachineLearningSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PredictionDetail(mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       generics.GenericAPIView):
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class PredictionResultDetail(mixins.RetrieveModelMixin,
                             generics.GenericAPIView):
    queryset = Prediction.objects.all()
    serializer_class = PredictonResultSerializer

    def get(self, request, *args, **kwargs):
        prediction = self.queryset.get(pk=kwargs['pk'])
        result = PredictionResult.objects.filter(prediction=prediction)
        predict_result = []
        for r in result:
            city = City.objects.filter(pk=r.city.id).first()
            res = model_to_dict(r)
            res['province'] = city.province
            res['city'] = city.name
            predict_result.append(res)

        response = model_to_dict(prediction)
        response["predict_result"] = predict_result
        response["sorted_feature"] = util.rank_items([int(i) for i in prediction.ranked_index.split(",")])
        return Response(response, status=st.HTTP_200_OK)


class Predictor(views.APIView):

    def post(self, request, format=None):
        print(request.data, flush=True)
        # checkboxes
        default_model = True if "default_model" in request.data else False
        new_model = True if "new_model" in request.data else False

        # normal input
        existing_dataset = request.data["existing_dataset"]
        existing_training_dataset = request.data["existing_training_dataset"]

        response = {}
        if not validate_request(request):
            response["success"] = False
            response["message"] = ["Failed to predict due to incompatible data input"]
            return Response(response, status=st.HTTP_400_BAD_REQUEST)

        dataset_training_profile = DatasetProfile.objects.get(pk=existing_training_dataset)
        dataset_training_data = Dataset.objects.filter(profile=dataset_training_profile)
        now_time = datetime.now()

        # get model -
        # get dataset testing -
        # predict! -
        if default_model:
            # get full default file path
            SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            full_model_file_path = SITE_ROOT + "/svr_best.sav"

            best_feature_list = [
                36, 63, 60, 48, 57, 54, 51, 6, 9, 66,
                18, 15, 69, 38, 3, 13, 0, 24, 21, 27,
                33, 30, 42, 45, 87, 72, 84, 14, 75, 12,
                93, 39, 61, 65, 62, 90, 86, 89, 50, 49,
                71, 52, 85, 78, 44, 81, 64, 37, 74, 68,
                2, 67, 73, 47, 1, 20, 53, 25, 88, 59,
                70, 26, 31, 34, 8, 79, 95, 82, 56, 23,
                28, 11, 94, 76, 32, 43, 83, 55, 58, 10,
                92, 77, 91, 80, 29, 46, 19, 7, 35, 22,
                16, 40, 4, 17, 41, 5,
            ]

            result, city_result = svr.load_model(
                dataset=dataset_training_data,
                features=best_feature_list,
                url=full_model_file_path)

            poverty_each_city = []
            geojson_features = []
            for city, poverty_rate in city_result.items():
                city = City.objects.get(pk=city)
                geojson = CityGeography.objects.filter(city=city).first()
                data = {
                    "city": city.name,
                    "province": city.province,
                    "poverty_rate": '{0:.4g}'.format(poverty_rate),
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
                            "poverty_rate": '{0:.4g}'.format(poverty_rate),
                        },
                        "geometry": json.loads(geojson.area_geometry)
                    }
                    geojson_features.append(feature)

            region_geojson = {
                "type": "FeatureCollection",
                "features": geojson_features
            }

            regularization = 10
            epsilon = 0.5
            accuracy_value = 0.42765
            error_value = 13.882
            feature_num = 90

            data_for_input = {
                "name": dataset_training_profile.name + " - " + now_time.strftime("%d-%m-%Y, %H:%M:%S"),
                "feature_selection": None,
                "regularization": regularization,
                "epsilon": epsilon,
                "accuracy_value": accuracy_value,
                "error_value": error_value,
                "pred_result": city_result,
                "feature_num": feature_num,
                "ranked_index": best_feature_list,
            }
            # save model
            self.save_prediction_to_db(data_for_input)

            response["success"] = True
            response["new_model"] = False
            response["best_model"] = True
            response["result_cities"] = poverty_each_city
            response["region_geojson"] = region_geojson
            response["accuracy_value"] = accuracy_value
            response["error_value"] = error_value
            response["regularization"] = regularization
            response["epsilon"] = epsilon
            response["feature_num"] = feature_num
            response["sorted_feature"] = util.rank_items(ranked_index=best_feature_list)
            response["result_cities"] = poverty_each_city
            response["region_geojson"] = region_geojson
            return Response(response, status=st.HTTP_200_OK)
        else:
            if new_model:
                feature_selection = request.data["feature_selection"]
                regularization = request.data["regularization"]
                epsilon = request.data["epsilon"]

                # convert string input to float
                # to prevent error
                regularization = float(regularization) if regularization != None and regularization != "" else 1.0
                epsilon = float(epsilon) if epsilon != None and epsilon != "" else 0.1

                dataset_data = None
                dataset_source = None

                dataset_profile = DatasetProfile.objects.get(pk=existing_dataset)
                dataset_data = Dataset.objects.filter(profile=dataset_profile)

                """
                proses training sekaligus prediksi
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

                ranked_index = [str(i) for i in best_score[4]]
                ranked_index = ",".join(ranked_index)

                data_for_input = {
                    "name": dataset_training_profile.name + " - " + now_time.strftime("%d-%m-%Y, %H:%M:%S"),
                    "feature_selection": feature_selection,
                    "regularization": regularization,
                    "epsilon": epsilon,
                    "accuracy_value": best_score[0],
                    "error_value": best_score[1],
                    "pred_result": best_pred[1],
                    "feature_num": best_score[2],
                    "ranked_index": ranked_index,
                }
                # save model
                self.save_prediction_to_db(data_for_input)

                sorted_feature = util.rank_items(ranked_index=best_score[4])

                poverty_each_city = []
                geojson_features = []
                for city, result in best_pred[1].items():
                    city = City.objects.get(pk=city)
                    geojson = CityGeography.objects.filter(city=city).first()
                    data = {
                        "city": city.name,
                        "province": city.province,
                        "poverty_rate": '{0:.4g}'.format(result),
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
                                "poverty_rate": '{0:.4g}'.format(result),
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
                response["best_model"] = False
                response["accuracy_value"] = best_score[0]
                response["error_value"] = best_score[1]
                response["regularization"] = regularization
                response["epsilon"] = epsilon
                response["feature_num"] = best_score[2]
                response["sorted_feature"] = sorted_feature
                response["result_chart"] = self.draw_figure(best_pred[0], y_true)
                response["result_cities"] = poverty_each_city
                response["region_geojson"] = region_geojson
                response["feature_selection"] = feature_selection
                response["ranked_index"] = ranked_index
                response["dumped_model"] = full_model_file_path
                return Response(response, status=st.HTTP_200_OK)
            else:
                existing_model = request.data["existing_model"]
                model = MachineLearningModel.objects.get(pk=existing_model)

                result, city_result = svr.load_model(
                    dataset=dataset_training_data,
                    features=Conversion.to_list(Conversion, model.ranked_index),
                    url=model.dumped_model)

                ranked_feature = model.ranked_index.split(",")
                ranked_features = [int(i) for i in ranked_feature]
                sorted_feature = util.rank_items(ranked_index=ranked_features)

                poverty_each_city = []
                geojson_features = []
                for city, poverty_rate in city_result.items():
                    city = City.objects.get(pk=city)
                    geojson = CityGeography.objects.filter(city=city).first()
                    data = {
                        "city": city.name,
                        "province": city.province,
                        "poverty_rate": '{0:.4g}'.format(poverty_rate),
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
                                "poverty_rate": '{0:.4g}'.format(poverty_rate),
                            },
                            "geometry": json.loads(geojson.area_geometry)
                        }
                        geojson_features.append(feature)

                region_geojson = {
                    "type": "FeatureCollection",
                    "features": geojson_features
                }

                data_for_input = {
                    "name": dataset_training_profile.name + " - " + now_time.strftime("%d-%m-%Y, %H:%M:%S"),
                    "feature_selection": model.feature_selection,
                    "regularization": model.regularization,
                    "epsilon": model.epsilon,
                    "accuracy_value": model.accuracy_value,
                    "error_value": model.error_value,
                    "pred_result": city_result,
                    "feature_num": model.feature_num,
                    "ranked_index": model.ranked_index,
                }
                # save model
                self.save_prediction_to_db(data_for_input)

                response["success"] = True
                response["new_model"] = False
                response["best_model"] = False
                response["accuracy_value"] = model.accuracy_value
                response["error_value"] = model.error_value
                response["regularization"] = model.regularization
                response["epsilon"] = model.epsilon
                response["feature_num"] = model.feature_num
                response["sorted_feature"] = sorted_feature
                response["result_cities"] = poverty_each_city
                response["region_geojson"] = region_geojson
                return Response(response, status=st.HTTP_200_OK)

    def save_prediction_to_db(self, data_dict):
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

    def draw_figure(self, predicted, real):
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
