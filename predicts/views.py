from django.shortcuts import render

def index(request):
    return render(request, 'index.html', {})


def dataset_insert(request):
    return render(request, 'dataset_insert.html', {})


def dataset_list(request):
    return render(request, 'dataset_list.html', {})


def predictor(request):
    return render(request, 'predictor.html', {})


def predict_mapping(request):
    return render(request, 'predict_mapping.html', {})
