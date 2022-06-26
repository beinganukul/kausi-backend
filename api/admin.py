from django.contrib import admin
from api.models import Coordinate, UserCrop, Crop

admin.site.register(Crop) 
admin.site.register(UserCrop) 
admin.site.register(Coordinate) 

