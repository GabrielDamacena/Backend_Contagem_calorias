from django.contrib import admin
from django.urls import path
from .views import TextMealInputView, FileMealInputView
from django.views.generic.base import RedirectView
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('', RedirectView.as_view(url='/admin/')),
    path('meals/text/', TextMealInputView.as_view(), name='meal-text-input'),
    path('meals/files/', FileMealInputView.as_view(), name='meal-file-input'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)