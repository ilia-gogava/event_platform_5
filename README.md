# Event Management Platform API

A clean, beginner-friendly Django REST Framework backend for managing events.

## Tech Stack
- Django 4.2+
- Django REST Framework
- Simple JWT (authentication)
- django-filter (filtering)
- drf-spectacular (Swagger docs)

---

## Setup Instructions

### 1. Clone and create virtual environment

```bash
git clone <your-repo-url>
cd event_platform

python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create superuser (for admin panel)

```bash
python manage.py createsuperuser
```

### 5. Start the server

```bash
python manage.py runserver
```

---

## API Endpoints

### Auth
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login → get JWT tokens |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| GET | `/api/auth/me/` | View your profile |
| PATCH | `/api/auth/me/` | Update your profile |

### Events
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/events/` | List all events |
| POST | `/api/events/` | Create event (organizer only) |
| GET | `/api/events/{id}/` | Get one event |
| PATCH | `/api/events/{id}/` | Update event (owner only) |
| DELETE | `/api/events/{id}/` | Delete event (owner only) |

### Filtering Events
```
?status=published
?event_type=online
?category=1
?start_date__gte=2025-01-01
?search=tbilisi
?ordering=start_date
?ordering=-created_at
```

### Registrations
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/events/{id}/registrations/` | List registrations |
| POST | `/api/events/{id}/registrations/` | Register for event |
| PATCH | `/api/events/{id}/registrations/{id}/` | Update status |
| DELETE | `/api/events/{id}/registrations/{id}/` | Cancel registration |

### Reviews
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/events/{id}/reviews/` | List reviews |
| POST | `/api/events/{id}/reviews/` | Create review (confirmed attendee only) |
| PATCH | `/api/events/{id}/reviews/{id}/` | Update your review |
| DELETE | `/api/events/{id}/reviews/{id}/` | Delete your review |

### Categories & Tags
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/categories/` | List categories |
| GET | `/api/tags/` | List tags |

---

## Swagger Docs
Visit: http://127.0.0.1:8000/api/schema/swagger-ui/

## Admin Panel
Visit: http://127.0.0.1:8000/admin/

---

## User Roles
- **organizer** — can create and manage events
- **attendee** — can register for events and leave reviews

Set `role` field during registration.
