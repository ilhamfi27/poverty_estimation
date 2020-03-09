from django.shortcuts import render

def index(request):
    return render(request, 'index.html', {})

def dataset_insert(request):
    return render(request, 'dataset_insert.html', {})
