from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from drf_spectacular.utils import extend_schema, OpenApiExample
# from drf_spectacular.types import OpenApiTypes

from .models import *
from .serializers import *
from .forms import *

# @extend_schema(tags=['Tasks'])
class AdDetailView(APIView):
    def post(self, request):
        id = request.data.get('id', None)
        if id is None:
            return Response({
                'status': 'error',
                'data': 'Не передано поле id'
            })
        try:
            ad = Ad.objects.get(id=id)
            serializer = AdSerializer(ad)
            return Response({
                'status': 'success',
                'ad': serializer.data
            }, status=status.HTTP_200_OK)

        except Ad.DoesNotExist:
            return Response({
                'status': 'error',
                'data': 'Объявление не найдено'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as error:
            return Response({
                'status': 'error',
                'data': str(error)
            }, status=status.HTTP_400_BAD_REQUEST)


class AdCreateView(APIView):
    def post(self, request):
        try:
            form = AdForm(request.data, user=request.user)
            if form.is_valid():
                ad = form.save()
                serializer = AdSerializer(ad)

                return Response({
                    'status': 'success',
                    'ad': serializer.data
                }, status=status.HTTP_201_CREATED)

            else:
                return Response({
                    'status': 'error',
                    'data': form.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            return Response({
                'status': 'error',
                'data': str(error)
            }, status=status.HTTP_400_BAD_REQUEST)


class AdUpdateView(APIView):
    def get(self, request):
        form = AdForm(user=request.user)
        return render(request, 'barter/ad_create.html', {'form': form})

    def post(self, request):
        id = request.data.get('id', None)
        if id is None:
            return Response({
                'status': 'error',
                'data': 'Не передано поле id'
            })
        try:
            ad = Ad.objects.get(id=id, author=request.user)
            form = AdForm(request.data, instance=ad, user=request.user)
            if form.is_valid():
                ad = form.save()
                serializer = AdSerializer(ad)
                return Response({
                    'status': 'success',
                    'ad': serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                'status': 'error',
                'data': form.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Ad.DoesNotExist:
            return Response({
                'status': 'error',
                'data': 'Объявление не найдено или нет прав'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as error:
            return Response({
                'status': 'error',
                'data': str(error)
            }, status=status.HTTP_400_BAD_REQUEST)

class AdListView(APIView):
    def post(self, request):
        try:
            ads = Ad.objects.filter(is_active=True)
            serializer = AdSerializer(ads, many=True)
            return Response({
                'status': 'success',
                'ads': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({
                'status': 'error',
                'data': str(error)
            }, status=status.HTTP_400_BAD_REQUEST)

class AdDeleteView(APIView):
    def post(self, request):
        id = request.data.get('id', None)
        if id is None:
            return Response({
                'status': 'error',
                'data': 'Не передано поле id'
            })
        try:
            ad = Ad.objects.get(id=id, author=request.user)
            ad.delete()
            return Response({
                'status': 'success'
            }, status=status.HTTP_200_OK)

        except Ad.DoesNotExist:
            return Response({
                'status': 'error',
                'data': 'Объявление не найдено или нет прав'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as error:
            return Response({
                'status': 'error',
                'data': str(error)
            }, status=status.HTTP_400_BAD_REQUEST)

class ProposalDetailView(APIView):
    def post(self, request):
        id = request.data.get('id', None)
        if id is None:
            return Response({
                'status': 'error',
                'data': 'Не передано поле id'
            })
        try:
            proposal = ExchangeProposal.objects.get(id=id)
            serializer = ExchangeProposalSerializer(proposal)

            return Response({
                'status': 'success',
                'proposal': serializer.data
            }, status=status.HTTP_200_OK)

        except ExchangeProposal.DoesNotExist:
            return Response({
                'status': 'error',
                'data': 'Предложение не найдено'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as error:
            return Response({
                'status': 'error',
                'data': str(error)
            }, status=status.HTTP_400_BAD_REQUEST)

class ProposalCreateView(APIView):
    def post(self, request):
        try:
            serializer = ExchangeProposalSerializer(
                data=request.data,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()

                return Response({
                    'status': 'success',
                    'proposal': serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'status': 'error',
                    'data': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error:
            return Response({
                'status': 'error',
                'data': str(error)
            }, status=status.HTTP_400_BAD_REQUEST)

class ProposalListView(APIView):
    def post(self, request):
        try:
            proposals = ExchangeProposal.objects.filter(
                sender__author=request.user
            ) | ExchangeProposal.objects.filter(
                receiver__author=request.user
            )
            serializer = ExchangeProposalSerializer(proposals, many=True)

            return Response({
                'status': 'success',
                'proposals': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as error:
            return Response({
                'status': 'error',
                'data': str(error)
            }, status=status.HTTP_400_BAD_REQUEST)

class ProposalDeleteView(APIView):
    def post(self, request):
        id = request.data.get('id', None)
        if id is None:
            return  Response({
                'status': 'error',
                'data': 'Не передано поле id'
            })
        try:
            proposal = ExchangeProposal.objects.get(
                id=id,
                sender__author=request.user
            )
            proposal.delete()

            return Response({
                'status': 'success'
            }, status=status.HTTP_200_OK)

        except ExchangeProposal.DoesNotExist:
            return Response({
                'status': 'error',
                'data': 'Предложение не найдено или нет прав'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as error:
            return Response({
                'status': 'error',
                'data': str(error)
            }, status=status.HTTP_400_BAD_REQUEST)
