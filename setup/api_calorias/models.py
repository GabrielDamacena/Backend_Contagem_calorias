from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class FoodItem(models.Model):
    meal = models.ForeignKey(Meal, related_name='food_items', on_delete=models.CASCADE)
    food = models.CharField(max_length=255)
    grams = models.FloatField()
    calories = models.FloatField()
    proteins_g = models.FloatField()
    carbohydrates_g = models.FloatField()
    fats_g = models.FloatField()
    
    def __str__(self):
        return f"{self.food} ({self.grams}g)"