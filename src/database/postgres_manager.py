import os
import uuid
import bcrypt
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Text, ForeignKey, DateTime,Integer
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Fetch the database URL. Falls back to local SQLite if the .env variable is missing
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mjuziai_local.db")

# Create the database engine with pool_pre_ping to handle Neon serverless sleep states
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,  # Checks connection before querying
    pool_recycle=300     # Recycles idle connections after 5 minutes
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# DATABASE SCHEMA (TABLES)
# ==========================================

class Organization(Base):
    """Stores Enterprise Clients and their verified email domains."""
    __tablename__ = "organizations"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    email_domain = Column(String, unique=True, nullable=False) # e.g., 'safaricom.co.ke'
    deployment_mode = Column(String, default="platform") # 'platform' or 'widget'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationship: An organization has many users
    users = relationship("User", back_populates="organization")

class User(Base):
    """Stores all users: Public users, Enterprise Employees, and Admins."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    
    # Core roles: 'user' (public), 'employee' (corporate), 'admin' (tech guy)
    role = Column(String, default="user", nullable=False) 
    #  Subscription and Limits tracking
    subscription_tier = Column(String, default="free", nullable=False) # 'free', 'pro', 'enterprise'
    daily_query_count = Column(Integer, default=0)
    last_query_date = Column(String, nullable=True) # Stored as YYYY-MM-DD

    # Nullable because public users don't belong to an organization
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=True) 
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    organization = relationship("Organization", back_populates="users")
    sessions = relationship("ChatSession", back_populates="user")

class ChatSession(Base):
    """Groups messages into specific conversation threads."""
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    session_title = Column(String, default="New Chat")
    collection_name = Column(String, nullable=True) # Tracks which knowledge base they are talking to
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    """Individual messages inside a chat session."""
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False) # 'user' or 'ai'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    session = relationship("ChatSession", back_populates="messages")


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

def init_db():
    """Creates all tables in the database. Run this once on startup."""
    # UNCOMMENT the drop_all line temporarily to clear the old tables!
    # Base.metadata.drop_all(bind=engine) 
    Base.metadata.create_all(bind=engine)
    print(" Database Tables Wiped and Re-Initialized Successfully in PostgreSQL!")

# ==========================================
# SECURITY HELPER FUNCTIONS
# ==========================================

def hash_password(password: str) -> str:
    """Hashes a password securely using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks a plain password against the stored hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# ==========================================
# AUTHENTICATION & REGISTRATION LOGIC
# ==========================================

def register_smart_user(email: str, full_name: str, plain_password: str):
    """
    Auto-routing registration: Extracts the domain from the email. 
    If the domain matches a registered enterprise, makes them an 'employee'. 
    Otherwise, makes them a public 'user'.
    """
    db = SessionLocal()
    
    # Check if user already exists
    if db.query(User).filter(User.email == email.lower()).first():
        db.close()
        return False, "Email already registered."
        
    try:
        # Extract the domain (e.g., 'john@acmecorp.com' -> 'acmecorp.com')
        domain = email.split('@')[-1].lower()
        
        # Check if an organization owns this domain
        org = db.query(Organization).filter(Organization.email_domain == domain).first()
        
        assigned_role = "employee" if org else "user"
        assigned_org_id = org.id if org else None
        # Employees automatically get the Enterprise tier paid by their admin
        assigned_tier = "enterprise" if org else "free"

        new_user = User(
            id=f"usr_{uuid.uuid4().hex[:12]}",
            email=email.lower(),
            full_name=full_name,
            password_hash=hash_password(plain_password),
            role=assigned_role,
            organization_id=assigned_org_id
        )
        db.add(new_user)
        db.commit()
        
        result = {"id": new_user.id, "role": new_user.role, "org_id": new_user.organization_id}
        db.close()
        return True, result
    except Exception as e:
        db.rollback()
        db.close()
        return False, str(e)

def create_organization_and_admin(org_name: str, domain: str, deployment_mode: str, admin_email: str, admin_name: str, admin_pass: str):
    """Registers a new Enterprise client and their root Admin account."""
    db = SessionLocal()
    
    # Check if domain or org already exists
    if db.query(Organization).filter(Organization.email_domain == domain.lower()).first():
        db.close()
        return False, "This email domain is already registered to an organization."
        
    try:
        org_id = f"org_{uuid.uuid4().hex[:8]}"
        new_org = Organization(
            id=org_id, 
            name=org_name, 
            email_domain=domain.lower(), 
            deployment_mode=deployment_mode
        )
        db.add(new_org)
        
        new_admin = User(
            id=f"usr_{uuid.uuid4().hex[:12]}",
            email=admin_email.lower(),
            full_name=admin_name,
            password_hash=hash_password(admin_pass),
            role="admin",
            organization_id=org_id,
            subscription_tier="enterprise"
        )
        db.add(new_admin)
        db.commit()
        db.close()
        return True, "Organization and Admin created successfully!"
    except Exception as e:
        db.rollback()
        db.close()
        return False, str(e)

