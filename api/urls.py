from . import views
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('v1/gps/', views.getcoords),
    path('v1/getcrop/', views.getcrop),
    path('v1/cropradius/', views.cropradius),
    path('v1/createuser/', views.createuser),
    path('v1/requestcrop/', views.requestcrop),
    path('v1/getallcrops/', views.getallcrops),
    path('v1/addusercrop/', views.addusercrop),
    path('v1/getusercrops/', views.getusercrops),
    path('v1/addcoordinate/', views.addcoordinate),
    path('v1/getsuggestion/', views.getsuggestion),
    path('v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]