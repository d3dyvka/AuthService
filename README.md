# Сервис аутентификации

REST API сервис для регистрации и аутентификации пользователей, построенный на FastAPI с использованием гексагональной архитектуры.

**ВЕРСИЯ PYTHON** - 3.12+

## Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone https://github.com/d3dyvka/AuthService.git
cd AuthService

# 2. Создать .env файл
cp .env.example .env
# Заменить JWT_SECRET, SMTP_USER, SMTP_PASSWORD

# 3. Запустить
docker-compose up --build
```

Swagger документация доступна по адресу: http://localhost:8000/docs

## API

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/auth/register` | Начало регистрации |
| POST | `/auth/register/verify` | Подтверждение email → получение токенов |
| POST | `/auth/login` | Начало входа |
| POST | `/auth/login/verify` | Подтверждение кода → получение токенов |
| POST | `/auth/refresh` | Обновление access токена |
| POST | `/auth/logout` | Выход (отзыв refresh токена) |
| POST | `/auth/resend-code` | Повторная отправка кода |
| POST | `/auth/password/reset` | Запрос сброса пароля |
| POST | `/auth/password/confirm` | Подтверждение нового пароля |
| GET  | `/users/me` | Информация о текущем пользователе |

## Требования к паролю

- Минимум 8 символов
- Минимум одна буква
- Минимум одна цифра

## Запуск тестов

```bash
docker-compose exec app pytest tests/ -v
```

## Структура проекта

```
src/
├── domain/          # Бизнес-логика (entities, exceptions, value objects)
├── application/     # Use cases и порты
├── infrastructure/  # БД, Redis, JWT, Email, конфигурация
└── interfaces/      # HTTP контроллеры, схемы, зависимости
```