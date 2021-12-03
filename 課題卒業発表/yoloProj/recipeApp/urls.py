from django.urls import path
from . import views

# app_name = 'fileUploadSample'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    # path('predictImage', views.predictImage, name='predictImage'),
]


