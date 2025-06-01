import pytest

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Даем доступ к БД всем тестам"""
    pass