import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVR
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneOut
from django.forms.models import model_to_dict
from skfeature.function.statistical_based import f_score
from skfeature.function.statistical_based import chi_square
from skfeature.function.statistical_based import CFS


def predict(fs_algorithm=None, dataframe=None, dataset=None, C=1.0, epsilon=0.1):
    sc = MinMaxScaler(feature_range=(0,10))
    best_sort_feature = []

    if dataframe == None and dataset == None:
        return None

    if dataset:
        dataset_data = [model_to_dict(data) for data in dataset]

        df = pd.DataFrame(dataset_data)

        city_id = np.asarray(df['city'])
        raw_X = np.asarray(df.loc[:, 'sum_price_car':'std_buyer_land_rent'])  # features
        raw_y = np.asarray(df['BPS_poverty_rate'])  # label

    if dataframe:
        df = pd.read_excel(dataframe)

        city_id = np.asarray(df['city_id'])
        raw_X = np.asarray(df.loc[:, 'sum_price_car':'std_buyer_land_rent'])  # features
        raw_y = np.asarray(df['BPS_poverty_rate'])  # label


    # 2. pre-processing
    clean_X = np.nan_to_num(raw_X)
    clean_y = np.nan_to_num(raw_y)

    # 3. normalization
    sc.fit(raw_X)
    X = np.array(sc.transform(clean_X))
    y = np.array(clean_y)

    if fs_algorithm == "f_score":
        ranked_index = f_score.f_score(X, y, mode="index")
    elif fs_algorithm == "chi_square":
        X_feature = X.astype(int)
        y_label = y.astype(int)
        ranked_index = chi_square.chi_square(X_feature, y_label, mode="index")
    elif fs_algorithm == "cfs":
        ranked_index = CFS.cfs(X, y)

    for row in X:
        row_array = []
        for num, feature_idx in enumerate(ranked_index):
            row_array.append(row[feature_idx])
        best_sort_feature.append(row_array)


    # 5. get best feature predict score
    best_pred, best_score, result, ten_column_predictions \
        = trainf(best_sort_feature, y, C, epsilon)

    now_unix_timestamp = str(datetime.utcnow().timestamp())
    time = now_unix_timestamp.split(".")[0]

    # set filename
    filename = "dumped_model/svr_"+ fs_algorithm + "_" + time +"_.sav"
    # get full file path
    SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_model_file_path = SITE_ROOT + "/" + filename

    # get regressor
    regressor = best_score[3]
    pickle.dump(regressor, open(filename, 'wb'))

    """
    RETURN VALUES
    hasil return dari prediksi SVR
    """

    # modified best prediction return value
    best_pred = [best_pred, dict(zip(city_id, best_pred))]

    # nambahin list ranked index dari pecahan 10 terbaik
    best_score.append(ranked_index[:best_score[2]])

    y_true = y

    """
    1. best prediction => hasil prediksi poverty rate (dictionary, key => city_id)
    2. detail => detail best score (array)
        .best_score => r2
        .lowest_score => rmse
        .jumlah fitur dengan terbaik
        .model terbaik
        .urutan fitur terbaik
    3. result => detail hasil r2 dari 10 fitur hingga 96 fitur (array)
        -> [fitur, r2, rmse]
    4. hasil percobaan prediksi per 10 fitur (array)
    5. actual poverty rate
    6. filename
    """
    return best_pred, best_score, result, ten_column_predictions, y_true, full_model_file_path


def trainf(X, y, C=1.0, epsilon=0.1):
    repeat = 0
    X = np.array(X)
    X_column = X.shape[1]
    result = []
    best_score = 0
    lowest_error = 0
    best_pred = []
    ten_column_predictions = []

    while repeat < X_column - 1:
        score = []
        if (X_column - repeat) < 10:
            repeat += (X_column - repeat)
        else:
            repeat += 10

        # predict
        regressor = SVR(gamma='scale', C=C, epsilon=epsilon)
        y_pred = []
        y_true = []

        X_selected = X[0:, 0:repeat]
        loo = LeaveOneOut()
        loo.get_n_splits(X)

        for train_index, test_index in loo.split(X_selected):
            X_train, X_test = X_selected[train_index], X_selected[test_index]
            y_train, y_test = y[train_index], y[test_index]
            regressor.fit(X_train, y_train)
            y_pred.extend(regressor.predict(X_test))
            y_true.extend(y_test)

        # count accuracy prediction
        accuracy_score = r2_score(y_true, y_pred)
        rmse_score = mean_squared_error(y_true, y_pred)

        score.append(repeat)
        score.append(accuracy_score)
        score.append(rmse_score)

        result.append(score)

        ten_column_predictions.append(y_pred)

        if best_score < accuracy_score:
            best_pred = y_pred
            best_score = accuracy_score
            lowest_error = rmse_score
            best_feature_num = repeat
            best_regressor = regressor

    """
    1. best prediction => hasil prediksi poverty rate (array)
    2. detail => detail best score (array)
        .best_score => r2
        .lowest_score => rmse
        .jumlah fitur dengan terbaik
        .model terbaik
    3. result => detail hasil r2 dari 10 fitur hingga 96 fitur (array)
        -> [fitur, r2, rmse]
    4. hasil percobaan prediksi per 10 fitur (array)
    """

    return best_pred, [best_score, lowest_error, best_feature_num, best_regressor], result, ten_column_predictions


def load_model(features=None, dataframe=None, regressor=None, url=None):
    sc = MinMaxScaler(feature_range=(0,10))

    sorted_feature = []

    df = pd.DataFrame(dataframe)
    city_id = np.asarray(df['city_id'])
    raw_X = np.asarray(df.loc[:, 'sum_price_car':'std_buyer_land_rent'])  # features

    # 2. pre-processing
    clean_X = np.nan_to_num(raw_X)

    # 3. normalization
    sc.fit(raw_X)
    X = np.array(sc.transform(clean_X))

    X = X[:, features[:]]

    # load the model from disk
    if url:
        print("=======================================================", flush=True)
        print(url, flush=True)
        print("=======================================================", flush=True)
        loaded_model = pickle.load(open(url, 'rb'))
        result = loaded_model.predict(X)

    if regressor:
        result = regressor.predict(X)
    return result, dict(zip(city_id, result))
