"""
validator for predicts

"""

def validate_request(request):
    new_model = request.POST.get("new_model")
    new_dataset = request.POST.get("new_dataset")
    existing_model = request.POST.get("existing_model")
    feature_selection = request.POST.get("feature_selection")
    regularization = request.POST.get("regularization")
    epsilon = request.POST.get("epsilon")
    existing_dataset = request.POST.get("existing_dataset")
    dataset_source = request.POST.get("dataset_source")
    dataset_predict = request.POST.get("dataset_predict")

    if new_model == "on":
        if feature_selection == "" or regularization == "" or epsilon == "":
            return False

        if new_dataset == "on":
            if dataset_source == "":
                return False
        else:
            if existing_dataset == "":
                return False
    else:
        if existing_model == "":
            return False


    if dataset_predict == "":
        return False

    return True