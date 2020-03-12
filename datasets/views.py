from django.http import JsonResponse
from django.shortcuts import render
from django.forms.models import model_to_dict
from .models import Dataset
from .models import City
import pandas as pd

dataset_column_names = [
    'no', 'city_id', 'BPS_poverty_rate', 'sum_price_car', 'avg_price_car', 'std_price_car', 'sum_sold_car',
    'avg_sold_car', 'std_sold_car', 'sum_viewer_car', 'avg_viewer_car', 'std_viewer_car', 'sum_buyer_car',
    'avg_buyer_car', 'std_buyer_car', 'sum_price_motor', 'avg_price_motor', 'std_price_motor', 'sum_sold_motor',
    'avg_sold_motor', 'std_sold_motor', 'sum_viewer_motor', 'avg_viewer_motor', 'std_viewer_motor',
    'sum_buyer_motor', 'avg_buyer_motor', 'std_buyer_motor', 'sum_price_rumah_sell', 'avg_price_rumah_sell',
    'std_price_rumah_sell', 'sum_sold_rumah_sell', 'avg_sold_rumah_sell', 'std_sold_rumah_sell',
    'sum_viewer_rumah_sell', 'avg_viewer_rumah_sell', 'std_viewer_rumah_sell', 'sum_buyer_rumah_sell',
    'avg_buyer_rumah_sell', 'std_buyer_rumah_sell', 'sum_price_rumah_rent', 'avg_price_rumah_rent',
    'std_price_rumah_rent', 'sum_sold_rumah_rent', 'avg_sold_rumah_rent', 'std_sold_rumah_rent',
    'sum_viewer_rumah_rent', 'avg_viewer_rumah_rent', 'std_viewer_rumah_rent', 'sum_buyer_rumah_rent',
    'avg_buyer_rumah_rent', 'std_buyer_rumah_rent', 'sum_price_apt_sell', 'avg_price_apt_sell',
    'std_price_apt_sell', 'sum_sold_apt_sell', 'avg_sold_apt_sell', 'std_sold_apt_sell', 'sum_viewer_apt_sell',
    'avg_viewer_apt_sell', 'std_viewer_apt_sell', 'sum_buyer_apt_sell', 'avg_buyer_apt_sell', 'std_buyer_apt_sell',
    'sum_price_apt_rent', 'avg_price_apt_rent', 'std_price_apt_rent', 'sum_sold_apt_rent', 'avg_sold_apt_rent',
    'std_sold_apt_rent', 'sum_viewer_apt_rent', 'avg_viewer_apt_rent', 'std_viewer_apt_rent', 'sum_buyer_apt_rent',
    'avg_buyer_apt_rent', 'std_buyer_apt_rent', 'sum_price_land_sell', 'avg_price_land_sell', 'std_price_land_sell',
    'sum_sold_land_sell', 'avg_sold_land_sell', 'std_sold_land_sell', 'sum_viewer_land_sell',
    'avg_viewer_land_sell', 'std_viewer_land_sell', 'sum_buyer_land_sell', 'avg_buyer_land_sell',
    'std_buyer_land_sell', 'sum_price_land_rent', 'avg_price_land_rent', 'std_price_land_rent',
    'sum_sold_land_rent', 'avg_sold_land_rent', 'std_sold_land_rent', 'sum_viewer_land_rent',
    'avg_viewer_land_rent', 'std_viewer_land_rent', 'sum_buyer_land_rent', 'avg_buyer_land_rent',
    'std_buyer_land_rent'
]

city_column_names = [
    'id', 'name', 'latitude', 'longitude', 'province'
]

def new(request):
    if request.method == 'GET':
        return render(request, 'datasets/new.html', {})
    else:
        source_file = request.FILES['dataset_source']
        file_extension = repr(str(source_file).split('.')[-1])

        dataframe = pd.read_excel(source_file)

        source_data = []
        for row in dataframe.iloc[0:, :].values:
            row_data = []
            for cell in row:
                row_data.append(cell)
            zipped_data = dict(zip(dataset_column_names, row_data))

            # make city id integer instead of float
            zipped_data['city_id'] = int(zipped_data['city_id'])

            dataset_insert(zipped_data)

        return render(request, 'datasets/new.html', {})


def list(request):
    table_header = dataset_column_names
    table_data = Dataset.objects.all()

    dataset_data = [data.__dict__ for data in table_data]

    context = {
        'table_header': table_header,
        'table_data': dataset_data,
    }

    return render(request, 'datasets/list.html', context)


def dataset_insert(data):
    return Dataset.objects.create(**data)


def city_list(request):
    table_header = city_column_names
    table_data = City.objects.all()

    city_data = [model_to_dict(data) for data in table_data]

    context = {
        'table_header': table_header,
        'table_data': city_data,
    }

    return render(request, 'datasets/city_list.html', context)


def city_detail(request):
    if request.method == 'GET':
        city_id = request.GET.get('city_id')
        city = City.objects.get(pk=city_id)
        city_response = model_to_dict(city)

        context = {}
        context['success'] = True
        context['data'] = city_response

        return JsonResponse(context, content_type="application/json")
