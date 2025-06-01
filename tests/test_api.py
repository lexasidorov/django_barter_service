import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from barter.models import Category, Ad, ExchangeProposal

User = get_user_model()


@pytest.fixture(scope='module')
def django_db_setup(django_db_setup, django_db_blocker):
    """Фикстура для создания тестовых данных"""
    with django_db_blocker.unblock():
        # Пользователи
        user1 = User.objects.create_user(username='user1', password='pass1')
        user2 = User.objects.create_user(username='user2', password='pass2')
        admin = User.objects.create_superuser(username='admin', password='adminpass')

        # Категории
        cat1 = Category.objects.create(title='Электроника')
        cat2 = Category.objects.create(title='Одежда')

        # Объявления
        Ad.objects.create(
            title='Смартфон', description='Новый', author=user1, category=cat1, condition='new'
        )
        Ad.objects.create(
            title='Футболка', description='Б/у', author=user2, category=cat2, condition='used'
        )
        Ad.objects.create(
            title='Ноутбук', description='Рабочий', author=user1, category=cat1, condition='used'
        )

        # Предложения обмена
        ExchangeProposal.objects.create(
            sender=Ad.objects.get(title='Смартфон'),
            receiver=Ad.objects.get(title='Футболка'),
            comment='Предлагаю обмен',
            status='pending'
        )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user1_client(api_client):
    """Клиент с авторизацией user1"""
    user = User.objects.get(username='user1')
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def user2_client(api_client):
    """Клиент с авторизацией user2"""
    user = User.objects.get(username='user2')
    api_client.force_authenticate(user=user)
    return api_client


# ====================== Тесты объявлений (Ad) ======================
class TestAdAPI:
    def test_list_ads(self, api_client):
        """Проверка успешного получения списка объявлений"""
        response = api_client.get('/ads/')
        assert response.status_code == 200
        assert len(response.data['results']) == 3

    def test_create_ad(self, user1_client):
        """Проверка успешного создания объявления"""
        cat = Category.objects.first()
        data = {
            'title': 'Новое объявление',
            'description': 'Описание',
            'category_id': cat.id,
            'condition': 'new'
        }
        response = user1_client.post('/ads/', data=data)
        assert response.status_code == 201
        assert Ad.objects.count() == 4

    def test_retrieve_ad(self, api_client):
        """Проверка успешного получения одного объявления"""
        ad = Ad.objects.first()
        response = api_client.get(f'/ads/{ad.id}/')
        assert response.status_code == 200
        assert response.data['title'] == ad.title

    def test_retrieve_nonexistent_ad(self, api_client):
        """Проверка 404"""
        latest = Ad.objects.order_by('-pk').first()
        response = api_client.get(f'/ads/{latest.id + 1}/')
        assert response.status_code == 404

    def test_update_ad_unauthorized(self, api_client):
        """Проверка 403 при попытке изменить объявление без авторизации"""
        ad = Ad.objects.first()
        response = api_client.put(f'/ads/{ad.id}/', {'title': 'Новое название'})
        assert response.status_code == 403

    def test_update_others_ad(self, user2_client):
        """Проверка 403 при попытке изменить чужое объявление"""
        ad = Ad.objects.filter(author__username='user1').first()
        response = user2_client.put(f'/ads/{ad.id}/', {'title': 'Новое название'})
        assert response.status_code == 403

    def test_create_ad_invalid_data(self, user1_client):
        """Проверка 400 при невалидных данных"""
        data = {'title': ''}
        response = user1_client.post('/ads/', data=data)
        assert response.status_code == 400
        assert 'title' in response.data

    def test_filter_by_category(self, api_client):
        """Проверка фильтрации по категории"""
        cat = Category.objects.first()
        response = api_client.get(f'/ads/?category={cat.id}')
        assert response.status_code == 200
        assert all(ad['category']['id'] == cat.id for ad in response.data['results'])

    def test_filter_nonexistent_category(self, api_client):
        """Проверка фильтра по несуществующей категории"""
        latest = Category.objects.order_by('-pk').first()
        response = api_client.get(f'/ads/?category={latest.id + 1}')
        # Django валидирует поля фильтрации и возвращает 400. Обойти можно, но мне пока лень разбираться
        assert response.status_code == 400

    def test_search_ads(self, api_client):
        """Проверка поиска объявлений"""
        ad = Ad.objects.first()
        response = api_client.get(f'/ads/?search={ad.title[:-1]}') # Обрезаем последний символ
        assert response.status_code == 200
        assert any(item['title'] == ad.title for item in response.data['results'])

    def test_empty_search(self, api_client):
        """Проверка пустого поискового запроса"""
        response = api_client.get('/ads/?search=')
        assert response.status_code == 200
        assert len(response.data['results']) == 3  # Все объявления


