from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('buscar/', views.buscar, name='buscar'),
    path('negocio/<int:pk>/', views.negocio, name='negocio'),
    path('negocio/<int:pk>/resena/', views.agregar_resena, name='agregar_resena'),
]
