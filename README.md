# JWT_simple_login_creation
Built a FastAPI JWT Authentication system with PostgreSQL integration. Features include user registration, login, JWT token generation and validation, OAuth2 authentication, protected routes, role-based authorization (Admin/User), and Swagger UI testing

# JWT Authentication System using FastAPI

A complete JWT Authentication system built with FastAPI and PostgreSQL. This project demonstrates user registration, login, JWT token generation, JWT validation, OAuth2 authentication, protected routes, and role-based authorization.

## Features

✅ User Registration
✅ User Login
✅ JWT Token Generation
✅ JWT Token Validation
✅ OAuth2 Password Authentication
✅ Role-Based Authorization (Admin/User)
✅ Protected Routes
✅ PostgreSQL Integration
✅ Swagger UI Testing

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Python-JOSE (JWT)
- OAuth2PasswordBearer
- Uvicorn

## Project Workflow

### 1. User Registration

Users can register using:

```http
POST /register