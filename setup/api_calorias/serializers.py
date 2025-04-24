from rest_framework import serializers
from .models import Meal, FoodItem
from django.utils import timezone

class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = ['id', 'food', 'grams', 'calories', 'proteins_g', 
                 'carbohydrates_g', 'fats_g']
        read_only_fields = ['id']

class TextInputSerializer(serializers.Serializer):
    foods = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        help_text="Lista de alimentos. Ex: ['2 ovos', '1 banana']"
    )

class FileInputSerializer(serializers.Serializer):
    file = serializers.FileField(required=True, write_only=True)
    file_type = serializers.ChoiceField(
        choices=['audio', 'image'],
        required=True,
        write_only=True,
        source='type'  # Mapeia para o campo 'type' no validated_data
    )
    
    def to_representation(self, instance):
        # Quando for serializar a resposta, usa o MealSerializer
        return MealSerializer(instance).data

class MealSerializer(serializers.ModelSerializer):
    food_items = FoodItemSerializer(many=True, read_only=True)
    input_type = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Meal
        fields = ['id', 'date', 'user', 'food_items', 'input_type']
        read_only_fields = ['id', 'date', 'user']
    
    def get_input_type(self, obj):
        # Retorna o tipo de input baseado nos food_items associados
        if hasattr(obj, 'input_type'):
            return obj.input_type
        return None

class MealCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['id', 'date', 'user']
        read_only_fields = ['id', 'date']
        extra_kwargs = {
            'user': {'write_only': True}
        }