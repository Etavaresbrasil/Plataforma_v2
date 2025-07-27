from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import bcrypt
import jwt
import base64
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# JWT Configuration
SECRET_KEY = "pucrs_gamification_secret_key_2025"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 720

# Security
security = HTTPBearer()

# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    STUDENT = "student"
    PROFESSOR = "professor"

class ChallengeCategory(str, Enum):
    TECHNOLOGY = "technology"
    SUSTAINABILITY = "sustainability"
    EDUCATION = "education"
    HEALTH = "health"
    INNOVATION = "innovation"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ChallengeStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    EVALUATION = "evaluation"

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    password_hash: str
    role: UserRole
    points: int = 0
    badges: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class UserCreate(BaseModel):
    email: str
    name: str
    password: str
    role: UserRole = UserRole.STUDENT

class UserLogin(BaseModel):
    email: str
    password: str

class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole
    points: int
    badges: List[str]
    created_at: datetime

class Challenge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    category: ChallengeCategory
    difficulty: DifficultyLevel
    deadline: datetime
    criteria: str
    points_reward: int
    status: ChallengeStatus = ChallengeStatus.ACTIVE
    created_by: str  # admin user id
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChallengeCreate(BaseModel):
    title: str
    description: str
    category: ChallengeCategory
    difficulty: DifficultyLevel
    deadline: datetime
    criteria: str
    points_reward: int

class ChallengeResponse(BaseModel):
    id: str
    title: str
    description: str
    category: ChallengeCategory
    difficulty: DifficultyLevel
    deadline: datetime
    criteria: str
    points_reward: int
    status: ChallengeStatus
    created_at: datetime
    can_submit: bool = True
    user_submitted: bool = False

class Solution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    challenge_id: str
    user_id: str
    content: str
    files: List[str] = []  # base64 encoded files
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    score: Optional[int] = None
    feedback: Optional[str] = None
    evaluated_by: Optional[str] = None
    evaluated_at: Optional[datetime] = None

class SolutionSubmit(BaseModel):
    challenge_id: str
    content: str
    files: List[str] = []

class SolutionEvaluate(BaseModel):
    solution_id: str
    score: int
    feedback: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserProfile

class LeaderboardEntry(BaseModel):
    user_id: str
    name: str
    points: int
    badges: List[str]
    rank: int

# Helper Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_data = await db.users.find_one({"id": user_id})
    if user_data is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user_data)

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Authentication Routes
@api_router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=hashed_password,
        role=user_data.role
    )
    
    await db.users.insert_one(user.dict())
    
    # Create token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    user_profile = UserProfile(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        points=user.points,
        badges=user.badges,
        created_at=user.created_at
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_profile)

@api_router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user["is_active"]:
        raise HTTPException(status_code=401, detail="Account deactivated")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"]}, expires_delta=access_token_expires
    )
    
    user_profile = UserProfile(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        role=user["role"],
        points=user["points"],
        badges=user["badges"],
        created_at=user["created_at"]
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_profile)

@api_router.get("/me", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_user)):
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        points=current_user.points,
        badges=current_user.badges,
        created_at=current_user.created_at
    )

# Challenge Routes
@api_router.post("/challenges", response_model=Challenge)
async def create_challenge(challenge_data: ChallengeCreate, admin_user: User = Depends(get_admin_user)):
    challenge = Challenge(
        **challenge_data.dict(),
        created_by=admin_user.id
    )
    
    await db.challenges.insert_one(challenge.dict())
    return challenge

@api_router.get("/challenges", response_model=List[ChallengeResponse])
async def get_challenges(current_user: User = Depends(get_current_user)):
    challenges = await db.challenges.find({"status": ChallengeStatus.ACTIVE}).to_list(1000)
    
    # Check if user has submitted for each challenge
    user_solutions = await db.solutions.find({"user_id": current_user.id}).to_list(1000)
    submitted_challenge_ids = [sol["challenge_id"] for sol in user_solutions]
    
    challenge_responses = []
    for challenge in challenges:
        challenge_response = ChallengeResponse(
            **challenge,
            user_submitted=challenge["id"] in submitted_challenge_ids,
            can_submit=datetime.utcnow() < challenge["deadline"] and challenge["id"] not in submitted_challenge_ids
        )
        challenge_responses.append(challenge_response)
    
    return challenge_responses

