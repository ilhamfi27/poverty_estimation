from django.shortcuts import render

def new(request):
    return render(request, 'new.html', {})


def list(request):
    return render(request, 'list.html', {})