from django import forms
from .models import *


class AdForm(forms.ModelForm):
    category_id = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label='Категория',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    condition = forms.ChoiceField(
        choices=Ad.CONDITION_CHOICES,
        label='Состояние',
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='used',
    )

    class Meta:
        model = Ad
        fields = ['title', 'description', 'image_url', 'category_id', 'condition']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Подробно опишите товар...'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название товара'
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/photo.jpg'
            }),
        }
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'image_url': 'Ссылка на изображение',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['condition'].help_text = 'Выберите состояние товара'

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.author = self.user
        instance.category = self.cleaned_data['category_id']
        if commit:
            instance.save()
        return instance


class ProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['sender', 'receiver', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Фильтруем только свои объявления
        self.fields['sender'].queryset = Ad.objects.filter(is_active=True, author=self.user)

        # Фильтруем только активные объявления, кроме своего
        self.fields['receiver'].queryset = Ad.objects.filter(is_active=True).exclude(author=self.user)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance
