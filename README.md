# 🏨 Hotel Room Booking Application
* [Документация на русском](README.ru.md)
* [Docs in english](README.md)

**Django / Django REST Framework — Technical Assignment**

---

## 🚀 Quick Start — Run the Project Locally

### Option 1: Docker (recommended)
* **Admin User:** Automatically created using credentials from your `.env` file:

  * **Username:** `admin`
  * **Password:** `admin`

```bash
cp .env.example .env
docker-compose up --build
```

* Web app: [http://localhost:8000](http://localhost:8000)
* Admin panel: [http://localhost:8000/admin](http://localhost:8000/admin)
* Swagger UI: [http://localhost:8000/api/docs/swagger/](http://localhost:8000/api/docs/swagger/)
* Redoc: [http://localhost:8000/api/docs/redoc/](http://localhost:8000/api/docs/redoc/)

---

## 🧾 Technical Assignment — Compliance Checklist

### Core requirements

* ✅ Room fields:

  * name / number
  * price per night
  * capacity
* ✅ Filter rooms by price
* ✅ Filter rooms by capacity
* ✅ Sort rooms
* ✅ Search free rooms by date range
* ✅ Book a free room
* ✅ Cancel booking (user & admin)
* ✅ User registration
* ✅ User authentication
* ✅ Booking only for authenticated users
* ✅ Public room browsing
* ✅ Users see only their own bookings
* ✅ Django Admin for rooms & bookings
* ✅ Django + DRF used
* ✅ PostgreSQL supported (not SQLite in production)

### Nice-to-have (implemented)

* ✅ Automated tests (pytest)
* ✅ Type annotations
* ✅ Linter & formatter (flake8, black, isort)
* ✅ API documentation (Swagger / Redoc)
* ✅ Dockerized setup
* ✅ Production-ready stack (Gunicorn + WhiteNoise)

---

## 📌 Project Overview

A production-oriented hotel room booking application built with **Django** and **Django REST Framework**.

The system supports:

* room browsing and filtering,
* availability search by date range,
* secure booking workflow,
* role-based access (users / admins),
* both Web UI and REST API usage.

The project was implemented as a **technical interview assignment**, following best practices for backend development.

---

## ✨ Features

* Room management (name, price, capacity)
* Filtering & sorting
* Availability search
* Booking & cancellation
* User authentication (JWT)
* Django Admin for superusers
* REST API + Swagger / Redoc
* Docker & CI-ready setup

---

## 🧱 Tech Stack

* **Backend:** Django, Django REST Framework
* **Auth:** JWT (`djangorestframework-simplejwt`)
* **Database:** PostgreSQL
* **Static files:** WhiteNoise
* **WSGI:** Gunicorn
* **API Docs:** drf-spectacular
* **Testing:** pytest, pytest-django
* **Code quality:** black, flake8, isort
* **Frontend:** Django templates + Bootstrap 5

---

## 🔐 Data Validation & Concurrency

* Booking date validation (`end_date > start_date`)
* Overlapping booking protection
* Atomic transactions with `select_for_update()`

---

## 🧪 Tests & CI

* Model tests
* API tests
* Permission tests
* Filters & availability logic tests
* CI pipeline running linters and tests on every push

---

## 🔒 Security Notes

* Environment-based settings
* Secure cookies & headers
* PostgreSQL for production
* No SQLite in production environment

---

## 📜 License

See the `LICENSE` file for details.

# Media

### 🏠 Main Page — Room List & Search

Public page with room listing, filtering, sorting and availability search.

![Main Page](https://i.imgur.com/7iEYAeo.png)

---

### 🛠️ Django Admin Panel

Room and booking management available for superusers.

![Admin Panel](https://i.imgur.com/ghjApw0.png)

---

### 📘 Swagger UI — API Documentation

Interactive API documentation generated with **drf-spectacular**.

![Swagger UI](https://i.imgur.com/MZ3ptJa.png)

---

### 📄 OpenAPI Schema (Redoc)

Readable OpenAPI documentation for the REST API.

![OpenAPI Redoc](https://i.imgur.com/TZPMeQi.png)
