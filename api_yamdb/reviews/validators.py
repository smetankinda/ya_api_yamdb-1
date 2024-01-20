import re

from django.core.exceptions import ValidationError


def is_username_valid(value):
    """Проверка логина на валидность"""

    if value == 'me':
        raise ValidationError(
            ('Логин не может быть <me>.'),
            params={'value': value},
        )
    if re.search(r'^[a-zA-Z][a-zA-Z0-9-_\.]{1,20}$', value) is None:
        raise ValidationError(
            (f'Недопустимые символы <{value}> в логине.'),
            params={'value': value},
        )
