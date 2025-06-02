# Foodgram - онлайн сервис для публикации рецептов и финальный проект курса бэкэнд разработчика Yandex Prakticum
## Основные возможности
- Создание аккаунта и управление им
- Создание новых рецептов
- Подписки на авторов рецептов
- Список покупок, обновляющийся в зависимости от выбранных рецептов и скачиваемый в виде файла
- Добавление рецептов в избранное
## Стек технологий
### **Backend**
- **Python** (основной язык)
- **Django** (веб-фреймворк)
- **Django REST Framework (DRF)** (API)
- **PostgreSQL** (база данных)
- **Docker** (контейнеризация)
- **Nginx** (веб-сервер)
- **Gunicorn** (WSGI-сервер)

### **Аутентификация и безопасность**
- **JWT (JSON Web Tokens)** (`djangorestframework-simplejwt`)
- **Django Auth System** (стандартная аутентификация)

### **Дополнительные библиотеки**
- **Pillow** (работа с изображениями)
- **Django Filter** (фильтрация данных)
- **Psycopg2** (PostgreSQL адаптер)
- **python-dotenv** (переменные окружения)

### **Инфраструктура**
- **Docker Compose** (оркестрация контейнеров)
- **GitHub Actions** (CI/CD)

## Как развернуть
- Клонируйте репозиторий
```bash
git clone https://github.com/npuKoJlucTbl4/foodgram-st.git
```
- Перейдите в директорию infra и создайте там файл окружения .env
```bash
cd \[папка_с_проектом\]/foodgram-st/infra
touch .env
```
- При помощи nano (или другой утилиты) заполните созданный файл
```
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
```
- После этого в этой же директории запустите проект
```bash
docker-compose up
```
- Выполните миграции
```bash
docker-compose exec backend python manage.py migrate
```
- Создайте суперпользователя
```bash
docker-compose run backend python manage.py createsuperuser
```
- Заполните базу данных ингредиентами (ингредиенты загружаются из `data/ingredients.json`, при помощи команды `python manage.py import_ingredients`):
```bash
docker-compose exec backend python manage.py import_ingredients
```
## Адреса приложения
- [Веб-интерфейс](http://localhost/)
- [API документация](http://localhost/api/docs/)
- [Админка](http://localhost/admin/)

## Автор
