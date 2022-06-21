# Проект Foodgram
![foodgram_workflow](https://github.com/SaPer663/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)  
  
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![poetry](https://img.shields.io/badge/-poetry-464646?style=flat-square&logo=poetry)](https://github.com/python-poetry/poetry)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)


Foodgram(«Продуктовый помощник») - это онлайн-сервис и API для него. На этом
сервисе пользователи смогут публиковать рецепты, подписываться на публикации
других пользователей, добавлять понравившиеся рецепты в список «Избранное»,
а перед походом в магазин скачивать сводный список продуктов, необходимых для
приготовления одного или нескольких выбранных блюд.


## Подготовка и запуск проекта
### Склонировать репозиторий на локальную машину:
```
git clone https://github.com/SaPer663/foodgram-project-react.git
```
### На удаленном сервере:

- скопируйте файлы docker-compose.yml, docker-compose.prod.yml и nginx.conf
из директории infra на сервер;

- в директории `infra/` создайте `.env` на основе `.env.template`
```
DB_ENGINE - указать СУБД 
DB_NAME - имя базы данных
POSTGRES_USER - логин пользователя базы данных PostgreSQL
POSTGRES_PASSWORD - пароль пользователя базы данных PostgreSQL
DB_HOST - IP адрес сервера базы данных PostgreSQL
DB_PORT - порт сервера базы данных PostgreSQL

DJANGO_SECRET_KEY - секретный ключ
DJANGO_DEBUG - режим работы сервера
```
- для развёртывания с `github action` добавьте в Secrets GitHub переменные
окружения:

```
DB_ENGINE=<django.db.backends.postgresql>
DB_NAME=<имя базы данных postgres>
DB_USER=<пользователь бд>
DB_PASSWORD=<пароль>
DB_HOST=<db>
DB_PORT=<5432>

DOCKER_PASSWORD=<пароль от DockerHub>
DOCKER_USERNAME=<имя пользователя>

SECRET_KEY=<секретный ключ проекта django>
USER=<username для подключения к серверу>
HOST=<IP сервера>
SSH_KEY=< SSH ключ
TELEGRAM_TO=<ID чата, в который придет сообщение>
TELEGRAM_TOKEN=<токен вашего бота>
``` 
  
- на сервере запустите контейнеры через docker-compose:
```
sudo docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```
- только при первом развёртывании проекта на сервере:
    - соберите статические файлы:
    ```
    sudo docker-compose exec web python manage.py collectstatic --noinput
    ```
    - примените миграции:
    ```
    sudo docker-compose exec web python manage.py migrate --noinput
    ```
    - загрузите ингридиенты  в базу данных (необязательно):  

    ```
    sudo docker-compose exec web python manage.py filling -a `приложение` -m `Модель` -f файл из директории static/data `.csv`
    ```
    - cоздать суперпользователя Django:
    ```
    sudo docker-compose exec web python manage.py createsuperuser
    ```
### Документация
После запуска сервера документация API доступна по адресу:
- [swagger](http://foodgram.saper663.ru/api/swagger/)
- [redoc](http://foodgram.saper663.ru/api/docs/)

## Проект в интернете
Проект запущен и доступен по [адресу](http://foodgram.saper663.ru/)

Логин администратора `reviewer`
Пароль администратора `reviewer_2022`

### Автор
Александр

