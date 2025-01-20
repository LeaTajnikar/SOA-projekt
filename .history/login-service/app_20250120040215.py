from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# Nastavi logiranje
logging.basicConfig(level=logging.INFO)

app = FastAPI()

SECRET_KEY='secret'
os.environ["SECRET_KEY"] = SECRET_KEY
  # Privzeti ključ je "secret", ni varen za produkcijo
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
MONGO_URI = os.getenv("MONGO_URI", "mongodb://db:27017/library")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Spremeni to na ["http://localhost:3000"] za večjo varnost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB
client = MongoClient(MONGO_URI)
db = client["library"]
user_collection = db["login"]
user_collection.create_index("username", unique=True)


# Pydantic modeli
class User(BaseModel):
    username: str
    email: EmailStr | None = None
    password: str
    hashed_password: str | None = None
    role: str = "user"


class UserResponse(BaseModel):
    username: str
    email: EmailStr | None = None
    role: str


# Pomožne funkcije
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Odvisnosti
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = user_collection.find_one({"username": username})
        if user is None:
            raise credentials_exception
        return User(**user)
    except JWTError as e:
        logging.error(f"JWTError: {e}")
        raise credentials_exception


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough privileges")
    return current_user


# API Endpoints
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_collection.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        logging.warning(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user.get("role", "user")}, expires_delta=access_token_expires
    )
    logging.info(f"User {user['username']} logged in successfully.")
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: User):
    hashed_password = get_password_hash(user.password)
    new_user = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "role": user.role,
    }
    try:
        user_collection.insert_one(new_user)
        logging.info(f"User {user.username} registered successfully.")
        return {"message": "User registered successfully"}
    except DuplicateKeyError:
        logging.error(f"Registration failed: Username {user.username} already exists.")
        raise HTTPException(status_code=400, detail="Username already exists")


@app.get("/users/me", response_model=UserResponse)
async def get_my_user_data(current_user: User = Depends(get_current_user)):
    return current_user


# Testni endpoint za preverjanje, da deluje
@app.get("/")
async def root():
    return {"message": "Login service is running!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)
