from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Query
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
import re

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

class BadgeType(str, Enum):
    FIRST_SUBMISSION = "first_submission"
    EXPERT_SOLVER = "expert_solver"
    INNOVATION_LEADER = "innovation_leader"
    SUSTAINABILITY_CHAMPION = "sustainability_champion"
    TECHNOLOGY_PIONEER = "technology_pioneer"
    HEALTH_ADVOCATE = "health_advocate"
    EDUCATION_INNOVATOR = "education_innovator"
    QUICK_SOLVER = "quick_solver"
    TOP_PERFORMER = "top_performer"

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
    last_login: Optional[datetime] = None

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
    last_login: Optional[datetime] = None

class UserManagement(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole
    points: int
    badges: List[str]
    created_at: datetime
    is_active: bool
    last_login: Optional[datetime] = None

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
    tags: List[str] = []

class ChallengeCreate(BaseModel):
    title: str
    description: str
    category: ChallengeCategory
    difficulty: DifficultyLevel
    deadline: datetime
    criteria: str
    points_reward: int
    tags: List[str] = []

class ChallengeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ChallengeCategory] = None
    difficulty: Optional[DifficultyLevel] = None
    deadline: Optional[datetime] = None
    criteria: Optional[str] = None
    points_reward: Optional[int] = None
    status: Optional[ChallengeStatus] = None
    tags: Optional[List[str]] = None

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
    tags: List[str] = []

class Solution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    challenge_id: str
    user_id: str
    content: str
    files: List[str] = []  # base64 encoded files
    file_names: List[str] = []  # original file names
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    score: Optional[int] = None
    feedback: Optional[str] = None
    evaluated_by: Optional[str] = None
    evaluated_at: Optional[datetime] = None

class SolutionSubmit(BaseModel):
    challenge_id: str
    content: str
    files: List[str] = []
    file_names: List[str] = []

class SolutionResponse(BaseModel):
    id: str
    challenge_id: str
    challenge_title: str
    user_id: str
    user_name: str
    content: str
    files: List[str] = []
    file_names: List[str] = []
    submitted_at: datetime
    score: Optional[int] = None
    feedback: Optional[str] = None
    evaluated_by: Optional[str] = None
    evaluated_at: Optional[datetime] = None

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

class SearchResult(BaseModel):
    challenges: List[ChallengeResponse] = []
    users: List[UserProfile] = []
    total_results: int = 0

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    message: str
    type: str  # "evaluation", "badge", "challenge", "system"
    read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    type: str
    read: bool
    created_at: datetime

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

