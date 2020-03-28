import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVR
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneOut
from django.forms.models import model_to_dict
from skfeature.function.statistical_based import f_score
from skfeature.function.statistical_based import chi_square
from skfeature.function.statistical_based import CFS


def predict(dataset_data, fs_algorithm, C=1.0, epsilon=0.1):
    sc = MinMaxScaler(feature_range=(0,10))
    dataset_data = [model_to_dict(data) for data in dataset_data]

    best_sort_feature = []

    df = pd.DataFrame(dataset_data)
    city_id = df.iloc[0:, 1].values # city id
    raw_X = df.iloc[0:, 3:].values # dataset
    raw_y = df.iloc[0:, 2].values # label

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


    """
    RETURN VALUES
    hasil return dari prediksi SVR
    """

    # modified best prediction return value
    best_pred = dict(zip(city_id, best_pred))

    y_true = y
    return best_pred, best_score, result, ten_column_predictions, y_true


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

    return best_pred, [best_score, lowest_error], result, ten_column_predictions
