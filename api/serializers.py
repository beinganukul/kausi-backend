from rest_framework import serializers
from api.models import Coordinate, Crop, UserCrop, User, RequestCrop

class RequestCropSerialiser(serializers.ModelSerializer):
    class Meta:
        model = RequestCrop
        fields = '__all__'
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class CoordinateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinate
        fields = '__all__'

class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = '__all__'
         
class UserCropSerializer(serializers.ModelSerializer):
    crop = CropSerializer()
    class Meta:
        model = UserCrop
        fields = '__all__'

class AnotherUserCropSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCrop
        fields = '__all__'

class AnotherUserSerializer(serializers.ModelSerializer): 
    class Meta:
        model = User
        fields = '__all__'
        write_only_fields = ('password',)
        read_only_fields = ('id',)
    
    def create(self, validated_data):
        user = User.objects.create(
            username = validated_data['username'],
            email = validated_data['email'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user