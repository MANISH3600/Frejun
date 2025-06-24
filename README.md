# 🏢 Virtual Workspace Room Booking System

This is a RESTful API to manage a shared office setup — allowing users and teams to book **Private Rooms**, **Conference Rooms**, and **Shared Desks** with realistic constraints like time slots, room types, and occupancy limits.

---

## 🚀 Features

- Book, Cancel, and View Bookings
- Check Available Rooms by Time Slot
- Shared Desk Auto-Fill (up to 4 users per desk)
- Team-based Conference Room Booking (min 3 members)
- Enforces Room Limits (8 Private, 4 Conference, 3 Shared)
- Swagger Docs and Admin Panel Included
- Fully Dockerized with PostgreSQL

---



## 🐳 Setup & Running with Docker Compose

### 1. Clone the Repository

git clone https://github.com/MANISH3600/Frejun.git
cd frejun

2. Build and Run
docker-compose up --build


3. Apply Migrations and Create Superuser
In a new terminal:

docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser


