from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pet/<int:pk>/', views.pet_detail, name='pet_detail'),
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.register_view, name='register'),
    path('contract/<int:application_id>/download/', views.download_contract_txt, name='download_contract'),
]
