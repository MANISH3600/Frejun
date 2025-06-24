# 🏢 Virtual Workspace Room Booking System

This is a RESTful API to manage a shared office setup — allowing users and teams to book **Private Rooms**, **Conference Rooms**, and **Shared Desks** with realistic constraints like time slots, room types, and occupancy limits.

---

## 🚀 Features
- Handles Concurrent Booking Requests Safely
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

# 2. Build and Run
 docker-compose up --build


# 3. Apply Migrations and Create Superuser
In a new terminal:

 docker-compose exec web python manage.py migrate
 docker-compose exec web python manage.py createsuperuser


### Access URLs
Swagger UI: http://localhost:8000/swagger/

Admin Panel: http://localhost:8000/admin/

API Root: http://localhost:8000/api/v1/





### API Endpoints
📌 Users
➕ Create User

POST /api/v1/users/
Body:

{
  "name": "Alice",
  "age": 28,
  "gender": "Female"
}

👥 Teams
➕ Create Team
POST /api/v1/teams/
Body:

{
  "name": "Team Alpha",
  "members": [1, 2, 3]
}


📅 Bookings
➕ Book Room

POST /api/v1/bookings/
Body for Private Room:


{
  "room_type": "PRIVATE",
  "user": 1,
  "slot": "15:00",
  "date": "2025-06-25"
}

Body for Conference Room:

{
  "room_type": "CONFERENCE",
  "team": 1,
  "slot": "16:00",
  "date": "2025-06-25"
}

Body for Shared Desk:

{
  "room_type": "SHARED",
  "user": 2,
  "slot": "15:00",
  "date": "2025-06-25"
}


❌ Cancel Booking
POST /api/v1/cancel/{booking_id}/

📖 View All Bookings

GET /api/v1/bookings/all/

Supports pagination.


🏢 Available Rooms

GET /api/v1/rooms/available/?slot=15:00&date=2025-06-25

Returns available rooms for the given time slot.



⚙️ Room Capacity Rules
Room Type	Limit	Booking Rules
PRIVATE	8	1 user only
CONFERENCE	4	Min 3 team members
SHARED DESK	3	Up to 4 users per desk, auto-filled




### 🧪 Run Tests
## docker-compose exec web python manage.py test


📌 Tech Stack
Python 3.11

Django + DRF

PostgreSQL

Docker + Docker Compose

drf-yasg (Swagger)



