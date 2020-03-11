from django.shortcuts import render

def index(request):
    return render(request, 'predicts/index.html', {})


def predictor(request):
    return render(request, 'predicts/predictor.html', {})


def mapping(request):
    return render(request, 'predicts/mapping.html', {})
