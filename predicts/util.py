import numpy as np
import matplotlib as plt
import io
import urllib, base64

def humanize_item_name(item):
    item_name = {
        "car": "Cars",
        "motor": "Motorcycle",
        "land_rent": "Land Rent",
        "land_sell": "Land Sale",
        "apt_rent": "Apartment Rent",
        "apt_sell": "Apartment Sale",
        "rumah_rent": "House Rent",
        "rumah_sell": "House Sale",
    }
    result = item.replace(item, item_name[item])
    return result

def rank_items(ranked_index=[]):
    dataset_column_names = np.array([
        'sum_price_car', 'avg_price_car', 'std_price_car', 'sum_sold_car',
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
    ])

    total_items = {} # nampung total dari setiap item
    item_counts = {} # nampung perhitungan setiap item
    item_rank = [] # nampung ranking dari item

    sorted_header = dataset_column_names[ranked_index[:]] # sortir kolom sesuai hasil seleksi fitur
    all_items = ["_".join(s.split("_")[2:]) for s in sorted_header] # tampung semua nama item ex: apt_sell
    items = np.unique(all_items) # mengambil item secara unique ex: apt, car, motor

    # set total item dan perhitungan setiap item
    for i in items:
        total_items[i] = all_items.count(i)
        item_counts[i] = 0

    # sorting dilakukan dengan menambahkan item ke dalam item_rank
    for i in all_items:
        if i in items:
            item_counts[i] += 1

            # jika jumlah item sudah mencapai total items, maka item akan dimasukkan ke dalam item_rank
            if item_counts[i] == total_items[i]:
                item_rank.append(i)

    return [humanize_item_name(i) for i in item_rank]



def humanize_feature_name(feature):
    aggregation = {
        "avg": "average of",
        "sum": "sum of",
        "std": "standard deviation of",
    }
    s = feature.split("_")
    obj = s[2:]
    result = s[0].replace(s[0], aggregation[s[0]]) + " " + " ".join(obj) + " " + s[1]
    return result
