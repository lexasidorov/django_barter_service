from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

SUCCESS_CODES = {
    'get': 200,
    'post': 201,
    'put': 200,
    'delete': 204,
}


def auto_schema(is_list=False):
    def decorator(view_method):

        def build_schema(self, request):
            """Конструктор схемы документации"""
            method = request.method.lower()
            serializer_class = getattr(self, 'serializer_class', None)

            success_response = OpenApiResponse(description='Успешный ответ')
            request_body = None
            parameters = []
            required_fields = []
            error_examples = {}

            if serializer_class is not None:
                serializer = serializer_class()
                if method == 'get':
                    for field_name, field in serializer.fields.items():
                        param = OpenApiParameter(
                            name=field_name,
                            type=OpenApiTypes.STR,
                            description=getattr(field, 'help_text', ''),
                            required=field.required,
                            enum=list(field.choices.keys()) if hasattr(field, 'choices') else None
                        )
                        parameters.append(param)
                    if is_list:
                        success_response = serializer_class(many=True)
                    else:
                        success_response = serializer_class
                else:
                    for field_name, field in serializer.fields.items():
                        if field.required:
                            required_fields.append(field_name)
                            error_examples[field_name] = ["Это поле обязательно."]
                    request_body = serializer_class

            schema_config = {
                'responses': {
                    SUCCESS_CODES.get(method, 200): success_response,
                    400: OpenApiResponse(
                        description='Ошибка валидации',
                        examples={'application/json': error_examples} if error_examples else None
                    ),
                    403: OpenApiResponse(description='Доступ запрещен'),
                    404: OpenApiResponse(description='Не найдено')
                }
            }
            if method == 'get':
                schema_config['parameters'] = parameters
            else:
                schema_config['request'] = request_body

            return schema_config

        def wrapped(self, request, *args, **kwargs):
            # Сначала выполняется оригинальный метод
            response = view_method(self, request, *args, **kwargs)

            # Затем формируем схему для документации
            schema_config = build_schema(self, request)
            extend_schema(**schema_config)(view_method)

            # Возвращаем оригинальный response
            return response
        return wrapped
    return decorator