async def check_and_award_badges(user_id: str):
    """Check and award badges based on user achievements"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        return
    
    current_badges = set(user.get("badges", []))
    new_badges = []
    
    # Get user's solutions
    solutions = await db.solutions.find({"user_id": user_id}).to_list(1000)
    evaluated_solutions = [s for s in solutions if s.get("score") is not None]
    
    # First submission badge
    if len(solutions) >= 1 and BadgeType.FIRST_SUBMISSION not in current_badges:
        new_badges.append(BadgeType.FIRST_SUBMISSION)
    
    # Expert solver badge (5+ evaluated solutions)
    if len(evaluated_solutions) >= 5 and BadgeType.EXPERT_SOLVER not in current_badges:
        new_badges.append(BadgeType.EXPERT_SOLVER)
    
    # Top performer badge (500+ points)
    if user.get("points", 0) >= 500 and BadgeType.TOP_PERFORMER not in current_badges:
        new_badges.append(BadgeType.TOP_PERFORMER)
    
    # Category-specific badges
    category_solutions = {}
    for solution in evaluated_solutions:
        if solution.get("score", 0) >= 80:  # High-scoring solutions
            challenge = await db.challenges.find_one({"id": solution["challenge_id"]})
            if challenge:
                category = challenge.get("category")
                category_solutions[category] = category_solutions.get(category, 0) + 1
    
    # Award category badges (3+ high-scoring solutions in category)
    category_badges = {
        "sustainability": BadgeType.SUSTAINABILITY_CHAMPION,
        "technology": BadgeType.TECHNOLOGY_PIONEER,
        "health": BadgeType.HEALTH_ADVOCATE,
        "education": BadgeType.EDUCATION_INNOVATOR
    }
    
    for category, count in category_solutions.items():
        if count >= 3:
            badge = category_badges.get(category)
            if badge and badge not in current_badges:
                new_badges.append(badge)
    
    # Quick solver badge (submitted within 24 hours of challenge creation)
    quick_solutions = 0
    for solution in solutions:
        challenge = await db.challenges.find_one({"id": solution["challenge_id"]})
        if challenge:
            time_diff = solution["submitted_at"] - challenge["created_at"]
            if time_diff.total_seconds() <= 24 * 3600:  # 24 hours
                quick_solutions += 1
    
    if quick_solutions >= 3 and BadgeType.QUICK_SOLVER not in current_badges:
        new_badges.append(BadgeType.QUICK_SOLVER)
    
    # Update user badges if new ones were earned
    if new_badges:
        all_badges = list(current_badges) + new_badges
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"badges": all_badges}}
        )
        
        # Create notifications for new badges
        for badge in new_badges:
            badge_names = {
                BadgeType.FIRST_SUBMISSION: "Primeira Submissão",
                BadgeType.EXPERT_SOLVER: "Solucionador Expert",
                BadgeType.TOP_PERFORMER: "Alto Desempenho",
                BadgeType.SUSTAINABILITY_CHAMPION: "Campeão da Sustentabilidade",
                BadgeType.TECHNOLOGY_PIONEER: "Pioneiro em Tecnologia",
                BadgeType.HEALTH_ADVOCATE: "Defensor da Saúde",
                BadgeType.EDUCATION_INNOVATOR: "Inovador em Educação",
                BadgeType.QUICK_SOLVER: "Solucionador Rápido"
            }
            
            notification = Notification(
                user_id=user_id,
                title=f"Nova Badge Conquistada! 🏆",
                message=f"Parabéns! Você conquistou a badge '{badge_names.get(badge, badge)}'",
                type="badge"
            )
            await db.notifications.insert_one(notification.dict())

async def create_notification(user_id: str, title: str, message: str, notification_type: str):
    """Create a notification for a user"""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type
    )
    await db.notifications.insert_one(notification.dict())

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
        role=user_data.role,
        last_login=datetime.utcnow()
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
        created_at=user.created_at,
        last_login=user.last_login
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_profile)

@api_router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user["is_active"]:
        raise HTTPException(status_code=401, detail="Account deactivated")
    
    # Update last login
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
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
        created_at=user["created_at"],
        last_login=datetime.utcnow()
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
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

# Challenge Routes
@api_router.post("/challenges", response_model=Challenge)
async def create_challenge(challenge_data: ChallengeCreate, admin_user: User = Depends(get_admin_user)):
    challenge = Challenge(
        **challenge_data.dict(),
        created_by=admin_user.id
    )
    
    await db.challenges.insert_one(challenge.dict())
    
    # Notify all active users about new challenge
    users = await db.users.find({"is_active": True}).to_list(1000)
    for user in users:
        if user["id"] != admin_user.id:  # Don't notify the creator
            await create_notification(
                user["id"],
                "Novo Desafio Disponível! 🎯",
                f"Um novo desafio foi criado: '{challenge.title}'. Participe e ganhe {challenge.points_reward} pontos!",
                "challenge"
            )
    
    return challenge

@api_router.get("/challenges", response_model=List[ChallengeResponse])
async def get_challenges(
    current_user: User = Depends(get_current_user),
    category: Optional[ChallengeCategory] = None,
    difficulty: Optional[DifficultyLevel] = None,
    status: Optional[ChallengeStatus] = None,
    search: Optional[str] = None
):
    # Build filter query
    filter_query = {}
    if category:
        filter_query["category"] = category
    if difficulty:
        filter_query["difficulty"] = difficulty
    if status:
        filter_query["status"] = status
    else:
        filter_query["status"] = ChallengeStatus.ACTIVE  # Default to active challenges
    
    if search:
        filter_query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"tags": {"$in": [re.compile(search, re.IGNORECASE)]}}
        ]
    
    challenges = await db.challenges.find(filter_query).to_list(1000)
    
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

@api_router.put("/challenges/{challenge_id}", response_model=Challenge)
async def update_challenge(challenge_id: str, challenge_update: ChallengeUpdate, admin_user: User = Depends(get_admin_user)):
    challenge = await db.challenges.find_one({"id": challenge_id})
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    update_data = {k: v for k, v in challenge_update.dict().items() if v is not None}
    
    if update_data:
        await db.challenges.update_one({"id": challenge_id}, {"$set": update_data})
        updated_challenge = await db.challenges.find_one({"id": challenge_id})
        return Challenge(**updated_challenge)
    
    return Challenge(**challenge)

@api_router.delete("/challenges/{challenge_id}")
async def delete_challenge(challenge_id: str, admin_user: User = Depends(get_admin_user)):
    challenge = await db.challenges.find_one({"id": challenge_id})
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    await db.challenges.delete_one({"id": challenge_id})
    return {"message": "Challenge deleted successfully"}

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
        files=solution_data.files,
        file_names=solution_data.file_names
    )
    
    await db.solutions.insert_one(solution.dict())
    
    # Check and award badges
    await check_and_award_badges(current_user.id)
    
    return solution

@api_router.get("/solutions", response_model=List[SolutionResponse])
async def get_solutions(admin_user: User = Depends(get_admin_user)):
    solutions = await db.solutions.find().to_list(1000)
    
    solution_responses = []
    for solution in solutions:
        # Get challenge and user info
        challenge = await db.challenges.find_one({"id": solution["challenge_id"]})
        user = await db.users.find_one({"id": solution["user_id"]})
        
        solution_response = SolutionResponse(
            **solution,
            challenge_title=challenge["title"] if challenge else "Unknown",
            user_name=user["name"] if user else "Unknown"
        )
        solution_responses.append(solution_response)
    
    return solution_responses

@api_router.get("/solutions/my", response_model=List[SolutionResponse])
async def get_my_solutions(current_user: User = Depends(get_current_user)):
    solutions = await db.solutions.find({"user_id": current_user.id}).to_list(1000)
    
    solution_responses = []
    for solution in solutions:
        # Get challenge info
        challenge = await db.challenges.find_one({"id": solution["challenge_id"]})
        
        solution_response = SolutionResponse(
            **solution,
            challenge_title=challenge["title"] if challenge else "Unknown",
            user_name=current_user.name
        )
        solution_responses.append(solution_response)
    
    return solution_responses

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
    
    # Create notification for user
    await create_notification(
        solution["user_id"],
        "Solução Avaliada! 📝",
        f"Sua solução foi avaliada e recebeu {evaluation.score} pontos. Feedback: {evaluation.feedback[:100]}...",
        "evaluation"
    )
    
    # Check and award badges after evaluation
    await check_and_award_badges(solution["user_id"])
    
    return {"message": "Solution evaluated successfully"}

# Search Route
@api_router.get("/search", response_model=SearchResult)
async def search(
    q: str = Query(..., description="Search query"),
    current_user: User = Depends(get_current_user)
):
    # Search challenges
    challenge_filter = {
        "status": ChallengeStatus.ACTIVE,
        "$or": [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"tags": {"$in": [re.compile(q, re.IGNORECASE)]}}
        ]
    }
    challenges = await db.challenges.find(challenge_filter).to_list(50)
    
    # Get user's submitted challenges
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
    
    # Search users (admin only)
    users = []
    if current_user.role == UserRole.ADMIN:
        user_filter = {
            "$or": [
                {"name": {"$regex": q, "$options": "i"}},
                {"email": {"$regex": q, "$options": "i"}}
            ]
        }
        user_docs = await db.users.find(user_filter).to_list(20)
        users = [UserProfile(**user) for user in user_docs]
    
    return SearchResult(
        challenges=challenge_responses,
        users=users,
        total_results=len(challenge_responses) + len(users)
    )

# Notification Routes
@api_router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(current_user: User = Depends(get_current_user)):
    notifications = await db.notifications.find({"user_id": current_user.id}).sort("created_at", -1).limit(50).to_list(50)
    return [NotificationResponse(**notification) for notification in notifications]

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: User = Depends(get_current_user)):
    notification = await db.notifications.find_one({"id": notification_id, "user_id": current_user.id})
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    await db.notifications.update_one(
        {"id": notification_id},
        {"$set": {"read": True}}
    )
    return {"message": "Notification marked as read"}

@api_router.put("/notifications/mark-all-read")
async def mark_all_notifications_read(current_user: User = Depends(get_current_user)):
    await db.notifications.update_many(
        {"user_id": current_user.id, "read": False},
        {"$set": {"read": True}}
    )
    return {"message": "All notifications marked as read"}

# User Management (Admin)
@api_router.get("/admin/users", response_model=List[UserManagement])
async def get_all_users(admin_user: User = Depends(get_admin_user)):
    users = await db.users.find().to_list(1000)
    return [UserManagement(**user) for user in users]

@api_router.put("/admin/users/{user_id}/toggle-active")
async def toggle_user_active(user_id: str, admin_user: User = Depends(get_admin_user)):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_status = not user["is_active"]
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"is_active": new_status}}
    )
    
    # Notify user of status change
    status_text = "ativada" if new_status else "desativada"
    await create_notification(
        user_id,
        f"Conta {status_text.capitalize()}",
        f"Sua conta foi {status_text} por um administrador.",
        "system"
    )
    
    return {"message": f"User {'activated' if new_status else 'deactivated'} successfully"}

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
    
    # Additional stats
    total_points_awarded = 0
    solution_cursor = db.solutions.find({"score": {"$ne": None}})
    async for solution in solution_cursor:
        total_points_awarded += solution.get("score", 0)
    
    # Get recent activity
    recent_solutions = await db.solutions.find().sort("submitted_at", -1).limit(5).to_list(5)
    recent_registrations = await db.users.find().sort("created_at", -1).limit(5).to_list(5)
    
    return {
        "total_users": total_users,
        "total_challenges": total_challenges,
        "active_challenges": active_challenges,
        "total_solutions": total_solutions,
        "evaluated_solutions": evaluated_solutions,
        "pending_evaluations": total_solutions - evaluated_solutions,
        "total_points_awarded": total_points_awarded,
        "recent_solutions_count": len(recent_solutions),
        "recent_registrations_count": len(recent_registrations)
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