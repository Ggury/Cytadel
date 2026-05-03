from databases import Base, engine, async_session_maker, User, VirtualMachine

from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from schemas import UserCreate, UserOut,LoginRequest, ChangePasswordRequest
from utils  import hash_password, generate_activation_key, verify_password
from tasks import send_activation_code
import json
import asyncio
from datetime import datetime


app = FastAPI(title = "Proxy Service API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3003", "http://localhost:3000", "http://127.0.0.1:3003", "http://127.0.0.1:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message" : "API is running"}

async def get_db():
    async with async_session_maker() as session:
        yield session

@app.post("/register")
async def registration( user_data: UserCreate, db : AsyncSession = Depends(get_db)):
    if user_data.password != user_data.password_confirm:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email  allready registered")

    new_user = User(email = user_data.email,
                    password = hash_password(user_data.password),
                    activation_key = generate_activation_key(),
                    is_active = False)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    send_activation_code.delay(new_user.email, new_user.activation_key)

    return new_user

@app.post("/login")
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    return {
        "status" : "success",
        "user_id" : user.id,
        "is_active" : user.is_active
    }



@app.get("/getkey")
async def get_key(user_id: int, db:AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.activation_key

@app.get("/profile/{user_id}", response_model= UserOut)
async def profile(user_id: int, db:AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id" : user.id,
        "email" : user.email,
        "is_active": user.is_active
    }

@app.post("/refresh_key/{user_id}")
async def refresh_key(user_id: int, db:AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_activation_key = generate_activation_key()
    user.activation_key = new_activation_key
    await db.commit()

    send_activation_code.delay(user.email, user.activation_key)

    return {
        "status": "success",
        "new_key" : new_activation_key
    }

@app.post("/change_password")
async def new_password(
    data: ChangePasswordRequest,
    db:AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == data.user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(data.old_password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")
        
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords dont match")
    
    user.password = hash_password(data.new_password)
    await db.commit()
    return {"status": "success", "message": "password updated"}
    


@app.post("/api/activate-key")
async def activate_key(payload: dict, db: AsyncSession = Depends(get_db)):
    activation_key = payload.get("key")
    if not activation_key:
        raise HTTPException(status_code=400, detail="Key is required")
    result = await db.execute(select(User).where(User.activation_key == activation_key))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Invalid or expired key")

    await db.execute(
        update(VirtualMachine)
        .where(VirtualMachine.current_user_id == user.id)
        .values(current_user_id=None)
    )

    vm_result = await db.execute(
        select(VirtualMachine).where(
            VirtualMachine.current_user_id == None, 
            VirtualMachine.is_active == True
        ).limit(1))
    vm = vm_result.scalar_one_or_none()

    if not vm:
        raise HTTPException(status_code=503, detail="All proxies are busy")

    user.is_active = True
    vm.current_user_id = user.id
    vm.last_used_at = datetime.utcnow()
    
    new_key = generate_activation_key()
    user.activation_key = new_key
    
    await db.commit()

    send_activation_code.delay(user.email, new_key)
    return {
        "status": "connected",
        "user_id": user.id,
        "host": vm.host,
        "port": vm.port,
        "protocol": vm.protocol
    }


@app.websocket("/ws/status/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    try:
        while True:
            async with async_session_maker() as db:
                vm_result = await db.execute(
                    select(VirtualMachine).where(VirtualMachine.current_user_id == user_id)
                )
                vm = vm_result.scalar_one_or_none()
                
                if vm:
                    await websocket.send_json({"status": "connected"})
                else:
                    await websocket.send_json({"status": "disconnected", "message": "Proxy released by server"})
                    break
            
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        async with async_session_maker() as db:
            result = await db.execute(
                select(VirtualMachine).where(VirtualMachine.current_user_id == user_id)
            )
            vms = result.scalars().all()
            for vm in vms:
                vm.current_user_id = None
            await db.commit()
        print(f"User {user_id} disconnected")
