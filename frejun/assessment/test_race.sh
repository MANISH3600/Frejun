#!/bin/bash
for i in {1..3}; do
  curl -X POST http://localhost:8000/api/v1/bookings/ \
    -H "Content-Type: application/json" \
    -d '{"room_type": "PRIVATE", "user": '$i', "slot": "15:30", "date": "2025-06-25"}' &
done
wait