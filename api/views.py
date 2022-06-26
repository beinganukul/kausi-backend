import os
import json
import requests
import overpass
import geopy.distance
from dotenv import load_dotenv
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.models import Coordinate, UserCrop, Crop
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from api.serializers import UserSerializer, CoordinateSerializer, UserCropSerializer, CropSerializer, AnotherUserCropSerializer, AnotherUserSerializer, RequestCropSerialiser

load_dotenv()
email = os.environ.get("NARC_EMAIL")
password = os.environ.get("NARC_PASSWORD")

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def requestcrop(request):
    """
    request for new crop to be added to database
    """
    serializer = RequestCropSerialiser(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors)
    return Response(serializer.data, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addusercrop(request):
    """create entry for each crop of individual user to create croudsourced database
    """
    description = request.data["description"]
    user = request.data["user"]
    crop = request.data["crop"]
    UserCrop.objects.create(user_id=user, crop_id=crop, description=description)
    return Response({"message":"user crop created"})
    
       
def get_org_ph(longtitude, latitude):
    """function to collect soil details using longtitude and latitude from NARC

    Args:
        longtitude (float): longtitude 
        latitude (float): latitude

    Returns:
        ph (float): ph value of soil
        organicMatter (float): organic matter of soil
    """
    data = {"email":email, "password":password}
    output = requests.post("https://soil.narc.gov.np/api/token", data=data)
    print(data)
    data = output.json()
    access_token = data["access"]
    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }
    url = f"https://krishiprabidhi.net/soil/soildata?lat={latitude}&lon={longtitude}"
    ph_output = requests.get(url, headers=headers)
    phdata = ph_output.json()
    return phdata["ph"], phdata["organicMatter"]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getusercrops(request):
    """
    returns crop of particular user id that is parsed from jwt
    """
    print(request.user.id)
    serializer = UserCropSerializer(UserCrop.objects.filter(user=request.user.id), many=True) 
    print(serializer.data)
    return Response(serializer.data, status=200)  

@api_view(['POST'])
def getcoords(request):
    """
    test endpoint when starting project
    """
    longtitude = request.data['lon']
    latitude = request.data['lat']
    return Response({"lon":longtitude, "lat":latitude})

@api_view(['POST'])
def createuser(request):
    """
    creates user
    """
    serializer = AnotherUserSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors)
    serializer.save()
    return Response(serializer.data, status = 200)

@api_view(['POST'])
def addcoordinate(request):
    """
    adds coordinates of individual user
    """ 
    serializer = CoordinateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors) 
    serializer.save()
    return Response(serializer.data, status=200)

@api_view(['POST'])
def cropradius(request):
    """
    gets crops that are being cultivated in 5km radius from given coordinates
    """
    longtitude = request.data['lon']
    latitude = request.data['lat']
    main_coord = (longtitude, latitude)
    acc_id = []
    dist = []
    for i in Coordinate.objects.all():
        dist.append(geopy.distance.geodesic(main_coord, (i.latitude, i.longtitude)).km)
        acc_id.append(i.id)
    zipped = zip(acc_id, dist)
    sorted_dist =  sorted(zipped, key=lambda x: float(x[1]), reverse=False)
    nearest_user_id = []
    for tpl in enumerate(sorted_dist):
        if tpl[1][1] < 5.0:
            nearest_user_id.append(tpl[1][0])
    output = []
    for id in nearest_user_id:
        for crpusr in UserCrop.objects.filter(user=id):
            data_value = UserCropSerializer(crpusr)
            output.append(data_value.data)
    return Response(output)

@api_view(['POST'])
def getcrop(request):
    serializer = CropSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors)
    serializer.save()
    return Response(serializer.data, status=200)