@api_router.get("/challenges/{challenge_id}", response_model=ChallengeResponse)
async def get_challenge(challenge_id: str, current_user: User = Depends(get_current_user)):
    challenge = await db.challenges.find_one({"id": challenge_id})
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Check if user has submitted
    user_solution = await db.solutions.find_one({"challenge_id": challenge_id, "user_id": current_user.id})
    
    return ChallengeResponse(
        **challenge,
        user_submitted=user_solution is not None,
        can_submit=datetime.utcnow() < challenge["deadline"] and user_solution is None
    )

# Solution Routes
@api_router.post("/solutions", response_model=Solution)
async def submit_solution(solution_data: SolutionSubmit, current_user: User = Depends(get_current_user)):
    # Check if challenge exists and is active
    challenge = await db.challenges.find_one({"id": solution_data.challenge_id})
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    if challenge["status"] != ChallengeStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Challenge is not active")
    
    if datetime.utcnow() > challenge["deadline"]:
        raise HTTPException(status_code=400, detail="Challenge deadline has passed")
    
    # Check if user already submitted
    existing_solution = await db.solutions.find_one({
        "challenge_id": solution_data.challenge_id,
        "user_id": current_user.id
    })
    if existing_solution:
        raise HTTPException(status_code=400, detail="Solution already submitted for this challenge")
    
    solution = Solution(
        challenge_id=solution_data.challenge_id,
        user_id=current_user.id,
        content=solution_data.content,
        files=solution_data.files
    )
    
    await db.solutions.insert_one(solution.dict())
    return solution

@api_router.get("/solutions", response_model=List[Solution])
async def get_solutions(admin_user: User = Depends(get_admin_user)):
    solutions = await db.solutions.find().to_list(1000)
    return [Solution(**solution) for solution in solutions]

@api_router.get("/solutions/my", response_model=List[Solution])
async def get_my_solutions(current_user: User = Depends(get_current_user)):
    solutions = await db.solutions.find({"user_id": current_user.id}).to_list(1000)
    return [Solution(**solution) for solution in solutions]

@api_router.put("/solutions/evaluate")
async def evaluate_solution(evaluation: SolutionEvaluate, admin_user: User = Depends(get_admin_user)):
    solution = await db.solutions.find_one({"id": evaluation.solution_id})
    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")
    
    # Update solution with evaluation
    await db.solutions.update_one(
        {"id": evaluation.solution_id},
        {
            "$set": {
                "score": evaluation.score,
                "feedback": evaluation.feedback,
                "evaluated_by": admin_user.id,
                "evaluated_at": datetime.utcnow()
            }
        }
    )
    
    # Update user points
    await db.users.update_one(
        {"id": solution["user_id"]},
        {"$inc": {"points": evaluation.score}}
    )
    
    return {"message": "Solution evaluated successfully"}

# Leaderboard Route
@api_router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard():
    users = await db.users.find({"is_active": True}).sort("points", -1).limit(50).to_list(50)
    
    leaderboard = []
    for i, user in enumerate(users):
        entry = LeaderboardEntry(
            user_id=user["id"],
            name=user["name"],
            points=user["points"],
            badges=user["badges"],
            rank=i + 1
        )
        leaderboard.append(entry)
    
    return leaderboard

# Dashboard Stats (Admin)
@api_router.get("/admin/stats")
async def get_admin_stats(admin_user: User = Depends(get_admin_user)):
    total_users = await db.users.count_documents({"is_active": True})
    total_challenges = await db.challenges.count_documents({})
    active_challenges = await db.challenges.count_documents({"status": ChallengeStatus.ACTIVE})
    total_solutions = await db.solutions.count_documents({})
    evaluated_solutions = await db.solutions.count_documents({"score": {"$ne": None}})
    
    return {
        "total_users": total_users,
        "total_challenges": total_challenges,
        "active_challenges": active_challenges,
        "total_solutions": total_solutions,
        "evaluated_solutions": evaluated_solutions,
        "pending_evaluations": total_solutions - evaluated_solutions
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()