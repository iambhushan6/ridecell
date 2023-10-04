from django.contrib import admin
from django.urls import path, include
from main.views import TestAPIView

urlpatterns = [
    path('test/', TestAPIView, name='test_api_view')
]