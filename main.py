from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# ==================================================
# DATABASE CONNECTION
# ==================================================

DATABASE_URL = "postgresql://postgres:Nihonviji%40553@localhost:5432/JWT"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ==================================================
# JWT CONFIGURATION
# ==================================================

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)

# ==================================================
# REQUEST MODELS
# ==================================================

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str

# ==================================================
# CREATE ACCESS TOKEN
# ==================================================

def create_access_token(data: dict):

    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload.update({"exp": expire})

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

# ==================================================
# GET USER FROM DATABASE
# ==================================================

def get_user(username: str):

    db = SessionLocal()

    result = db.execute(
        text("""
            SELECT username, password, role
            FROM users
            WHERE username = :username
        """),
        {"username": username}
    )

    user = result.fetchone()

    db.close()

    return user

# ==================================================
# JWT VALIDATION
# ==================================================

def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return payload

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

# ==================================================
# ADMIN AUTHORIZATION
# ==================================================

def admin_only(
    current_user=Depends(get_current_user)
):

    if current_user["role"] != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admins only"
        )

    return current_user

# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():

    return {
        "message": "JWT Authentication Project"
    }

# ==================================================
# REGISTER
# ==================================================

@app.post("/register")
def register(data: RegisterRequest):

    db = SessionLocal()

    existing_user = db.execute(
        text("""
            SELECT username
            FROM users
            WHERE username = :username
        """),
        {"username": data.username}
    ).fetchone()

    if existing_user:

        db.close()

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    db.execute(
        text("""
            INSERT INTO users
            (username, password, role)
            VALUES
            (:username, :password, :role)
        """),
        {
            "username": data.username,
            "password": data.password,
            "role": data.role
        }
    )

    db.commit()

    db.close()

    return {
        "message": "User registered successfully"
    }

# ==================================================
# LOGIN
# ==================================================

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    user = get_user(form_data.username)

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    if user.password != form_data.password:

        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    access_token = create_access_token(
        {
            "sub": user.username,
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# ==================================================
# PROFILE
# ==================================================

@app.get("/profile")
def profile(
    current_user=Depends(get_current_user)
):

    return {
        "message": "Welcome",
        "user": current_user
    }

# ==================================================
# ADMIN
# ==================================================

@app.get("/admin")
def admin_dashboard(
    current_user=Depends(admin_only)
):

    return {
        "message": "Welcome Admin",
        "user": current_user
    }

# ==================================================
# DATABASE TEST
# ==================================================

@app.get("/db-test")
def db_test():

    try:

        db = SessionLocal()

        result = db.execute(
            text("SELECT version();")
        )

        version = result.scalar()

        db.close()

        return {
            "message": "Database Connected",
            "postgres_version": version
        }

    except Exception as e:

        return {
            "error": str(e)
        }