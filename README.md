# Foodgram

### Описание:
Сервис представляет собой социальную сеть, направленную на обменивание рецептами различных блюд. Пользователь может добавлять, удалять и редактировать рецепты, просматривать чужие, скачивать список ингредиенто, а также подписывать на других пользователей и добавлять их рецепты в избранное.
Проект написан в рамках дипломной работы на курсе Я.Практикум.

### Используемые технологии:
- [Django==3.2.3](https://docs.djangoproject.com/en/4.2/)
- [djangorestframework==3.12.4](https://www.django-rest-framework.org/topics/documenting-your-api/)
- [djoser==2.1.0](https://djoser.readthedocs.io/en/latest/)
- [webcolors==1.11.1](https://webcolors.readthedocs.io/en/latest/)
- [psycopg2-binary](https://pypi.org/project/psycopg2-binary/)
- [pytest==6.2.4](https://docs.pytest.org/en/7.1.x/contents.html)
- [pytest-django==4.4.0](https://pytest-django.readthedocs.io/en/latest/)
- [pytest-pythonpath==0.7.3](https://pypi.org/project/pytest-pythonpath/)
- [PyYAML==6.0](https://pyyaml.org/wiki/PyYAMLDocumentation)

### Развертывание проекта:

Клонирование репозитория:
```
gic clone  git@github.com:ваш_аккаунт/название_репозитория.git
```

Запуск проекта (находимся в директории infra)
```
sudo docker compose up
```
Установка микраций + статика:
```
sudo docker compose exec backend migrate
```
```
sudo docker compose exec backend collectstatic
```
При запуске локально документация находится по адресу:
```
https://localhost:8000/api/docs/
```

### Примеры запросов к api проекта:

Создание пользователя:
```
POST | https://localhost:8000/api/users/
```
```
{
  "email": "vpupkin@yandex.ru",
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Пупкин",
  "password": "Qwerty123"
}
```
Получение jwt-токена:
```
POST | http://localhost:9000/api/token/login/
'''
'''
{
  "email": "vpupkin@yandex.ru",
  "username": "vasya.pupkin",
}
```
Получение списка рецептов:
```
GET | https://localhost:8000/api/recipes/
```
Пример ответа:
```
{
  "count": 123,
  "next": "http://foodgram.example.org/api/recipes/?page=4",
  "previous": "http://foodgram.example.org/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "color": "#E26C2D",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": false
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
```

### Автор:
#### Владимир Митин
