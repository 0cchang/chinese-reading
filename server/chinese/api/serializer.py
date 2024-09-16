from rest_framework import serializers
from .models import CharMap

class CharSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharMap
        fields ='__all__'