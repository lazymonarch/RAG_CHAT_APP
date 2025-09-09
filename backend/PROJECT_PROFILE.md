# User Management API - Complete Project Profile

## 📋 Project Overview
A clean, production-ready User Management API built with FastAPI, MongoDB, and JWT authentication. Features role-based access control (RBAC) with admin and user roles.

## 🏗️ Architecture

### Tech Stack
- **Framework**: FastAPI 0.116.1
- **Database**: MongoDB Atlas (Cloud)
- **ODM**: Beanie 2.0.0 (Async MongoDB ODM)
- **Authentication**: JWT with python-jose
- **Password Hashing**: bcrypt via passlib
- **Validation**: Pydantic 2.11.7
- **Server**: Uvicorn

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── dependencies.py         # Authentication dependencies
│   ├── auth/                   # Authentication routes
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── users/                  # User management routes
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── core/                   # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py          # Settings and environment
│   │   └── security.py        # Password hashing & JWT
│   ├── db/                     # Database layer
│   │   ├── mongodb.py         # Database connection
│   │   └── mongodb_models.py  # Beanie document models
│   └── schemas/                # Pydantic schemas
│       ├── __init__.py
│       ├── auth.py            # Authentication schemas
│       └── user.py            # User schemas
├── requirements.txt            # Dependencies
├── Dockerfile                 # Container configuration
├── docker-compose.yml         # Docker Compose setup
├── .env                       # Environment variables
└── .env.example              # Environment template
```

## 🗄️ Database Schema

### MongoDB Collections

#### Users Collection
```python
{
  "_id": ObjectId,
  "email": "user@example.com",           # Indexed, Unique
  "hashed_password": "$2b$12$...",       # bcrypt hashed
  "role": "user" | "admin",              # Enum: USER, ADMIN
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### Beanie Document Models

#### User Model (`app/db/mongodb_models.py`)
```python
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class User(BeanieDocument):
    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    role: UserRole = UserRole.USER
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"
```

## 📝 Pydantic Schemas

### User Schemas (`app/schemas/user.py`)

#### Base Schemas
```python
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.USER

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    role: UserRole | None = None

class AdminUserCreate(UserBase):
    password: str
    role: UserRole = UserRole.USER
```

#### Response Schemas
```python
class UserOut(UserBase):
    id: str
    role: UserRole
    created_at: datetime

class AdminCreateResponse(BaseModel):
    user: UserOut
    access_token: str
    token_type: str = "bearer"
```

### Auth Schemas (`app/schemas/auth.py`)
```python
class LoginRequest(BaseModel):
    email: str
    password: str
```

## 🔐 Authentication System

### JWT Configuration (`app/core/security.py`)
```python
# Password hashing with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

### Dependencies (`app/dependencies.py`)
```python
# JWT Authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Validates JWT and returns User object

# Role-based Access Control
async def require_admin(current_user: User = Depends(get_current_user)):
    # Requires admin role

async def require_user_or_admin(current_user: User = Depends(get_current_user)):
    # Requires user or admin role
```

## 🛣️ API Routes

### Authentication Routes (`/auth`)

| Method | Endpoint | Description | Auth Required | Role Required |
|--------|----------|-------------|---------------|---------------|
| POST | `/auth/register` | Register new user | ❌ | None |
| POST | `/auth/login` | User login | ❌ | None |
| GET | `/auth/me` | Get current user | ✅ | Any |

### User Management Routes (`/users`)

| Method | Endpoint | Description | Auth Required | Role Required |
|--------|----------|-------------|---------------|---------------|
| POST | `/users/` | Create user | ❌ | None |
| GET | `/users/` | List all users | ✅ | Admin |
| GET | `/users/{user_id}` | Get user by ID | ✅ | Admin |
| PUT | `/users/{user_id}` | Update user | ✅ | Admin |
| DELETE | `/users/{user_id}` | Delete user | ✅ | Admin |
| GET | `/users/admin/count` | Get admin count | ❌ | None |
| POST | `/users/admin/create` | Create admin (max 2) | ❌ | None |
| GET | `/users/me/profile` | Get my profile | ✅ | User/Admin |
| PUT | `/users/me/profile` | Update my profile | ✅ | User/Admin |
| DELETE | `/users/me/profile` | Delete my profile | ✅ | User/Admin |

## ⚙️ Configuration

### Environment Variables (`.env`)
```bash
# MongoDB Configuration
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority&appName=ClusterName
DATABASE_NAME=user_management_db

# Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Settings (`app/core/config.py`)
```python
class Settings(BaseSettings):
    PROJECT_NAME: str = "User Management API"
    MONGODB_URL: str
    DATABASE_NAME: str = "user_management_db"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
```

## 🔒 Security Features

### Password Security
- **Hashing**: bcrypt with 12 rounds
- **Validation**: Pydantic EmailStr validation
- **Storage**: Never store plain text passwords

### JWT Security
- **Algorithm**: HS256
- **Expiration**: 30 minutes (configurable)
- **Claims**: User ID in 'sub' claim
- **Validation**: Automatic token validation

### Role-Based Access Control (RBAC)
- **Admin Role**: Full system access
- **User Role**: Limited to own profile
- **Public Endpoints**: Registration, login, admin count
- **Admin Creation**: Limited to 2 admin users

## 🚀 Deployment

### Docker Configuration
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=${MONGODB_URL}
      - SECRET_KEY=${SECRET_KEY}
    restart: unless-stopped
```

## 📦 Dependencies

### Core Dependencies (`requirements.txt`)
```
fastapi==0.116.1
uvicorn[standard]==0.35.0
starlette==0.47.3
motor==3.7.1
pymongo==4.14.1
beanie==2.0.0
passlib[bcrypt]==1.7.4
python-jose==3.5.0
bcrypt==4.0.1
pydantic==2.11.7
pydantic-settings==2.10.1
pydantic-core==2.33.2
email-validator==2.3.0
python-multipart==0.0.20
python-dotenv==1.1.1
```

## 🧪 API Testing Examples

### 1. Register User
```bash
curl -X POST "http://localhost:8000/auth/register?email=user@example.com&password=password123"
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### 3. Create Admin
```bash
curl -X POST "http://localhost:8000/users/admin/create" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'
```

### 4. Get All Users (Admin)
```bash
curl -X GET "http://localhost:8000/users/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 5. Get My Profile
```bash
curl -X GET "http://localhost:8000/users/me/profile" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🔧 Key Features

### ✅ Implemented
- User registration and authentication
- JWT-based authentication
- Role-based access control (Admin/User)
- Password hashing with bcrypt
- MongoDB integration with Beanie ODM
- Admin user creation (limited to 2)
- Profile management
- Comprehensive API documentation (Swagger UI)
- Docker containerization
- Environment-based configuration

### 🎯 Production Ready
- Clean, minimal codebase
- Proper error handling
- Security best practices
- Scalable architecture
- Comprehensive documentation
- Docker deployment ready

## 📚 Next Steps for New Projects

1. **Copy the core structure** (auth, users, core, db, schemas)
2. **Update environment variables** for new project
3. **Modify database models** as needed
4. **Add new API routes** following the same pattern
5. **Update Swagger documentation** in main.py
6. **Test with the provided examples**

This profile provides a complete reference for building similar user management systems with FastAPI and MongoDB.
