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

    existing_dataset = request.data["existing_dataset"]
    existing_training_dataset = request.data["existing_training_dataset"]

    if new_model == "on":
        if feature_selection == "":
            return False

        else:
            if existing_dataset == "":
                return False
    else:
        if existing_model == "":
            return False

    if existing_dataset == "":
        return False

    if existing_training_dataset == "":
        return False

    return True


def saving_model_validation(request):
    new_model_name = request.POST.get("new_model_name")
    if new_model_name == "":
        return False

    return True
