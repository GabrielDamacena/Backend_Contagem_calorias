from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from .models import Meal, FoodItem
from .serializers import TextInputSerializer, FileInputSerializer, MealSerializer
from .services import analyze_text_input, analyze_audio_input, analyze_image_input
import json



class TextMealInputView(APIView):
    def post(self, request):
        serializer = TextInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Processa cada alimento individualmente
            foods_list = serializer.validated_data['foods']
            all_results = []
            
            for food_text in foods_list:
                analysis_result = analyze_text_input(food_text)
                if isinstance(analysis_result, list):
                    all_results.extend(analysis_result)
                else:
                    all_results.append(analysis_result)
            
            # Cria ou obtém a refeição
            today = timezone.now().date()
            meal, created = Meal.objects.get_or_create(
                user=request.user,
                date=today,
                defaults={'user': request.user, 'date': today}
            )
            
            # Cria todos os itens de comida
            self._create_food_items(meal, all_results)
            
            return Response(
                MealSerializer(meal).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _create_food_items(self, meal, analysis_result):
        """Método auxiliar para criar food items"""
        if not isinstance(analysis_result, list):
            analysis_result = [analysis_result]
            
        for item in analysis_result:
            FoodItem.objects.create(
                meal=meal,
                food=item.get('food', 'Unknown'),
                grams=item.get('grams', 0),
                calories=item.get('calories', 0),
                proteins_g=item.get('proteins_g', 0),
                carbohydrates_g=item.get('carbohydrates_g', 0),
                fats_g=item.get('fats_g', 0)
            )

class FileMealInputView(GenericAPIView):
    """
    Endpoint para processar arquivos de áudio ou imagem nutricional
    """
    serializer_class = FileInputSerializer
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            file = serializer.validated_data['file']
            file_type = serializer.validated_data['type']
            
            # Processa o arquivo conforme o tipo
            if file_type == 'audio':
                analysis_result = analyze_audio_input(file)
            else:
                analysis_result = analyze_image_input(file)

            # Verifica se o resultado é válido
            if not analysis_result or not isinstance(analysis_result, list):
                return Response(
                    {'error': 'Não foi possível processar o arquivo. Resultado inválido.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Cria ou obtém a refeição do dia
            today = timezone.now().date()
            meal, created = Meal.objects.get_or_create(
                user=request.user,
                date=today,
                defaults={'user': request.user, 'date': today}
            )
            
            # Cria os itens de comida e conta os processados/erros
            food_items_created = 0
            errors = []
            
            for food_data in analysis_result:
                try:
                    # Mapeia os campos da Gemini para seu modelo
                    mapped_data = {
                        'food': food_data.get('food', food_data.get('alimento', 'Unknown')),
                        'grams': float(food_data.get('grams', food_data.get('gramas', 0)) if food_data.get('grams') or food_data.get('gramas') else 0,),
                        'calories': float(food_data.get('calories', food_data.get('calorias', 0))),
                        'proteins_g': float(food_data.get('proteins_g', food_data.get('proteinas_g', 0))),
                        'carbohydrates_g': float(food_data.get('carbohydrates_g', food_data.get('carboidratos_g', 0))),
                        'fats_g': float(food_data.get('fats_g', food_data.get('gorduras_g', 0)))
                    }
                    
                    FoodItem.objects.create(meal=meal, **mapped_data)
                    food_items_created += 1
                except Exception as e:
                    errors.append({
                        'food_item': str(food_data),
                        'error': str(e)
                    })

            response_data = {
                'meal': MealSerializer(meal).data,
                'processing_summary': {
                    'input_type': file_type,
                    'total_items_processed': food_items_created,
                    'errors_count': len(errors),
                    'errors_details': errors if errors else None
                }
            }

            # Adiciona o tipo de input ao objeto meal para serialização
            meal.input_type = file_type

            return Response(
                response_data,
                status=status.HTTP_207_MULTI_STATUS if errors else status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )