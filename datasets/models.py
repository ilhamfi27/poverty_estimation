from django.db import models

class City(models.Model):
    name = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    province = models.CharField(max_length=40, default="")
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'cities'


class DatasetProfile(models.Model):
    name = models.CharField(max_length=50, default="")
    total_row = models.IntegerField(default=0)
    valid_date = models.DateField(auto_now_add=True)
    type = models.CharField(max_length=50, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dataset_profile'


class Dataset(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
    profile = models.ForeignKey(DatasetProfile, on_delete=models.CASCADE, blank=True, null=True, default=None)
    BPS_poverty_rate = models.FloatField(default=0)
    sum_price_car = models.FloatField(default=0)
    avg_price_car = models.FloatField(default=0)
    std_price_car = models.FloatField(default=0)
    sum_sold_car = models.FloatField(default=0)
    avg_sold_car = models.FloatField(default=0)
    std_sold_car = models.FloatField(default=0)
    sum_viewer_car = models.FloatField(default=0)
    avg_viewer_car = models.FloatField(default=0)
    std_viewer_car = models.FloatField(default=0)
    sum_buyer_car = models.FloatField(default=0)
    avg_buyer_car = models.FloatField(default=0)
    std_buyer_car = models.FloatField(default=0)
    sum_price_motor = models.FloatField(default=0)
    avg_price_motor = models.FloatField(default=0)
    std_price_motor = models.FloatField(default=0)
    sum_sold_motor = models.FloatField(default=0)
    avg_sold_motor = models.FloatField(default=0)
    std_sold_motor = models.FloatField(default=0)
    sum_viewer_motor = models.FloatField(default=0)
    avg_viewer_motor = models.FloatField(default=0)
    std_viewer_motor = models.FloatField(default=0)
    sum_buyer_motor = models.FloatField(default=0)
    avg_buyer_motor = models.FloatField(default=0)
    std_buyer_motor = models.FloatField(default=0)
    sum_price_rumah_sell = models.FloatField(default=0)
    avg_price_rumah_sell = models.FloatField(default=0)
    std_price_rumah_sell = models.FloatField(default=0)
    sum_sold_rumah_sell = models.FloatField(default=0)
    avg_sold_rumah_sell = models.FloatField(default=0)
    std_sold_rumah_sell = models.FloatField(default=0)
    sum_viewer_rumah_sell = models.FloatField(default=0)
    avg_viewer_rumah_sell = models.FloatField(default=0)
    std_viewer_rumah_sell = models.FloatField(default=0)
    sum_buyer_rumah_sell = models.FloatField(default=0)
    avg_buyer_rumah_sell = models.FloatField(default=0)
    std_buyer_rumah_sell = models.FloatField(default=0)
    sum_price_rumah_rent = models.FloatField(default=0)
    avg_price_rumah_rent = models.FloatField(default=0)
    std_price_rumah_rent = models.FloatField(default=0)
    sum_sold_rumah_rent = models.FloatField(default=0)
    avg_sold_rumah_rent = models.FloatField(default=0)
    std_sold_rumah_rent = models.FloatField(default=0)
    sum_viewer_rumah_rent = models.FloatField(default=0)
    avg_viewer_rumah_rent = models.FloatField(default=0)
    std_viewer_rumah_rent = models.FloatField(default=0)
    sum_buyer_rumah_rent = models.FloatField(default=0)
    avg_buyer_rumah_rent = models.FloatField(default=0)
    std_buyer_rumah_rent = models.FloatField(default=0)
    sum_price_apt_sell = models.FloatField(default=0)
    avg_price_apt_sell = models.FloatField(default=0)
    std_price_apt_sell = models.FloatField(default=0)
    sum_sold_apt_sell = models.FloatField(default=0)
    avg_sold_apt_sell = models.FloatField(default=0)
    std_sold_apt_sell = models.FloatField(default=0)
    sum_viewer_apt_sell = models.FloatField(default=0)
    avg_viewer_apt_sell = models.FloatField(default=0)
    std_viewer_apt_sell = models.FloatField(default=0)
    sum_buyer_apt_sell = models.FloatField(default=0)
    avg_buyer_apt_sell = models.FloatField(default=0)
    std_buyer_apt_sell = models.FloatField(default=0)
    sum_price_apt_rent = models.FloatField(default=0)
    avg_price_apt_rent = models.FloatField(default=0)
    std_price_apt_rent = models.FloatField(default=0)
    sum_sold_apt_rent = models.FloatField(default=0)
    avg_sold_apt_rent = models.FloatField(default=0)
    std_sold_apt_rent = models.FloatField(default=0)
    sum_viewer_apt_rent = models.FloatField(default=0)
    avg_viewer_apt_rent = models.FloatField(default=0)
    std_viewer_apt_rent = models.FloatField(default=0)
    sum_buyer_apt_rent = models.FloatField(default=0)
    avg_buyer_apt_rent = models.FloatField(default=0)
    std_buyer_apt_rent = models.FloatField(default=0)
    sum_price_land_sell = models.FloatField(default=0)
    avg_price_land_sell = models.FloatField(default=0)
    std_price_land_sell = models.FloatField(default=0)
    sum_sold_land_sell = models.FloatField(default=0)
    avg_sold_land_sell = models.FloatField(default=0)
    std_sold_land_sell = models.FloatField(default=0)
    sum_viewer_land_sell = models.FloatField(default=0)
    avg_viewer_land_sell = models.FloatField(default=0)
    std_viewer_land_sell = models.FloatField(default=0)
    sum_buyer_land_sell = models.FloatField(default=0)
    avg_buyer_land_sell = models.FloatField(default=0)
    std_buyer_land_sell = models.FloatField(default=0)
    sum_price_land_rent = models.FloatField(default=0)
    avg_price_land_rent = models.FloatField(default=0)
    std_price_land_rent = models.FloatField(default=0)
    sum_sold_land_rent = models.FloatField(default=0)
    avg_sold_land_rent = models.FloatField(default=0)
    std_sold_land_rent = models.FloatField(default=0)
    sum_viewer_land_rent = models.FloatField(default=0)
    avg_viewer_land_rent = models.FloatField(default=0)
    std_viewer_land_rent = models.FloatField(default=0)
    sum_buyer_land_rent = models.FloatField(default=0)
    avg_buyer_land_rent = models.FloatField(default=0)
    std_buyer_land_rent = models.FloatField(default=0)

    class Meta:
        db_table = 'ecommerce_transactions'

class CityGeography(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True, default=None)
    province = models.CharField(max_length=15)
    region_name = models.CharField(max_length=30)
    region_type = models.CharField(max_length=10)
    area_geometry = models.TextField(default="")

    class Meta:
        db_table = 'city_geography'