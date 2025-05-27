from django.urls import path
from .views import *

urlpatterns = [
    # Объявления
    path('ads/', AdListCreateView.as_view(), name='ad-list'),
    path('ads/<int:pk>/', AdRetrieveUpdateDestroyView.as_view(), name='ad-detail'),

    # Предложения обмена
    path('proposals/', ProposalListCreateView.as_view(), name='proposal-list'),
    path('proposals/<int:pk>/', ProposalRetrieveDestroyView.as_view(), name='proposal-detail'),
]

#
# urlpatterns = [
#     # Объявления
#     path('ad/detail/', AdDetailView.as_view()),
#     path('ad/create/', AdCreateView.as_view()),
#     path('ad/update/', AdUpdateView.as_view()),
#     path('ad/list/', AdListView.as_view()),
#     path('ad/delete/', AdDeleteView.as_view()),
#
#     # Предложения обмена
#     path('proposal/detail/', ProposalDetailView.as_view()),
#     path('proposal/create/', ProposalCreateView.as_view()),
#     path('proposal/list/', ProposalListView.as_view()),
#     path('proposal/delete/', ProposalDeleteView.as_view()),
# ]