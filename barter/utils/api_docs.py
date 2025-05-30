from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
# from rest_framework import serializers
from enum import Enum


class HttpMethod(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'


def auto_schema(serializer_class=None, method=HttpMethod.GET, success_code=200, is_list=False):
    def decorator(view_method):
        # Определяем параметры на основе сериализатора
        parameters = []
        request_body = None
        error_examples = {}

        if serializer_class:
            serializer = serializer_class()
            # fields_info = []
            required_fields = []

            for field_name, field in serializer.fields.items():
                if method == HttpMethod.GET:
                    # Для GET-запросов превращаем поля в параметры
                    param = OpenApiParameter(
                        name=field_name,
                        type=OpenApiTypes.STR,
                        description=getattr(field, 'help_text', ''),
                        required=field.required,
                        enum=list(field.choices.keys()) if hasattr(field, 'choices') else None
                    )
                    parameters.append(param)
                else:
                    # Для других методов собираем информацию о required полях
                    if field.required:
                        required_fields.append(field_name)
                        error_examples[field_name] = ["Это поле обязательно."]

            if method != HttpMethod.GET:
                request_body = serializer_class

            # Настраиваем успешный ответ
            if is_list:
                success_response = serializer_class(many=True)
            else:
                success_response = serializer_class
        else:
            success_response = OpenApiResponse(description='Успешный ответ')

        # Специфичные настройки для разных методов
        if method == HttpMethod.DELETE:
            success_response = OpenApiResponse(description='Успешно удалено')
            success_code = 204

        # Собираем итоговую конфигурацию
        schema_config = {
            'responses': {
                success_code: success_response,
                400: OpenApiResponse(
                    description='Ошибка валидации',
                    examples={'application/json': error_examples} if error_examples else None
                ),
                403: OpenApiResponse(description='Доступ запрещен'),
                404: OpenApiResponse(description='Не найдено')
            }
        }

        if method == HttpMethod.GET:
            schema_config['parameters'] = parameters
        else:
            schema_config['request'] = request_body

        return extend_schema(**schema_config)(view_method)

    return decorator