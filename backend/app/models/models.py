
import enum
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Float,
    Enum,
    ForeignKey,
    Text,
    DECIMAL,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base

# Enums based on the Prisma schema

class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"
    VIEWER = "VIEWER"

class RunStatus(enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class StepStatus(enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class ApprovalType(enum.Enum):
    PROCUREMENT = "PROCUREMENT"
    RISK_THRESHOLD = "RISK_THRESHOLD"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    POLICY_EXCEPTION = "POLICY_EXCEPTION"

class ApprovalStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class RiskLevel(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ExceptionType(enum.Enum):
    DATA_VALIDATION = "DATA_VALIDATION"
    INTEGRATION_ERROR = "INTEGRATION_ERROR"
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"

class ExceptionStatus(enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"

class ResolutionType(enum.Enum):
    AUTO_REPAIR = "AUTO_REPAIR"
    MANUAL_FIX = "MANUAL_FIX"
    IGNORE = "IGNORE"
    ESCALATE = "ESCALATE"

class EventStatus(enum.Enum):
    RECEIVED = "RECEIVED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    IGNORED = "IGNORED"

# SQLAlchemy Models

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    approvals = relationship("Approval", back_populates="approver")
    runs = relationship("Run", back_populates="createdBy")

class Account(Base):
    __tablename__ = "accounts"
    id = Column(String, primary_key=True, index=True)
    hubspotId = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    domain = Column(String)
    industry = Column(String)
    employeeCount = Column(Integer)
    annualRevenue = Column(DECIMAL)
    lifecycleStage = Column(String)
    lastModifiedDate = Column(DateTime)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    properties = Column(JSONB)
    customFields = Column(JSONB)

    contacts = relationship("Contact", back_populates="account")
    deals = relationship("Deal", back_populates="account")
    runs = relationship("Run", back_populates="account")

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(String, primary_key=True, index=True)
    hubspotId = Column(String, unique=True, index=True)
    email = Column(String)
    firstName = Column(String)
    lastName = Column(String)
    jobTitle = Column(String)
    phone = Column(String)
    lifecycleStage = Column(String)
    lastModifiedDate = Column(DateTime)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    accountId = Column(String, ForeignKey("accounts.id"))
    account = relationship("Account", back_populates="contacts")
    
    deals = relationship("Deal", back_populates="contact")
    runs = relationship("Run", back_populates="contact")
    
    properties = Column(JSONB)
    customFields = Column(JSONB)

class Deal(Base):
    __tablename__ = "deals"
    id = Column(String, primary_key=True, index=True)
    hubspotId = Column(String, unique=True, index=True)
    name = Column(String)
    stage = Column(String)
    amount = Column(DECIMAL)
    closeDate = Column(DateTime)
    probability = Column(Float)
    lastModifiedDate = Column(DateTime)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    accountId = Column(String, ForeignKey("accounts.id"))
    account = relationship("Account", back_populates="deals")
    
    contactId = Column(String, ForeignKey("contacts.id"))
    contact = relationship("Contact", back_populates="deals")
    
    runs = relationship("Run", back_populates="deal")
    
    properties = Column(JSONB)
    customFields = Column(JSONB)

class Run(Base):
    __tablename__ = "runs"
    id = Column(String, primary_key=True, index=True)
    correlationId = Column(String, unique=True, index=True)
    workflowId = Column(String)
    status = Column(Enum(RunStatus), default=RunStatus.PENDING)
    startedAt = Column(DateTime, default=datetime.utcnow)
    completedAt = Column(DateTime)
    errorMessage = Column(Text)
    
    eventType = Column(String)
    objectType = Column(String)
    objectId = Column(String)
    
    createdById = Column(String, ForeignKey("users.id"))
    createdBy = relationship("User", back_populates="runs")
    
    accountId = Column(String, ForeignKey("accounts.id"))
    account = relationship("Account", back_populates="runs")
    
    contactId = Column(String, ForeignKey("contacts.id"))
    contact = relationship("Contact", back_populates="runs")
    
    dealId = Column(String, ForeignKey("deals.id"))
    deal = relationship("Deal", back_populates="runs")
    
    steps = relationship("RunStep", back_populates="run", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="run", cascade="all, delete-orphan")
    exceptions = relationship("Exception", back_populates="run", cascade="all, delete-orphan")
    
    payload = Column(JSONB)
    checkpointData = Column(JSONB)

class RunStep(Base):
    __tablename__ = "run_steps"
    id = Column(String, primary_key=True, index=True)
    runId = Column(String, ForeignKey("runs.id"), nullable=False)
    run = relationship("Run", back_populates="steps")
    
    stepName = Column(String)
    status = Column(Enum(StepStatus), default=StepStatus.PENDING)
    startedAt = Column(DateTime, default=datetime.utcnow)
    completedAt = Column(DateTime)
    errorMessage = Column(Text)
    retryCount = Column(Integer, default=0)
    
    input = Column(JSONB)
    output = Column(JSONB)

class Approval(Base):
    __tablename__ = "approvals"
    id = Column(String, primary_key=True, index=True)
    runId = Column(String, ForeignKey("runs.id"), nullable=False)
    run = relationship("Run", back_populates="approvals")
    
    type = Column(Enum(ApprovalType))
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    requestedAt = Column(DateTime, default=datetime.utcnow)
    respondedAt = Column(DateTime)
    
    title = Column(String)
    description = Column(Text)
    riskLevel = Column(Enum(RiskLevel), default=RiskLevel.LOW)
    
    policyId = Column(String)
    policySnapshot = Column(JSONB)
    
    approverId = Column(String, ForeignKey("users.id"))
    approver = relationship("User", back_populates="approvals")
    decision = Column(Boolean)
    justification = Column(Text)
    
    metadata = Column(JSONB)

class Exception(Base):
    __tablename__ = "exceptions"
    id = Column(String, primary_key=True, index=True)
    runId = Column(String, ForeignKey("runs.id"), nullable=False)
    run = relationship("Run", back_populates="exceptions")
    
    type = Column(Enum(ExceptionType))
    status = Column(Enum(ExceptionStatus), default=ExceptionStatus.OPEN)
    createdAt = Column(DateTime, default=datetime.utcnow)
    resolvedAt = Column(DateTime)
    
    title = Column(String)
    description = Column(Text)
    errorCode = Column(String)
    
    resolutionType = Column(Enum(ResolutionType))
    resolutionData = Column(JSONB)
    resolvedById = Column(String)
    
    metadata = Column(JSONB)

class Policy(Base):
    __tablename__ = "policies"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)
    version = Column(String, default="1.0")
    isActive = Column(Boolean, default=True)
    
    conditions = Column(JSONB)
    actions = Column(JSONB)
    
    validFrom = Column(DateTime, default=datetime.utcnow)
    validTo = Column(DateTime)
    
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    createdById = Column(String)

class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    id = Column(String, primary_key=True, index=True)
    hubspotEventId = Column(String, unique=True, index=True)
    eventType = Column(String)
    objectType = Column(String)
    objectId = Column(String)
    correlationId = Column(String)
    
    payload = Column(JSONB)
    signature = Column(String)
    
    status = Column(Enum(EventStatus), default=EventStatus.RECEIVED)
    processedAt = Column(DateTime)
    errorMessage = Column(Text)
    retryCount = Column(Integer, default=0)
    
    occurredAt = Column(DateTime)
    receivedAt = Column(DateTime, default=datetime.utcnow)
