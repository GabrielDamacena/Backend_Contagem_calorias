from django.contrib import admin
from .models import Meal, FoodItem

class FoodItemInline(admin.TabularInline):  # ou admin.StackedInline
    model = FoodItem
    extra = 1  # Número de forms vazios para adicionar novos itens

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'created_at')
    list_filter = ('date', 'user')
    search_fields = ('user__username',)
    inlines = [FoodItemInline]  # Mostra os FoodItems diretamente na página de Meal

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('meal', 'food', 'grams', 'calories')
    list_filter = ('meal__date', 'food')
    search_fields = ('food',)