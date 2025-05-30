from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model


User = get_user_model()


class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name=_('Название категории'))

    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')

    def __str__(self):
        return self.title


class Ad(models.Model):
    CONDITION_CHOICES = [
        ('new', 'Новое'),
        ('used', 'Б/У'),
        ('broken', 'Сломано'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Автор'), related_name='ads')
    title = models.CharField(max_length=100, verbose_name=_('Название'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активно'))
    description = models.CharField(max_length=500, verbose_name=_('Описание'))
    image_url = models.CharField(max_length=100, blank=True,     verbose_name=_('URL изображения'))
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Категория')
    )
    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default='used',
        verbose_name='Состояние'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))

    class Meta:
        verbose_name = _('Объявление')
        verbose_name_plural = _('Объявления')

    def __str__(self):
        return self.title


class ExchangeProposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено')
    ]

    sender = models.ForeignKey(Ad, related_name='sent_proposals', on_delete=models.CASCADE, verbose_name=_('Отправитель'))
    receiver = models.ForeignKey(Ad, related_name='received_proposals', on_delete=models.CASCADE, verbose_name=_('Получатель'))
    comment = models.CharField(max_length=500, verbose_name=_('Комментарий'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))

    class Meta:
        verbose_name = _('Предложение обмена')
        verbose_name_plural = _('Предложения обмена')
