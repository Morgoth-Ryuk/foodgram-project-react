# praktikum_new_diplom
Проект Foodgram.

Является блогом для публикации рецептов.
Есть возможности:
* Просматривать рецепты.
* Добавлять рецепты в избранное.
* Подписоваться на авторов рецептов.
* Добавлять рецепты в корзину.
* Скачивать отложенные в корзину списки покупок.

```
[https://cherkasovaproject13.ddns.net/
Юзер для входа на сайт и админку:
Адрес электронной почты: testuser@mail.ru](https://cherkasovaproject13.ddns.net/
Юзер для входа на сайт и админку:
Адрес электронной почты: testuser@mail.ru
Никнэйм пользователя: TestUser
Пароль: TestUse)
```

### Как запустить бэкэнд часть проекта:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Morgoth-Ryuk/foodgram-project-react.git
```

```
cd foodgram-project-react
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

### Как запустить весь проект:

```
cd foodgram-project-react/infra
```

Запустить сборку docker compose
```
sudo docker compose -f docker-compose.production.yml -d
```

Внутри контейнера сделать миграции:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py makemigrations
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate

```

Собрать статику и копировать её:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/backend_static/. /backend_static/static/ 
```
