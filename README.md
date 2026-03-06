# 💬 Real-Time Chat Application

A production-ready real-time chat application built with Django Channels and WebSockets, featuring JWT authentication, private and group messaging, read receipts, and Google Cloud VM deployment.

---

## 📋 Table of Contents

- [Tech Stack](#tech-stack)
- [Features](#features)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Running the Project](#running-the-project)
- [Running with Docker](#running-with-docker)
- [API Endpoints](#api-endpoints)
- [WebSocket Events](#websocket-events)
- [Authentication](#authentication)
- [API Documentation](#api-documentation)
- [Deployment on Google Cloud VM](#deployment-on-google-cloud-vm)

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Framework | Django 4.x + Django REST Framework |
| Real-time | Django Channels (WebSocket) |
| Channel Layer | Redis 7 |
| Database | PostgreSQL 15 |
| Auth | JWT (SimpleJWT) |
| ASGI Server | Daphne |
| Reverse Proxy | Nginx |
| Docs | drf-spectacular (Swagger + ReDoc) |
| Container | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Cloud | Google Cloud VM (e2-micro) |

---

## ✨ Features

- JWT Authentication (register, login, logout, token refresh)
- Real-time messaging via WebSocket
- Private one-to-one chat
- Group chat with multiple members
- Read receipts with double tick indicators
- Online/offline status tracking
- Message history via REST API
- Paginated conversations and messages
- Redis as WebSocket channel layer
- Swagger UI + ReDoc documentation
- Dockerized with PostgreSQL and Redis
- GitHub Actions CI/CD for auto-deployment

---

## 📁 Project Structure

```
chat_app/
├── core/
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   ├── asgi.py                ← ASGI config for Channels
│   ├── wsgi.py
│   └── jwt_auth_middleware.py ← Custom JWT WebSocket auth
├── accounts/
│   ├── models.py              ← Custom User model
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── chat/
│   ├── models.py              ← Conversation, Message, ReadStatus
│   ├── serializers.py
│   ├── views.py               ← REST endpoints
│   ├── urls.py
│   ├── consumers.py           ← WebSocket consumer
│   └── routing.py             ← WebSocket URL routing
├── .github/
│   └── workflows/
│       └── deploy.yml         ← GitHub Actions CI/CD
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
└── manage.py
```

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 15
- Redis 7
- pip

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/chat_app.git
cd chat_app
```

### 2. Create and activate virtual environment

```bash
python3.11 -m venv env
source env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create PostgreSQL database

```bash
psql postgres
CREATE DATABASE chat_db;
\q
```

### 5. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your values
```

### 6. Run migrations

```bash
python manage.py migrate
```

### 7. Create superuser

```bash
python manage.py createsuperuser
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=chat_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://127.0.0.1:6379
```

---

## 🚀 Running the Project

```bash
# Start Redis
brew services start redis   # Mac
# or
sudo service redis start    # Linux

# Verify Redis
redis-cli ping   # Should return PONG

# Start server
python manage.py runserver
```

Server runs at `http://127.0.0.1:8000`

---

## 🐳 Running with Docker

```bash
# Build and start all containers
docker-compose up -d --build

# Check container status
docker-compose ps

# Create superuser
docker-compose exec web python manage.py createsuperuser

# View logs
docker-compose logs -f web

# Stop containers
docker-compose down
```

Containers started:
- `chat_web` — Django app on port 8000 (via Daphne)
- `chat_db` — PostgreSQL on port 5433
- `chat_redis` — Redis on port 6380

---

## 📡 API Endpoints

### Auth — `/api/v1/auth/`

| Method | Endpoint | Description | Permission |
|---|---|---|---|
| POST | `/register/` | Register new user | Public |
| POST | `/login/` | Login and get tokens | Public |
| POST | `/logout/` | Blacklist refresh token | Authenticated |
| POST | `/token/refresh/` | Get new access token | Authenticated |
| GET/PATCH | `/profile/` | View or update own profile | Authenticated |
| GET | `/users/` | List all users | Authenticated |

### Chat — `/api/v1/`

| Method | Endpoint | Description | Permission |
|---|---|---|---|
| GET | `/conversations/` | List my conversations | Authenticated |
| POST | `/conversations/private/` | Start private chat | Authenticated |
| POST | `/conversations/group/` | Create group chat | Authenticated |
| GET | `/conversations/<id>/` | Get conversation details | Member only |
| GET | `/conversations/<id>/messages/` | Get message history | Member only |
| POST | `/conversations/<id>/read/` | Mark messages as read | Member only |

---

## 🔌 WebSocket Events

### Connect

```
ws://localhost:8000/ws/chat/<conversation_id>/?token=<access_token>
```

### Send Message (Client → Server)

```json
{
    "type": "message.send",
    "content": "Hello!"
}
```

### Receive Message (Server → Client)

```json
{
    "type": "message.receive",
    "message_id": 1,
    "content": "Hello!",
    "sender_id": 1,
    "sender_username": "alice",
    "created_at": "2026-03-04T10:00:00Z"
}
```

### Send Read Receipt (Client → Server)

```json
{
    "type": "message.read",
    "message_id": 1
}
```

### Receive Read Receipt (Server → Client)

```json
{
    "type": "read.receipt",
    "message_id": 1,
    "user_id": 2,
    "username": "bob"
}
```

### Online/Offline Status (Server → Client)

```json
{
    "type": "user.status",
    "user_id": 1,
    "username": "alice",
    "is_online": true
}
```

---

## 🔑 Authentication

This API uses JWT (JSON Web Tokens). WebSocket connections also authenticate via JWT passed as a query parameter.

### Register

```bash
POST /api/v1/auth/register/
{
    "username": "alice",
    "email": "alice@chat.com",
    "password": "Test@1234",
    "password2": "Test@1234",
    "first_name": "Alice",
    "last_name": "Smith"
}
```

### Use the token in REST requests

```
Authorization: Bearer <your_access_token>
```

### Use the token in WebSocket

```
ws://localhost:8000/ws/chat/1/?token=<your_access_token>
```

Token lifetimes:
- Access token: **60 minutes**
- Refresh token: **7 days**

---

## 📖 API Documentation

With the server running, visit:

| URL | Description |
|---|---|
| `http://127.0.0.1:8000/api/docs/` | Swagger UI — interactive |
| `http://127.0.0.1:8000/api/redoc/` | ReDoc — readable docs |
| `http://127.0.0.1:8000/api/schema/` | Raw OpenAPI JSON |

---

## ☁️ Deployment on Google Cloud VM

### Architecture

```
Internet
    │
    ▼
Google Cloud Firewall (port 80, 443)
    │
    ▼
Nginx (port 80)
    │  ├── /static/  → staticfiles/
    │  ├── /media/   → media/
    │  ├── /ws/      → WebSocket → Daphne
    │  └── /api/     → HTTP → Daphne
    ▼
Daphne (unix socket)
    │
    ▼
Django Channels + REST API
    │            │
    ▼            ▼
PostgreSQL     Redis
```

### Quick Setup

```bash
# SSH into VM
gcloud compute ssh ubuntu@chat-app-server --zone=us-central1-a

# Install dependencies
sudo apt update && sudo apt install -y python3.11 python3.11-venv nginx postgresql redis-server

# Clone and setup project
git clone https://github.com/yourusername/chat_app.git
cd chat_app
python3.11 -m venv env
source env/bin/activate
pip install -r requirements.txt daphne

# Run migrations
python manage.py migrate
python manage.py collectstatic --noinput

# Start Daphne as service
sudo systemctl start daphne
sudo systemctl enable daphne

# Start Nginx
sudo systemctl restart nginx
```

### CI/CD

Every `git push` to `main` automatically:
1. Pulls latest code on VM
2. Installs new dependencies
3. Runs migrations
4. Collects static files
5. Restarts Daphne and Nginx

---

## 👨‍💻 Built With

- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Channels](https://channels.readthedocs.io/)
- [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [drf-spectacular](https://drf-spectacular.readthedocs.io/)
- [channels-redis](https://github.com/django/channels_redis)
- [Daphne](https://github.com/django/daphne)