@api_view(['POST'])
def getsuggestion(request):
    """
    functional code to filter given values and return query that matches from database, to be replaced by function checkbuilding
    """
    longtitude = request.data['lon']
    latitude = request.data['lat']
    temperature = request.data['temp']
    response = requests.get(f"https://api.open-elevation.com/api/v1/lookup?locations={latitude},{longtitude}")
    altitude = json.loads(response.text)["results"][0]["elevation"]
    ph, organicmatter = get_org_ph(longtitude, latitude)
    suitable_crops = Crop.objects.filter(Q(tempmin__lte=temperature, tempmax__gte=temperature) & Q(phmin__lte=ph, phmax__gte=ph) & Q(altitudemin__lte=altitude, altitudemax__gte=altitude) & Q(is_terrace__startswith="YES"))# & Q(organicmin__lte=organicmatter, organicmax__gte=organicmatter)  ) 
    serialize = CropSerializer(suitable_crops, many=True)
    
    #for i in suitable_crops:
    #    print(i)
    return Response(serialize.data, status=200)

@api_view(['POST'])
def checkbuilding(request):
    """
    main logic of whole project, incomplete
    """
    longtitude = request.data['lon']
    latitude = request.data['lat']
    temperature = request.data['temp']
    response = requests.get(f"https://api.open-elevation.com/api/v1/lookup?locations={latitude},{longtitude}")
    altitude = json.loads(response.text)["results"][0]["elevation"]
    api = overpass.API()
    query = f"""
    [out:json][timeout:25];
    (nwr["building"](around:4.0, {latitude},{longtitude}););
    out body;
    >;
    out skel qt;
    """ 
    resp = api._get_from_overpass(query)
    data = json.loads(resp.text)
    if len(data["elements"]) == 0:
        return Response({"message":"no building in this coordinate"})
    else:
        try:
            own_height = data["elements"][0]["tags"]["building:levels"]
            neighbor_query = f"""
            [out:json][timeout:25];
            (nwr["building"](around:35.0, {latitude},{longtitude}););
            out body;
            >;
            out skel qt;
            """
            neighbor_response = api._get_from_overpass(neighbor_query)
            neighbor_data = json.loads(neighbor_response.text)["elements"]
            try:
                if len(neighbor_data) != 0:
                    return Response({"message":"predict crop"})
            except:
                return Response({"mesage":"no building near you, predict crop"})
        except:
            return Response({"message":"building doesn't have enought tags to suggest crop to harvest, please contribute height information to openstreetmaps.org"})

     
@api_view(['POST'])
def getsuggestionforbuilding(request):
    """
    main logic of whole project, incomplete
    """
    longtitude = request.data['lon']
    latitude = request.data['lat']
    temperature = request.data['temp']
    response = requests.get(f"https://api.open-elevation.com/api/v1/lookup?locations={latitude},{longtitude}")
    altitude = json.loads(response.text)["results"][0]["elevation"]
    api = overpass.API()
    query = f"""
    [out:json][timeout:25];
    (nwr["building"](around:4.0, {latitude},{longtitude}););
    out body;
    >;
    out skel qt;
    """ 
    resp = api._get_from_overpass(query)
    data = json.loads(resp.text)
    if len(data["elements"]) == 0:
        return Response({"message":"no building in this coordinate"})
    else:
        try:
            own_height = data["elements"][0]["tags"]["building:levels"]
            neighbor_query = f"""
            [out:json][timeout:25];
            (nwr["building"](around:35.0, {latitude},{longtitude}););
            out body;
            >;
            out skel qt;
            """
            neighbor_response = api._get_from_overpass(neighbor_query)
            neighbor_data = json.loads(neighbor_response.text)["elements"]
            try:
                for i in neighbor_data:
                    if i["type"] == "way":
                        try:
                           if own_height < i["tags"]["building:levels"]:
                                print("your house is lower than other's please cultivate crops that are resistant to less sunlight")
                           else:
                               print("prediction code here")
                        except:
                            print("please input some building height") 
                            return Response({"message":"building doesn't have height data to suggest crop to harvest, please contribute height information to openstreetmaps.org"})
                return Response({"mesage":"building near you"})
            except:
                print("prediction code here")
                return Response({"mesage":"no building near you"})
        except:
            return Response({"message":"building doesn't have enought tags to suggest crop to harvest, please contribute height information to openstreetmaps.org"})

@api_view(['GET'])
def getallcrops(request):
    """
    dumps all the details of crops from database
    """
    serializer = CropSerializer(Crop.objects.all(), many=True)
    return Response(serializer.data, status=200)

