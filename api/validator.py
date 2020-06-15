"""
validator for predicts

"""

def validate_request(request):
    # checkboxes
    default_model = True if request.POST.get("default_model") == "on" else False
    new_model = True if request.POST.get("new_model") == "on" else False
    new_dataset = True if request.POST.get("new_dataset") == "on" else False

    # selections
    existing_model = request.POST.get("existing_model")
    feature_selection = request.POST.get("feature_selection")

    # normal input
    regularization = request.POST.get("regularization")
    epsilon = request.POST.get("epsilon")
    existing_dataset = request.POST.get("existing_dataset")
    dataset_source = request.POST.get("dataset_source")
    dataset_predict = request.POST.get("dataset_predict")

    if new_model == "on":
        if feature_selection == "":
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


def saving_model_validation(request):
    new_model_name = request.POST.get("new_model_name")
    if new_model_name == "":
        return False

    return True
