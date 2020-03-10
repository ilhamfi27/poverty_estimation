from django.shortcuts import render

def index(request):
    return render(request, 'index.html', {})


def predictor(request):
    return render(request, 'predictor.html', {})


def mapping(request):
    return render(request, 'mapping.html', {})