def authenticate_user(email: str, plain_password: str):
    """Verifies credentials and returns user details + role for UI routing."""
    db = SessionLocal()
    user = db.query(User).filter(User.email == email.lower()).first()
    
    if not user or not verify_password(plain_password, user.password_hash):
        db.close()
        return False, "Invalid email or password."
        
    org_name = user.organization.name if user.organization else "Public"
    user_data = {
        "id": user.id, 
        "full_name": user.full_name, 
        "email": user.email,
        "role": user.role,
        "org_id": user.organization_id,
        "org_name": org_name,
        "subscription_tier": user.subscription_tier
    }
    db.close()
    return True, user_data

# ==========================================
# USAGE LIMITS & SUBSCRIPTION LOGIC
# ==========================================

def enforce_query_limits(user_id: str) -> tuple[bool, str]:
    """Checks if a user is allowed to make a query today."""
    if user_id == "usr_public":
        return True, "Anonymous allowed"
        
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "User not found"
            
        # Unlimited tiers
        if user.subscription_tier in ["pro", "enterprise"]:
            return True, "Unlimited"
            
        # Free Tier Logic (Max 10 per day)
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        if user.last_query_date != today_str:
            # First query of a new day! Reset count.
            user.last_query_date = today_str
            user.daily_query_count = 1
        else:
            if user.daily_query_count >= 10:
                return False, "Daily limit reached. Upgrade to Pro to continue querying."
            user.daily_query_count += 1
            
        db.commit()
        return True, f"{10 - user.daily_query_count} queries remaining today."
    finally:
        db.close()

def upgrade_user_to_pro(user_id: str) -> bool:
    """Mock payment success handler to upgrade a public user."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.subscription_tier = "pro"
            db.commit()
            return True
        return False
    finally:
        db.close()

# ==========================================
# CHAT HISTORY LOGIC
# ==========================================

def create_chat_session(user_id: str, title: str, collection_name: str = None) -> str:
    """Creates a new chat thread for a user."""
    db = SessionLocal()
    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    new_session = ChatSession(
        id=session_id,
        user_id=user_id,
        session_title=title,
        collection_name=collection_name
    )
    db.add(new_session)
    db.commit()
    db.close()
    return session_id

def save_message(session_id: str, role: str, content: str):
    """Saves a single message (User or AI) to a chat session."""
    db = SessionLocal()
    msg_id = f"msg_{uuid.uuid4().hex[:12]}"
    new_message = Message(
        id=msg_id,
        session_id=session_id,
        role=role,
        content=content
    )
    db.add(new_message)
    db.commit()
    db.close()

def get_user_chat_sessions(user_id: str):
    """Retrieves all chat history threads for the sidebar."""
    db = SessionLocal()
    sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).order_by(ChatSession.created_at.desc()).all()
    
    results = [{"id": s.id, "title": s.session_title, "collection": s.collection_name, "date": s.created_at} for s in sessions]
    db.close()
    return results

def get_session_messages(session_id: str):
    """Retrieves the full back-and-forth conversation for a specific chat window."""
    db = SessionLocal()
    messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at.asc()).all()
    
    results = [{"role": m.role, "content": m.content, "time": m.created_at} for m in messages]
    db.close()
    return results

def delete_chat_session(session_id: str) -> bool:
    """Deletes a chat session and all its messages."""
    db = SessionLocal()
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            db.delete(session) # Cascade delete removes messages automatically
            db.commit()
            success = True
        else:
            success = False
    except Exception as e:
        db.rollback()
        print(f"Delete Error: {e}")
        success = False
    finally:
        db.close()
    return success

if __name__ == "__main__":
    print("Initializing Database Setup...")
    init_db()
    print("Testing functionality...")
    
    # 1. Test Admin & Organization Creation
    success, msg = create_organization_and_admin("Acme Corp", "acmecorp.com", "platform", "admin@acmecorp.com", "Sarah Chen", "securepassword123")
    print(f"Admin Test: {msg}")
    
    # 2. Test Standard Employee Auto-Routing (Matches acmecorp.com domain)
    success, user_data = register_smart_user("john@acmecorp.com", "John Doe", "password123")
    if success:
        print(f"User Test: Created {user_data['role']} account for John.")
        
    # 3. Test Chat Sessions & Messages
    print("\n--- Testing Chat History ---")
    session_id = create_chat_session(user_id=user_data["id"], title="Q3 Financials Discussion", collection_name="Acme_Fin_Docs")
    print(f"Created Chat Session: {session_id}")
    
    # Save a back-and-forth conversation
    save_message(session_id, role="user", content="What was our revenue in Q3?")
    save_message(session_id, role="ai", content="Based on the Acme Financials doc, Q3 revenue was $4.2M.")
    
    # Retrieve and print the conversation
    history = get_session_messages(session_id)
    for msg in history:
        print(f"[{msg['role'].upper()}]: {msg['content']}")
        
    print("\nAll Database systems (Orgs, Users, Sessions, Messages) are fully operational!")