# ====================== Тесты предложений обмена (ExchangeProposal) ======================

class TestExchangeProposalAPI:
    def test_list_proposals(self, user1_client):
        """Проверка успешного получения списка предложений"""
        response = user1_client.get('/proposals/')
        assert response.status_code == 200
        assert len(response.data) > 0

    def test_create_proposal(self, user1_client):
        """Проверка успешного создания предложения"""
        sender_ad = Ad.objects.filter(author__username='user1').first()
        receiver_ad = Ad.objects.filter(author__username='user2').first()

        data = {
            'sender_id': sender_ad.id,
            'receiver_id': receiver_ad.id,
            'comment': 'Хочу обменять'
        }
        response = user1_client.post('/proposals/', data=data)
        assert response.status_code == 201
        assert ExchangeProposal.objects.count() == 2

    def test_retrieve_proposal(self, user1_client):
        """Проверка успешного получения предложения"""
        proposal = ExchangeProposal.objects.first()
        response = user1_client.get(f'/proposals/{proposal.id}/')
        assert response.status_code == 200
        assert response.data['comment'] == proposal.comment

    # ----------- Обработка ошибок -----------
    def test_create_proposal_own_ad(self, user1_client):
        """Проверка 400 при попытке обмена на свое же объявление"""
        sender_ad = Ad.objects.filter(author__username='user1').first()
        data = {
            'sender_id': sender_ad.id,
            'receiver_id': sender_ad.id,  # Отправляем свое же объявление
            'comment': 'Нельзя!'
        }
        response = user1_client.post('/proposals/', data=data)
        assert response.status_code == 400

    def test_create_proposal_unauthorized(self, api_client):
        """Проверка 403 при создании предложения без авторизации"""
        ad1, ad2 = Ad.objects.all()[:2]
        response = api_client.post('/proposals/', {
            'sender_id': ad1.id,
            'receiver_id': ad2.id,
            'comment': 'Нельзя!'
        })
        assert response.status_code == 403

    def test_retrieve_others_proposal(self, user2_client):
        """Проверка 403 при просмотре чужого предложения"""
        # Предложение, где user2 является получателем
        proposal = ExchangeProposal.objects.filter(receiver__author__username='user2').first()
        response = user2_client.get(f'/proposals/{proposal.id}/')
        assert response.status_code == 200  # Должен иметь доступ

        # Предложение, где user2 не участвует
        proposal = ExchangeProposal.objects.exclude(
            sender__author__username='user2'
        ).exclude(
            receiver__author__username='user2'
        ).first()
        if proposal:  # Если такое предложение существует
            response = user2_client.get(f'/proposals/{proposal.id}/')
            assert response.status_code == 403

    def test_delete_proposal(self, user1_client):
        """Проверка успешного удаления предложения"""
        proposal = ExchangeProposal.objects.filter(sender__author__username='user1').first()
        response = user1_client.delete(f'/proposals/{proposal.id}/')
        assert response.status_code == 204
        assert not ExchangeProposal.objects.filter(id=proposal.id).exists()

    def test_delete_others_proposal(self, user2_client):
        """Проверка 403 при попытке удалить чужое предложение"""
        proposal = ExchangeProposal.objects.filter(sender__author__username='user1').first()
        response = user2_client.delete(f'/proposals/{proposal.id}/')
        assert response.status_code == 403