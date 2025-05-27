from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Ad, ExchangeProposal, Category


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class AdSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category',
        queryset=Category.objects.all(),
        write_only=True
    )
    condition_display = serializers.CharField(
        source='get_condition_display',
        read_only=True
    )

    class Meta:
        model = Ad
        fields = [
            'id', 'title', 'description', 'image_url',
            'category', 'category_id', 'condition', 'condition_display',
            'is_active', 'created_at', 'author'
        ]
        read_only_fields = ['created_at', 'author', 'condition_display']
        extra_kwargs = {
            'condition': {
                'choices': Ad.CONDITION_CHOICES,  # валидация в API
                'help_text': dict(Ad.CONDITION_CHOICES)  # для доки
            }
        }


class ExchangeProposalSerializer(serializers.ModelSerializer):
    sender_id = serializers.PrimaryKeyRelatedField(
        source='sender',
        queryset=Ad.objects.filter(is_active=True),
        write_only=True
    )
    receiver_id = serializers.PrimaryKeyRelatedField(
        source='receiver',
        queryset=Ad.objects.filter(is_active=True),
        write_only=True
    )
    sender = AdSerializer(read_only=True)
    receiver = AdSerializer(read_only=True)

    class Meta:
        model = ExchangeProposal
        fields = [
            'id', 'sender_id', 'receiver_id', 'sender', 'receiver',
            'comment', 'created_at', 'status'
        ]
        read_only_fields = ['created_at', 'status', 'sender', 'receiver']

    def validate(self, data):
        request = self.context.get('request')
        sender = data.get('sender', None)
        receiver = data.get('receiver', None)

        if not sender or not receiver:
            raise serializers.ValidationError("Необходимо указать объявления отправителя и получателя")

        if sender.author != request.user:
            raise serializers.ValidationError({
                'sender_id': 'Вы можете предлагать только свои объявления'
            })

        if receiver.author == request.user:
            raise serializers.ValidationError({
                'receiver_id': 'Нельзя предлагать обмен на собственное объявление'
            })

        return data

    def create(self, validated_data):
        validated_data['status'] = 'pending'
        return super().create(validated_data)
