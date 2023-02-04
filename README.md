### Описание проекта:

Проект Foodgram позволяет публиковать рецепты, подписываться на 
публикации других пользователей, добавлять понравившиеся рецепты в «Избранное», 
а перед походом в магазин скачивать сводный список продуктов, 
необходимых для приготовления одного или нескольких выбранных блюд.

Проект запущен по адресу: http://130.193.39.213/

Документация по API: http://130.193.39.213/api/docs/

Админка
Login: marsel
Password: marsel

### Используемые технологии:
- Python 3.8.6  
- Django 2.2.16  
- Django REST Framework 3.12.4  
- Djoser 2.1.0  
- PostgreSQL
- Docker
- Docker Compose
- GitHub Actions 


### Как запустить проект локально в docker-контейнерах:

Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone git@github.com:Marsel168/foodgram-project-react.git
```

```bash
cd foodgram-project-react
```

Перейти в папку infra и подготовить файл переменных окружения .env:

```bash
cd infra
```

Скопировать шаблон из файла .env.example:
```bash
cp .env.example .env
```

Заполнить его следующими данными:
```
SECRET_KEY='Django_SECRET_KEY'  # секретный ключ Django (укажите свой)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=foodgram # имя БД
POSTGRES_USER=postgres  # логин для подключения к БД
POSTGRES_PASSWORD=postgres  # пароль для подключения к БД (установите свой)
DB_HOST=db  # название сервиса (контейнера)
DB_PORT=5432  # порт для подключения к БД
```

### Подготовка сервера

1. Войдите на свой удаленный сервер в облаке.
    
2. Остановите службу nginx:
```
 sudo systemctl stop nginx 
```

3. Установите docker:
```
sudo apt install docker.io 
```

4. Установите docker-compose, с этим вам поможет  [официальная документация](https://docs.docker.com/compose/install/).
    
5. Скопируйте файлы  _docker-compose.yaml_  и  _nginx/default.conf_  из проекта на сервер в  _home/<ваш_username>/docker-compose.yaml_  и  _home/<ваш_username>/nginx/default.conf_  соответственно.
    

Эти файлы всегда копируются вручную. Обычно они настраиваются один раз и изменения в них вносятся крайне редко.

6. Добавьте в Secrets GitHub Actions переменные окружения для работы базы данных и деплоя.


Заполните данными таблицу ингредиентов:
```
docker compose exec backend python manage.py load_csv_data
```

Для создания суперпользователя, используйте:
```
docker compose exec backend python manage.py createsuperuser
```

Соберите статические файлы в единое место (--no-input - без запроса параметров у пользователя):

```
docker-compose exec backend python manage.py collectstatic --no-input
```

Для остановки работы контейнера, удаления его и томов используйте:

```
docker-compose down -v
```

___________________________________
### Автор
[**Марсель Галиаскаров**](https://github.com/Marsel168)

