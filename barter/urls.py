from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import *


urlpatterns = [
    # Объявления
    path('ads/', AdListCreateView.as_view(), name='ad-list'),
    path('ads/<int:pk>/', AdRetrieveUpdateDestroyView.as_view(), name='ad-detail'),

    # Предложения обмена
    path('proposals/', ProposalListCreateView.as_view(), name='proposal-list'),
    path('proposals/<int:pk>/', ProposalRetrieveDestroyView.as_view(), name='proposal-detail'),
]

# Документация
urlpatterns.extend([
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
])
