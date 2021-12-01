from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth.models import User



class LoginSerializers(serializers.ModelSerializer):
    password = serializers.CharField(read_only=True)

    class Meta:
        model = User,
        fields = ['id', 'username', 'password']

    def validators(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        print(user)
