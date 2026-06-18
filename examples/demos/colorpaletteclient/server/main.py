# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

DATA_DIR = Path(__file__).parent / "assets"

COLORS_PATH = DATA_DIR / "colors.json"
SESSIONS_PATH = DATA_DIR / "sessions.json"
USERS_PATH = DATA_DIR / "users.json"

with open(COLORS_PATH) as f:
    colors = json.load(f)
with open(SESSIONS_PATH) as f:
    sessions = json.load(f)
with open(USERS_PATH) as f:
    users = json.load(f)

# In-memory token store (token: email)
tokens = {}


def get_user_by_email(email):
    for u in users:
        if u["email"] == email:
            return u
    return None


def get_color_by_id(cid):
    for c in colors:
        if c.get("id") == cid:
            return c
    return None


def require_auth(request: Request):
    token = request.headers.get("token")
    if not token or token not in tokens:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return tokens[token]


app = FastAPI()

app.mount("/img/faces", StaticFiles(directory=DATA_DIR / "img"), name="faces")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    email: str
    password: str


class Color(BaseModel):
    name: str
    color: str
    pantone_value: str
    id: Optional[int] = None


@app.post("/api/logout")
def logout(request: Request, user=Depends(require_auth)):
    token = request.headers.get("token")
    if token in tokens:
        del tokens[token]
    return {"ok": True}


@app.post("/api/login")
def login(data: LoginRequest):
    for s in sessions:
        if s["email"] == data.email and s["password"] == data.password:
            token = f"token-{data.email}"
            tokens[token] = data.email
            user = get_user_by_email(data.email)
            return {"token": token, "id": user.get("id", 1) if user else 1}
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/api/unknown")
def list_colors():
    return {"data": colors, "total_pages": 1, "page": 1}


@app.get("/api/colors/{cid}")
def get_color(cid: int):
    c = get_color_by_id(cid)
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    return c


@app.post("/api/colors")
def add_color(color: Color, user=Depends(require_auth)):
    color.id = (
        max((c.get("id", 0) for c in colors), default=0) + 1
        if color.id is None
        else color.id
    )
    colors.append(color.dict())
    return color


@app.put("/api/colors/{cid}")
def update_color(cid: int, color: Color, user=Depends(require_auth)):
    c = get_color_by_id(cid)
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    c.update(color.dict(exclude_unset=True))
    return c


@app.delete("/api/colors/{cid}")
def delete_color(cid: int, user=Depends(require_auth)):
    c = get_color_by_id(cid)
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    colors.remove(c)
    return {"ok": True}


@app.get("/api/users")
def list_users():
    return {"data": users, "total_pages": 1, "page": 1}


@app.get("/api/users/{email}")
def get_user(email: str):
    u = get_user_by_email(email)
    if not u:
        raise HTTPException(status_code=404, detail="Not found")
    return u
