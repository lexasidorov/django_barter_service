from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q
from .permissions import *
# from .models import *
from .serializers import *
from .forms import *
from .utils.api_docs import auto_schema


class AdListCreateView(generics.ListCreateAPIView):
    # Фильтры
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'condition']
    search_fields = ['title', 'description']

    queryset = Ad.objects.filter(is_active=True)
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        if request.accepted_renderer.format == 'html':
            form = AdForm(user=request.user)
            return render(request, 'barter/ad_list.html', {
                'form': form,
                'search_query': request.GET.get('search', '')
            })
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', None)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class AdRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    @extend_schema(
        description='Детальная информация об объявлении',
        responses={
            200: AdSerializer,
            404: OpenApiResponse(description='Объявление не найдено')
        }
    )
    def get(self, request, *args, **kwargs):
        if request.accepted_renderer.format == 'html':
            instance = self.get_object()
            form = AdForm(instance=instance, user=request.user)
            return render(request, 'barter/ad_detail.html', {'form': form})
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description='Обновить объявление',
        request=AdSerializer,
        responses={
            200: AdSerializer,
            400: OpenApiResponse(description='Неверные данные'),
            403: OpenApiResponse(description='Нет прав на редактирование')
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        description='Удалить объявление',
        responses={
            204: OpenApiResponse(description='Успешно удалено'),
            403: OpenApiResponse(description='Нет прав на удаление'),
            404: OpenApiResponse(description='Объявление не найдено')
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class ProposalListCreateView(generics.ListCreateAPIView):
    serializer_class = ExchangeProposalSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        description='Получить список предложений обмена',
        parameters=[
            OpenApiParameter(name='sender', description='Фильтр по отправителю', required=False, type=int),
            OpenApiParameter(name='receiver', description='Фильтр по получателю', required=False, type=int),
        ],
        responses=ExchangeProposalSerializer(many=True)
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return ExchangeProposal.objects.filter(
            sender__author=self.request.user
        ) | ExchangeProposal.objects.filter(
            receiver__author=self.request.user
        )
    def perform_create(self, serializer):
        serializer.save()

    @extend_schema(
        description='Создать новое предложение обмена',
        request=ExchangeProposalSerializer,
        responses={
            201: ExchangeProposalSerializer,
            400: OpenApiResponse(description='Неверные данные'),
            403: OpenApiResponse(description='Нет прав на создание')
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ProposalRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        description='Получить детальную информацию о предложении',
        responses={
            200: ExchangeProposalSerializer,
            404: OpenApiResponse(description='Предложение не найдено')
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description='Удалить предложение обмена',
        responses={
            204: OpenApiResponse(description='Успешно удалено'),
            403: OpenApiResponse(description='Нет прав на удаление'),
            404: OpenApiResponse(description='Предложение не найдено')
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
