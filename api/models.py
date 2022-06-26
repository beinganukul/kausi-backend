from django.db import models
from django.contrib.auth.models import User

class Coordinate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    latitude = models.FloatField(null=False, blank=False)
    longtitude = models.FloatField(null=False, blank=False)
   
class Crop(models.Model):
    CROP_CATEGORY = [
        ("FRUIT", 'Fruit'),
        ("VEGETABLE", 'Vegetable'),
        ("Cash Crop", 'Cash Crop'),
    ]
    CROP_SEASON = [
        ("WINTER", "Winter"),
        ("SUMMER", "Summer"),
        ("AUTUMN", "Autumn"),
        ("SPRING", "Spring"),
    ]
    KAUSI = [
        ("YEs", "Yes"),
        ("NO", "No"),
    ]
    local_name = models.CharField(max_length=150)
    scientific_name = models.CharField(max_length=150, unique=True)
    description = models.CharField(max_length=2000)
    category = models.CharField(max_length=10, choices=CROP_CATEGORY)
    tempmin = models.FloatField(null=False, blank=False)
    tempmax = models.FloatField(null=False, blank=False)
    rainmin = models.FloatField(null=True, blank=True)
    rainmax = models.FloatField(null=True, blank=True)
    phmin = models.FloatField(null=False, blank=False)
    phmax = models.FloatField(null=False, blank=False)
    organicmin = models.FloatField(null=True, blank=True)
    organicmax = models.FloatField(null=True, blank=True)
    altitudemin = models.FloatField(null=False, blank=False)
    altitudemax = models.FloatField(null=False, blank=False)
    image = models.ImageField(upload_to="images/", blank=True)
    season = models.CharField(max_length=7, choices=CROP_SEASON)
    harvest = models.FloatField(null=False, blank=False)
    is_terrace = models.CharField(max_length=3, choices=KAUSI)
    link = models.URLField(max_length=2000)
    
    def __str__(self):
        return self.local_name
    
    
class UserCrop(models.Model):
    CROP_REMARKS = [
        ("FRUITFUL", "Fruitful"),
        ("GOOD", "Good"),
        ("NOTGOOD", "Not So Good"),
        ("FRUITLESS", "Fruitless"),
    ]
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    crop = models.OneToOneField(Crop, on_delete=models.DO_NOTHING)
    description = models.CharField(max_length=2000)
    
    ## Last minute edit to create functional demo, all the below fields needs to be populated for STAGE-II of project
    #remarks = models.CharField(max_length=10, choices=CROP_REMARKS)
    #latitude = models.FloatField(null=False, blank=False)
    #longtitude = models.FloatField(null=False, blank=False)
    #temp = models.FloatField(null=False, blank=False)
    #rain = models.FloatField(null=True, blank=True)
    #ph = models.FloatField(null=False, blank=False)
    #organic = models.FloatField(null=True, blank=True)
    #altitude = models.FloatField(null=False, blank=False)

class RequestCrop(models.Model):
    local_name = models.CharField(max_length=150)
    scientific_name = models.CharField(max_length=150, unique=True)
