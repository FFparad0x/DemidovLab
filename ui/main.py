from fastapi import Depends, FastAPI, HTTPException, status, Request, Header
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware
import os

name = os.getenv("TARGET_HOST", "127.0.0.1:8001")
print(f"Hello from NAVEC target host: {name}")

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "num": 0,
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="html")

def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: str | None = None
    disabled: bool | None = None
    num: int | None = None

class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print(form_data)
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        fake_users_db[form_data.username] = {}
        fake_users_db[form_data.username]["username"] = form_data.username
        fake_users_db[form_data.username]["hashed_password"] = fake_hash_password(form_data.password)
        fake_users_db[form_data.username]["disabled"] = False
        fake_users_db[form_data.username]["num"] = 0
    user_dict = fake_users_db.get(form_data.username)
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/")
async def search(request: Request):
    return templates.TemplateResponse("index.html", {"request": request,"name": name})


@app.get("/login")
async def logpage(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/users/count")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    fake_users_db[current_user.username]["num"] += 1
    return fake_users_db[current_user.username]["num"]


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user.num


@app.post("/register")
def register(username: str, password: str): # use Header as a dependency
    fake_users_db[username]={}
    fake_users_db[username]["username"] = username
    fake_users_db[username]["hashed_password"] = fake_hash_password(password)
    fake_users_db[username]["disabled"] = False
    fake_users_db[username]["num"] = 0
    resp = RedirectResponse("/try", headers={"Authorization": f"Bearer {password}"})  # pass the token as a header in the redirect response

    return resp
