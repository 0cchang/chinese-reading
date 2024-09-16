from django.urls import path
from .views import get_all_chars, create_char, char_detail

urlpatterns = [
    path('chars/', get_all_chars, name = 'get_all_chars'),
    path('chars/create', create_char, name = 'create_char'),
    path('chars/<int:pk>', char_detail, name = 'char_detail'),
]