# Async Social Media Backend API

A high-performance, asynchronous REST API for a social media platform built with **FastAPI**, **SQLAlchemy 2.0 (asyncpg)**, **PostgreSQL**, and **ImageKit** for cloud media hosting.

---

## Features

- **Asynchronous Architecture:** Full async I/O database operations powered by `asyncpg` and SQLAlchemy 2.0 async sessions.
- **JWT Authentication & Security:** User registration and login with `bcrypt` password hashing and signed JWT bearer tokens.
- **Cloud Media Uploads:** Direct image upload processing integrated with ImageKit CDN.
- **Post Management (CRUD):** Endpoints to create posts with image attachments, list feed posts, view individual posts, and delete posts with strict user ownership authorization.
- **Interactive Documentation:** Auto-generated interactive Swagger UI and OpenAPI documentation at `/docs`.

---

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL with SQLAlchemy 2.0 & `asyncpg`
- **Authentication:** PyJWT, Passlib (Bcrypt)
- **File Storage:** ImageKit Python SDK
- **Data Validation:** Pydantic v2
- **Server:** Uvicorn

---

## API Endpoints

### Authentication
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/auth/register` | Register a new user | No |
| `POST` | `/auth/login` | Authenticate and obtain JWT token | No |

### Posts
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/posts` | Create a new post with image upload and caption | Yes (Bearer) |
| `GET` | `/posts` | Retrieve all posts feed | Yes (Bearer) |
| `GET` | `/posts/{post_id}` | Retrieve post by ID | Yes (Bearer) |
| `DELETE` | `/posts/{post_id}` | Delete post (owner only) | Yes (Bearer) |

---

## Quickstart

### 1. Installation
Clone the repository and install dependencies using `uv` (recommended) or `pip`:

```bash
git clone https://github.com/eyyub679/social_media_app.git
cd social_media_app
uv sync
```

### 2. Environment Configuration
Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Configure your PostgreSQL database URL, JWT secret key, and ImageKit API credentials:
```ini
DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/social_media_app"
SECRET_KEY="your-secret-key"
IMAGEKIT_PUBLIC_KEY="your-public-key"
IMAGEKIT_PRIVATE_KEY="your-private-key"
IMAGEKIT_URL_ENDPOINT="https://ik.imagekit.io/your_endpoint"
```

### 3. Run the Development Server

```bash
python main.py
```
Or with Uvicorn directly:
```bash
uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload
```

Visit `http://localhost:8000/docs` to test all endpoints interactively.

---

## Development Roadmap (In Progress)

- [x] User registration & bcrypt authentication
- [x] JWT token generation & protected route dependencies
- [x] Cloud image upload via ImageKit
- [x] Post creation, retrieval, and authorized deletion
- [ ] Comment and reply threads
- [ ] Like / reaction counts
- [ ] User profiles, follow/unfollow relationships
- [ ] Frontend integration (React / Next.js)
