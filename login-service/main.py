from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import secrets
import uvicorn

app = FastAPI()

SECRET_KEY = "secret"  # Insecure - change this for production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class User(BaseModel):
    username: str
    email: str | None = None
    password: str
    hashed_password: str | None = None
    role: str = "user"

MONGO_URI = 'mongodb+srv://Lea:123leici@cluster0.iupgk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
client = MongoClient(MONGO_URI)
db = client["library"]
user_collection = db["login"]
user_collection.create_index("username", unique=True)

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
    except JWTError:
        raise credentials_exception

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough privileges")
    return current_user

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_collection.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user.get("role", "user")}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: User):
    hashed_password = get_password_hash(user.password)
    new_user = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "role": user.role
    }
    try:
        user_collection.insert_one(new_user)
        return {"message": "User registered successfully"}
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Username already exists")

@app.get("/users/")
async def get_all_users(current_user: User = Depends(get_current_active_user)):
    users = list(user_collection.find({}, {"_id": 0, "hashed_password": 0}))
    return users

@app.get("/users/me")
async def get_my_user_data(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/users/update_email")
async def update_my_email(email: str, current_user: User = Depends(get_current_user)):
    user_collection.update_one({"username": current_user.username}, {"$set": {"email": email}})
    return {"message": "Email updated successfully"}

@app.post("/users/{username}/admin_update")
async def admin_update_user_email(username: str, email: str, current_user: User = Depends(get_current_active_user)):
    user_collection.update_one({"username": username}, {"$set": {"email": email}})
    return {"message": f"Email updated for {username}"}

@app.put("/users/me")
async def update_my_user_data(user_data: User, current_user: User = Depends(get_current_user)):
    update_data = user_data.model_dump(exclude={"password", "hashed_password"})
    user_collection.update_one({"username": current_user.username}, {"$set": update_data})
    return {"message": "User data updated successfully"}

@app.put("/users/{username}")
async def update_user(username: str, user_data: User, current_user: User = Depends(get_current_active_user)):
    update_data = user_data.model_dump(exclude={"password", "hashed_password"})  # Exclude password fields
    user_collection.update_one({"username": username}, {"$set": update_data})
    return {"message": f"User {username} updated successfully"}


@app.delete("/users/me")
async def delete_my_account(current_user: User = Depends(get_current_user)):
    user_collection.delete_one({"username": current_user.username})
    return {"message": "Account deleted successfully"}

@app.delete("/users/{username}")
async def delete_user(username: str, current_user: User = Depends(get_current_active_user)):
    user_collection.delete_one({"username": username})
    return {"message": f"User {username} deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8010)

