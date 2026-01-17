"""
ProficientHub - ERM (Enterprise Resource Management) Models
Complete models for Employee, Department, Project, Time Tracking, Leave Management,
Asset Management, Budget/Expenses, and Performance Reviews.
Based on SQLAlchemy 2.0 with async support.
"""

from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum
from typing import List, Dict, Optional, Any
from uuid import uuid4

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date, Time, Text,
    ForeignKey, Numeric, JSON, Enum as SQLEnum, Index, CheckConstraint,
    UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


# =============================================================================
# ENUMS - Employee Management
# =============================================================================

class EmploymentType(str, Enum):
    """Types of employment"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERN = "intern"
    FREELANCE = "freelance"


class EmploymentStatus(str, Enum):
    """Employment status"""
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    PROBATION = "probation"
    NOTICE_PERIOD = "notice_period"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    RESIGNED = "resigned"
    RETIRED = "retired"


class Gender(str, Enum):
    """Gender options"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class PayFrequency(str, Enum):
    """Pay frequency options"""
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    SEMI_MONTHLY = "semi_monthly"
    MONTHLY = "monthly"
    ANNUALLY = "annually"


# =============================================================================
# ENUMS - Project Management
# =============================================================================

class ProjectStatus(str, Enum):
    """Project status"""
    PLANNING = "planning"
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"
    REVIEW = "review"


class ProjectPriority(str, Enum):
    """Project priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    """Task status"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class TaskPriority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# =============================================================================
# ENUMS - Leave Management
# =============================================================================

class LeaveType(str, Enum):
    """Types of leave"""
    ANNUAL = "annual"
    SICK = "sick"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    BEREAVEMENT = "bereavement"
    UNPAID = "unpaid"
    COMPENSATORY = "compensatory"
    STUDY = "study"
    SABBATICAL = "sabbatical"


class LeaveRequestStatus(str, Enum):
    """Leave request status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


# =============================================================================
# ENUMS - Asset Management
# =============================================================================

class AssetType(str, Enum):
    """Types of assets"""
    LAPTOP = "laptop"
    DESKTOP = "desktop"
    MONITOR = "monitor"
    PHONE = "phone"
    TABLET = "tablet"
    KEYBOARD = "keyboard"
    MOUSE = "mouse"
    HEADSET = "headset"
    CHAIR = "chair"
    DESK = "desk"
    OTHER = "other"


class AssetStatus(str, Enum):
    """Asset status"""
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    IN_MAINTENANCE = "in_maintenance"
    RETIRED = "retired"
    DISPOSED = "disposed"


# =============================================================================
# ENUMS - Expense Management
# =============================================================================

class ExpenseCategory(str, Enum):
    """Expense categories"""
    TRAVEL = "travel"
    ACCOMMODATION = "accommodation"
    MEALS = "meals"
    TRANSPORTATION = "transportation"
    OFFICE_SUPPLIES = "office_supplies"
    SOFTWARE = "software"
    HARDWARE = "hardware"
    TRAINING = "training"
    PROFESSIONAL_SERVICES = "professional_services"
    MARKETING = "marketing"
    UTILITIES = "utilities"
    RENT = "rent"
    OTHER = "other"


class ExpenseStatus(str, Enum):
    """Expense claim status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"


# =============================================================================
# ENUMS - Performance Management
# =============================================================================

class ReviewType(str, Enum):
    """Types of performance reviews"""
    ANNUAL = "annual"
    SEMI_ANNUAL = "semi_annual"
    QUARTERLY = "quarterly"
    PROBATION = "probation"
    PROJECT_BASED = "project_based"
    PROMOTION = "promotion"


class ReviewStatus(str, Enum):
    """Review status"""
    SCHEDULED = "scheduled"
    SELF_ASSESSMENT = "self_assessment"
    MANAGER_REVIEW = "manager_review"
    CALIBRATION = "calibration"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PerformanceRating(str, Enum):
    """Performance rating levels"""
    EXCEPTIONAL = "exceptional"
    EXCEEDS_EXPECTATIONS = "exceeds_expectations"
    MEETS_EXPECTATIONS = "meets_expectations"
    NEEDS_IMPROVEMENT = "needs_improvement"
    UNSATISFACTORY = "unsatisfactory"


# =============================================================================
# MODEL: Department
# =============================================================================

class Department(Base):
    """
    Department model with hierarchical structure support.
    """
    __tablename__ = "departments"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Academy Reference
    academy_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academies.id", ondelete="CASCADE"),
        nullable=False
    )

    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Hierarchy
    parent_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL")
    )

    # Department Head
    head_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL")
    )

    # Budget Information
    annual_budget: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    budget_year: Mapped[Optional[int]] = mapped_column(Integer)
    cost_center: Mapped[Optional[str]] = mapped_column(String(50))

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Contact Information
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    location: Mapped[Optional[str]] = mapped_column(String(255))

    # Custom Fields
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    created_by_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL")
    )

    # Soft Delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    employees = relationship("Employee", back_populates="department", foreign_keys="Employee.department_id")
    child_departments = relationship(
        "Department",
        backref=backref("parent", remote_side="Department.id"),
        foreign_keys=[parent_id]
    )
    teams = relationship("Team", back_populates="department")
    projects = relationship("Project", back_populates="department")
    budgets = relationship("DepartmentBudget", back_populates="department")

    # Indexes
    __table_args__ = (
        Index("idx_departments_academy_id", "academy_id"),
        Index("idx_departments_parent_id", "parent_id"),
        Index("idx_departments_code", "code"),
        Index("idx_departments_is_active", "is_active"),
        UniqueConstraint("academy_id", "code", name="uq_department_code"),
    )

    def __repr__(self) -> str:
        return f"<Department {self.name} ({self.code})>"

    @property
    def full_path(self) -> str:
        """Get full department path including parent departments"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name


# =============================================================================
# MODEL: Employee
# =============================================================================

class Employee(Base):
    """
    Employee model with comprehensive HR data, skills, and certifications.
    """
    __tablename__ = "employees"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Academy and User References
    academy_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academies.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL")
    )

    # Employee Identification
    employee_number: Mapped[str] = mapped_column(String(50), nullable=False)

    # Personal Information
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    preferred_name: Mapped[Optional[str]] = mapped_column(String(100))
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date)
    gender: Mapped[Optional[Gender]] = mapped_column(SQLEnum(Gender))
    nationality: Mapped[Optional[str]] = mapped_column(String(100))
    national_id: Mapped[Optional[str]] = mapped_column(String(100))
    passport_number: Mapped[Optional[str]] = mapped_column(String(100))
    marital_status: Mapped[Optional[str]] = mapped_column(String(50))

    # Contact Information
    personal_email: Mapped[Optional[str]] = mapped_column(String(255))
    work_email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    mobile: Mapped[Optional[str]] = mapped_column(String(50))

    # Address
    address_line1: Mapped[Optional[str]] = mapped_column(String(255))
    address_line2: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    country: Mapped[Optional[str]] = mapped_column(String(100))

    # Employment Details
    department_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL")
    )
    job_title: Mapped[str] = mapped_column(String(150), nullable=False)
    job_description: Mapped[Optional[str]] = mapped_column(Text)
    employment_type: Mapped[EmploymentType] = mapped_column(
        SQLEnum(EmploymentType),
        default=EmploymentType.FULL_TIME
    )
    employment_status: Mapped[EmploymentStatus] = mapped_column(
        SQLEnum(EmploymentStatus),
        default=EmploymentStatus.ACTIVE
    )

    # Manager
    manager_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL")
    )

    # Important Dates
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    probation_end_date: Mapped[Optional[date]] = mapped_column(Date)
    termination_date: Mapped[Optional[date]] = mapped_column(Date)
    termination_reason: Mapped[Optional[str]] = mapped_column(String(255))
    last_working_day: Mapped[Optional[date]] = mapped_column(Date)
    original_hire_date: Mapped[Optional[date]] = mapped_column(Date)  # For rehires

    # Compensation
    salary: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    pay_frequency: Mapped[PayFrequency] = mapped_column(
        SQLEnum(PayFrequency),
        default=PayFrequency.MONTHLY
    )
    bank_name: Mapped[Optional[str]] = mapped_column(String(255))
    bank_account_number: Mapped[Optional[str]] = mapped_column(String(100))  # Encrypted
    bank_routing_number: Mapped[Optional[str]] = mapped_column(String(100))  # Encrypted
    tax_id: Mapped[Optional[str]] = mapped_column(String(100))  # Encrypted

    # Leave Balances
    annual_leave_days: Mapped[int] = mapped_column(Integer, default=25)
    sick_leave_days: Mapped[int] = mapped_column(Integer, default=10)
    remaining_annual_leave: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("25"))
    remaining_sick_leave: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("10"))
    carried_over_leave: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))

    # Work Schedule
    work_hours_per_week: Mapped[Decimal] = mapped_column(Numeric(4, 1), default=Decimal("40"))
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    work_location: Mapped[Optional[str]] = mapped_column(String(255))
    remote_work_eligible: Mapped[bool] = mapped_column(Boolean, default=False)

    # Skills and Certifications
    skills: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    certifications: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)
    # Structure: [{"name": "...", "issuer": "...", "issue_date": "...", "expiry_date": "...", "credential_id": "..."}]
    languages: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)
    # Structure: [{"language": "English", "proficiency": "native"}]

    # Education
    education: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)
    # Structure: [{"institution": "...", "degree": "...", "field": "...", "graduation_year": 2020}]

    # Emergency Contact
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(255))
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(50))
    emergency_contact_relationship: Mapped[Optional[str]] = mapped_column(String(100))

    # Documents
    documents: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)
    # Structure: [{"name": "...", "type": "...", "url": "...", "uploaded_at": "..."}]

    # Profile
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Custom Fields
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    created_by_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL")
    )

    # Soft Delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    direct_reports = relationship(
        "Employee",
        backref=backref("manager", remote_side="Employee.id"),
        foreign_keys=[manager_id]
    )
    team_memberships = relationship("TeamMember", back_populates="employee")
    time_entries = relationship("TimeEntry", back_populates="employee")
    leave_requests = relationship("LeaveRequest", back_populates="employee")
    asset_assignments = relationship("AssetAssignment", back_populates="employee")
    expenses = relationship("Expense", back_populates="employee")
    performance_reviews = relationship("PerformanceReview", back_populates="employee", foreign_keys="PerformanceReview.employee_id")

    # Indexes
    __table_args__ = (
        Index("idx_employees_academy_id", "academy_id"),
        Index("idx_employees_department_id", "department_id"),
        Index("idx_employees_manager_id", "manager_id"),
        Index("idx_employees_employee_number", "employee_number"),
        Index("idx_employees_status", "employment_status"),
        Index("idx_employees_hire_date", "hire_date"),
        Index("idx_employees_work_email", "work_email"),
        UniqueConstraint("academy_id", "employee_number", name="uq_employee_number"),
        UniqueConstraint("academy_id", "work_email", name="uq_employee_work_email"),
    )

    def __repr__(self) -> str:
        return f"<Employee {self.first_name} {self.last_name} ({self.employee_number})>"

    @property
    def full_name(self) -> str:
        """Get full name"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    @property
    def display_name(self) -> str:
        """Get display name (preferred name if set)"""
        return self.preferred_name or self.full_name

    @property
    def tenure_years(self) -> float:
        """Calculate years of tenure"""
        end_date = self.termination_date or date.today()
        delta = end_date - self.hire_date
        return round(delta.days / 365.25, 1)

    @property
    def is_on_probation(self) -> bool:
        """Check if employee is still on probation"""
        if not self.probation_end_date:
            return False
        return date.today() < self.probation_end_date


# =============================================================================
# MODEL: Team
# =============================================================================

class Team(Base):
    """
    Team model for organizing employees within departments.
    """
    __tablename__ = "teams"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Academy and Department References
    academy_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academies.id", ondelete="CASCADE"),
        nullable=False
    )
    department_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL")
    )

    # Team Information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Team Lead
    lead_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL")
    )

    # Configuration
    max_members: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Custom Fields
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Soft Delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    department = relationship("Department", back_populates="teams")
    members = relationship("TeamMember", back_populates="team")

    # Indexes
    __table_args__ = (
        Index("idx_teams_academy_id", "academy_id"),
        Index("idx_teams_department_id", "department_id"),
        Index("idx_teams_lead_id", "lead_id"),
        Index("idx_teams_is_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Team {self.name}>"


class TeamMember(Base):
    """
    Team membership model.
    """
    __tablename__ = "team_members"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # References
    team_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False
    )
    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )

    # Membership Details
    role: Mapped[Optional[str]] = mapped_column(String(100))
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    left_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    team = relationship("Team", back_populates="members")
    employee = relationship("Employee", back_populates="team_memberships")

    # Indexes
    __table_args__ = (
        Index("idx_team_members_team_id", "team_id"),
        Index("idx_team_members_employee_id", "employee_id"),
        UniqueConstraint("team_id", "employee_id", name="uq_team_member"),
    )


# =============================================================================
# MODEL: Project
# =============================================================================

class Project(Base):
    """
    Project model with task tracking, milestones, and team allocation.
    """
    __tablename__ = "projects"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Academy and Department References
    academy_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academies.id", ondelete="CASCADE"),
        nullable=False
    )
    department_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL")
    )

    # Project Information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Status and Priority
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus),
        default=ProjectStatus.PLANNING
    )
    priority: Mapped[ProjectPriority] = mapped_column(
        SQLEnum(ProjectPriority),
        default=ProjectPriority.MEDIUM
    )
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)

    # Timeline
    planned_start_date: Mapped[Optional[date]] = mapped_column(Date)
    planned_end_date: Mapped[Optional[date]] = mapped_column(Date)
    actual_start_date: Mapped[Optional[date]] = mapped_column(Date)
    actual_end_date: Mapped[Optional[date]] = mapped_column(Date)

    # Project Manager
    project_manager_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL")
    )

    # Budget and Costs
    budget: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    actual_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")

    # Time Estimates
    estimated_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    actual_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))

    # Client Information (for client projects)
    client_name: Mapped[Optional[str]] = mapped_column(String(255))
    client_contact: Mapped[Optional[str]] = mapped_column(String(255))
    is_billable: Mapped[bool] = mapped_column(Boolean, default=False)
    hourly_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))

    # Organization
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)

    # Settings
    allow_overtime: Mapped[bool] = mapped_column(Boolean, default=True)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    created_by_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL")
    )

    # Soft Delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    department = relationship("Department", back_populates="projects")
    tasks = relationship("ProjectTask", back_populates="project", cascade="all, delete-orphan")
    milestones = relationship("ProjectMilestone", back_populates="project", cascade="all, delete-orphan")
    team_allocations = relationship("ProjectTeamAllocation", back_populates="project", cascade="all, delete-orphan")
    time_entries = relationship("TimeEntry", back_populates="project")

    # Indexes
    __table_args__ = (
        Index("idx_projects_academy_id", "academy_id"),
        Index("idx_projects_department_id", "department_id"),
        Index("idx_projects_status", "status"),
        Index("idx_projects_priority", "priority"),
        Index("idx_projects_code", "code"),
        Index("idx_projects_project_manager", "project_manager_id"),
        UniqueConstraint("academy_id", "code", name="uq_project_code"),
        CheckConstraint("progress_percent >= 0 AND progress_percent <= 100", name="ck_project_progress"),
    )

    def __repr__(self) -> str:
        return f"<Project {self.name} ({self.code})>"

    @property
    def is_overdue(self) -> bool:
        """Check if project is overdue"""
        if not self.planned_end_date or self.status == ProjectStatus.COMPLETED:
            return False
        return date.today() > self.planned_end_date

    @property
    def budget_variance(self) -> Optional[Decimal]:
        """Calculate budget variance"""
        if self.budget and self.actual_cost:
            return self.budget - self.actual_cost
        return None

    @property
    def budget_utilization(self) -> Optional[float]:
        """Calculate budget utilization percentage"""
        if self.budget and self.budget > 0 and self.actual_cost:
            return float(self.actual_cost / self.budget * 100)
        return None


# =============================================================================
# MODEL: ProjectMilestone
# =============================================================================

class ProjectMilestone(Base):
    """
    Project milestone model for tracking major project phases.
    """
    __tablename__ = "project_milestones"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Project Reference
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )

    # Milestone Information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0)

    # Timeline
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    completed_date: Mapped[Optional[date]] = mapped_column(Date)

    # Status
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Deliverables
    deliverables: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    project = relationship("Project", back_populates="milestones")
    tasks = relationship("ProjectTask", back_populates="milestone")

    # Indexes
    __table_args__ = (
        Index("idx_milestones_project_id", "project_id"),
        Index("idx_milestones_target_date", "target_date"),
        Index("idx_milestones_is_completed", "is_completed"),
    )


# =============================================================================
# MODEL: ProjectTask
# =============================================================================

class ProjectTask(Base):
    """
    Project task model with subtask support and time tracking.
    """
    __tablename__ = "project_tasks"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Project and Milestone References
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    milestone_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project_milestones.id", ondelete="SET NULL")
    )

    # Parent Task (for subtasks)
    parent_task_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project_tasks.id", ondelete="CASCADE")
    )

    # Task Information
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    task_number: Mapped[Optional[str]] = mapped_column(String(50))

    # Status and Priority
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus),
        default=TaskStatus.TODO
    )
    priority: Mapped[TaskPriority] = mapped_column(
        SQLEnum(TaskPriority),
        default=TaskPriority.MEDIUM
    )

    # Assignment
    assignee_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL")
    )
    reporter_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL")
    )

    # Timeline
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Time Estimates
    estimated_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2))
    actual_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2))

    # Dependencies
    blocked_by: Mapped[Optional[List[str]]] = mapped_column(ARRAY(UUID))

    # Organization
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    labels: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    # Checklist
    checklist: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)
    # Structure: [{"item": "...", "completed": false}]

    # Attachments
    attachments: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)

    # Custom Fields
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    created_by_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL")
    )

    # Soft Delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    milestone = relationship("ProjectMilestone", back_populates="tasks")
    subtasks = relationship(
        "ProjectTask",
        backref=backref("parent_task", remote_side="ProjectTask.id"),
        foreign_keys=[parent_task_id]
    )
    time_entries = relationship("TimeEntry", back_populates="task")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_tasks_project_id", "project_id"),
        Index("idx_tasks_milestone_id", "milestone_id"),
        Index("idx_tasks_parent_id", "parent_task_id"),
        Index("idx_tasks_status", "status"),
        Index("idx_tasks_assignee_id", "assignee_id"),
        Index("idx_tasks_due_date", "due_date"),
    )

    def __repr__(self) -> str:
        return f"<ProjectTask {self.title[:30]}>"

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if not self.due_date or self.status == TaskStatus.DONE:
            return False
        return datetime.utcnow() > self.due_date.replace(tzinfo=None)

    @property
    def checklist_progress(self) -> float:
        """Calculate checklist completion percentage"""
        if not self.checklist:
            return 0.0
        completed = sum(1 for item in self.checklist if item.get("completed", False))
        return (completed / len(self.checklist)) * 100


class TaskComment(Base):
    """
    Task comment model.
    """
    __tablename__ = "task_comments"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # References
    task_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project_tasks.id", ondelete="CASCADE"),
        nullable=False
    )
    author_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )

    # Comment Content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    attachments: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)

    # Edit History
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    edited_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Soft Delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    task = relationship("ProjectTask", back_populates="comments")

    # Indexes
    __table_args__ = (
        Index("idx_comments_task_id", "task_id"),
        Index("idx_comments_author_id", "author_id"),
    )


# =============================================================================
# MODEL: ProjectTeamAllocation
# =============================================================================

class ProjectTeamAllocation(Base):
    """
    Project team allocation model for tracking employee assignments.
    """
    __tablename__ = "project_team_allocations"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # References
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )

    # Allocation Details
    role: Mapped[Optional[str]] = mapped_column(String(150))
    allocation_percent: Mapped[int] = mapped_column(Integer, default=100)  # 0-100
    billable_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))

    # Timeline
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    project = relationship("Project", back_populates="team_allocations")

    # Indexes
    __table_args__ = (
        Index("idx_allocation_project_id", "project_id"),
        Index("idx_allocation_employee_id", "employee_id"),
        Index("idx_allocation_is_active", "is_active"),
        CheckConstraint("allocation_percent >= 0 AND allocation_percent <= 100", name="ck_allocation_percent"),
    )


# =============================================================================
# MODEL: TimeEntry
# =============================================================================

class TimeEntry(Base):
    """
    Time entry model with billing support.
    """
    __tablename__ = "time_entries"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Academy Reference
    academy_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academies.id", ondelete="CASCADE"),
        nullable=False
    )

    # Employee Reference
    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )

    # Project and Task References
    project_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL")
    )
    task_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project_tasks.id", ondelete="SET NULL")
    )

    # Time Details
    date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[Optional[time]] = mapped_column(Time)
    end_time: Mapped[Optional[time]] = mapped_column(Time)
    duration_hours: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)

    # Description
    description: Mapped[Optional[str]] = mapped_column(Text)
    activity_type: Mapped[Optional[str]] = mapped_column(String(100))

    # Billing
    is_billable: Mapped[bool] = mapped_column(Boolean, default=True)
    billing_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    billed_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    is_invoiced: Mapped[bool] = mapped_column(Boolean, default=False)
    invoice_id: Mapped[Optional[str]] = mapped_column(String(100))

    # Approval
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL")
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Timer
    is_running: Mapped[bool] = mapped_column(Boolean, default=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    employee = relationship("Employee", back_populates="time_entries", foreign_keys=[employee_id])
    project = relationship("Project", back_populates="time_entries")
    task = relationship("ProjectTask", back_populates="time_entries")

    # Indexes
    __table_args__ = (
        Index("idx_time_entries_academy_id", "academy_id"),
        Index("idx_time_entries_employee_id", "employee_id"),
        Index("idx_time_entries_project_id", "project_id"),
        Index("idx_time_entries_task_id", "task_id"),
        Index("idx_time_entries_date", "date"),
        Index("idx_time_entries_is_approved", "is_approved"),
        Index("idx_time_entries_is_billable", "is_billable"),
    )

    def __repr__(self) -> str:
        return f"<TimeEntry {self.date} ({self.duration_hours}h)>"


# =============================================================================
# MODEL: LeaveRequest
# =============================================================================

class LeaveRequest(Base):
    """
    Leave request model with approval workflow.
    """
    __tablename__ = "leave_requests"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Academy and Employee References
    academy_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academies.id", ondelete="CASCADE"),
        nullable=False
    )
    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )

    # Leave Details
    leave_type: Mapped[LeaveType] = mapped_column(
        SQLEnum(LeaveType),
        nullable=False
    )
    status: Mapped[LeaveRequestStatus] = mapped_column(
        SQLEnum(LeaveRequestStatus),
        default=LeaveRequestStatus.PENDING
    )

    # Dates
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_days: Mapped[Decimal] = mapped_column(Numeric(4, 1), nullable=False)

    # Half Day Options
    is_half_day_start: Mapped[bool] = mapped_column(Boolean, default=False)
    is_half_day_end: Mapped[bool] = mapped_column(Boolean, default=False)

    # Reason and Documents
    reason: Mapped[Optional[str]] = mapped_column(Text)
    supporting_documents: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)

    # Approval
    approved_by_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL")
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    rejected_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Coverage
    coverage_employee_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL")
    )
    handover_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    employee = relationship("Employee", back_populates="leave_requests", foreign_keys=[employee_id])

    # Indexes
    __table_args__ = (
        Index("idx_leave_requests_academy_id", "academy_id"),
        Index("idx_leave_requests_employee_id", "employee_id"),
        Index("idx_leave_requests_status", "status"),
        Index("idx_leave_requests_leave_type", "leave_type"),
        Index("idx_leave_requests_start_date", "start_date"),
        Index("idx_leave_requests_end_date", "end_date"),
    )

    def __repr__(self) -> str:
        return f"<LeaveRequest {self.leave_type.value} ({self.start_date} - {self.end_date})>"


# =============================================================================
# MODEL: Asset
# =============================================================================

class Asset(Base):
    """
    Asset model for equipment tracking.
    """
    __tablename__ = "assets"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Academy Reference
    academy_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academies.id", ondelete="CASCADE"),
        nullable=False
    )

    # Asset Identification
    asset_tag: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Classification
    asset_type: Mapped[AssetType] = mapped_column(
        SQLEnum(AssetType),
        nullable=False
    )
    status: Mapped[AssetStatus] = mapped_column(
        SQLEnum(AssetStatus),
        default=AssetStatus.AVAILABLE
    )

    # Product Details
    serial_number: Mapped[Optional[str]] = mapped_column(String(100))
    model: Mapped[Optional[str]] = mapped_column(String(255))
    manufacturer: Mapped[Optional[str]] = mapped_column(String(255))
    specifications: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)

    # Purchase Information
    purchase_date: Mapped[Optional[date]] = mapped_column(Date)
    purchase_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    current_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    vendor: Mapped[Optional[str]] = mapped_column(String(255))
    purchase_order_number: Mapped[Optional[str]] = mapped_column(String(100))

    # Warranty
    warranty_expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    warranty_details: Mapped[Optional[str]] = mapped_column(Text)

    # Location
    location: Mapped[Optional[str]] = mapped_column(String(255))
    department_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL")
    )

    # Software License (for software assets)
    license_key: Mapped[Optional[str]] = mapped_column(String(255))
    license_seats: Mapped[Optional[int]] = mapped_column(Integer)
    license_expiry_date: Mapped[Optional[date]] = mapped_column(Date)

    # Documents and Images
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    documents: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)

    # Depreciation
    depreciation_method: Mapped[Optional[str]] = mapped_column(String(50))
    useful_life_years: Mapped[Optional[int]] = mapped_column(Integer)
    salvage_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))

    # Custom Fields
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    created_by_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL")
    )

    # Soft Delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    assignments = relationship("AssetAssignment", back_populates="asset", cascade="all, delete-orphan")
    maintenance_logs = relationship("AssetMaintenanceLog", back_populates="asset", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_assets_academy_id", "academy_id"),
        Index("idx_assets_asset_tag", "asset_tag"),
        Index("idx_assets_asset_type", "asset_type"),
        Index("idx_assets_status", "status"),
        Index("idx_assets_serial_number", "serial_number"),
        UniqueConstraint("academy_id", "asset_tag", name="uq_asset_tag"),
    )

    def __repr__(self) -> str:
        return f"<Asset {self.name} ({self.asset_tag})>"

    @property
    def is_warranty_active(self) -> bool:
        """Check if warranty is still active"""
        if not self.warranty_expiry_date:
            return False
        return date.today() <= self.warranty_expiry_date


class AssetAssignment(Base):
    """
    Asset assignment model for tracking who has which assets.
    """
    __tablename__ = "asset_assignments"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # References
    asset_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False
    )
    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )

    # Assignment Details
    assigned_date: Mapped[date] = mapped_column(Date, nullable=False)
    returned_date: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Condition
    condition_at_assignment: Mapped[Optional[str]] = mapped_column(String(50))
    condition_at_return: Mapped[Optional[str]] = mapped_column(String(50))

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Assigned By
    assigned_by_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL")
    )

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    asset = relationship("Asset", back_populates="assignments")
    employee = relationship("Employee", back_populates="asset_assignments", foreign_keys=[employee_id])

    # Indexes
    __table_args__ = (
        Index("idx_asset_assignments_asset_id", "asset_id"),
        Index("idx_asset_assignments_employee_id", "employee_id"),
        Index("idx_asset_assignments_is_active", "is_active"),
    )


class AssetMaintenanceLog(Base):
    """
    Asset maintenance log for tracking repairs and maintenance.
    """
    __tablename__ = "asset_maintenance_logs"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Asset Reference
    asset_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False
    )

    # Maintenance Details
    maintenance_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Timeline
    scheduled_date: Mapped[Optional[date]] = mapped_column(Date)
    completed_date: Mapped[Optional[date]] = mapped_column(Date)

    # Cost
    cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")

    # Vendor
    vendor: Mapped[Optional[str]] = mapped_column(String(255))
    invoice_number: Mapped[Optional[str]] = mapped_column(String(100))

    # Status
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    created_by_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL")
    )

    # Relationships
    asset = relationship("Asset", back_populates="maintenance_logs")

    # Indexes
    __table_args__ = (
        Index("idx_maintenance_logs_asset_id", "asset_id"),
        Index("idx_maintenance_logs_scheduled_date", "scheduled_date"),
        Index("idx_maintenance_logs_is_completed", "is_completed"),
    )


# =============================================================================
# MODEL: DepartmentBudget
# =============================================================================

class DepartmentBudget(Base):
    """
    Department budget model for financial planning.
    """
    __tablename__ = "department_budgets"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Department Reference
    department_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=False
    )

    # Budget Period
    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False)
    fiscal_quarter: Mapped[Optional[int]] = mapped_column(Integer)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)

    # Budget Amounts
    total_budget: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    allocated_budget: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    spent_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    committed_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")

    # Budget Categories
    category_budgets: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)
    # Structure: {"travel": 10000, "training": 5000, "equipment": 20000}

    # Status
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL")
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    created_by_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL")
    )

    # Relationships
    department = relationship("Department", back_populates="budgets")
    expenses = relationship("Expense", back_populates="budget")

    # Indexes
    __table_args__ = (
        Index("idx_budgets_department_id", "department_id"),
        Index("idx_budgets_fiscal_year", "fiscal_year"),
        Index("idx_budgets_period", "period_start", "period_end"),
        UniqueConstraint("department_id", "fiscal_year", "fiscal_quarter", name="uq_budget_period"),
    )

    def __repr__(self) -> str:
        return f"<DepartmentBudget {self.fiscal_year} Q{self.fiscal_quarter or 'Full'}>"

    @property
    def remaining_budget(self) -> Decimal:
        """Calculate remaining budget"""
        return self.total_budget - self.spent_amount - self.committed_amount

    @property
    def utilization_percent(self) -> float:
        """Calculate budget utilization percentage"""
        if self.total_budget == 0:
            return 0.0
        return float(self.spent_amount / self.total_budget * 100)


# =============================================================================
# MODEL: Expense
# =============================================================================

class Expense(Base):
    """
    Expense claim model with approval workflow.
    """
    __tablename__ = "expenses"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Academy and Employee References
    academy_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academies.id", ondelete="CASCADE"),
        nullable=False
    )
    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )

    # Budget Reference (optional)
    budget_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("department_budgets.id", ondelete="SET NULL")
    )

    # Project Reference (optional)
    project_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL")
    )

    # Expense Identification
    expense_number: Mapped[str] = mapped_column(String(50), nullable=False)

    # Expense Details
    category: Mapped[ExpenseCategory] = mapped_column(
        SQLEnum(ExpenseCategory),
        nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Amount
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    exchange_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))
    amount_in_base_currency: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))

    # Dates
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    submitted_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Receipts
    receipts: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)
    # Structure: [{"name": "...", "url": "...", "uploaded_at": "..."}]

    # Vendor Information
    vendor_name: Mapped[Optional[str]] = mapped_column(String(255))
    invoice_number: Mapped[Optional[str]] = mapped_column(String(100))

    # Status
    status: Mapped[ExpenseStatus] = mapped_column(
        SQLEnum(ExpenseStatus),
        default=ExpenseStatus.DRAFT
    )

    # Approval
    approved_by_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL")
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Payment
    payment_method: Mapped[Optional[str]] = mapped_column(String(50))
    payment_reference: Mapped[Optional[str]] = mapped_column(String(100))
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Tax
    tax_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    is_tax_deductible: Mapped[bool] = mapped_column(Boolean, default=True)

    # Custom Fields
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    employee = relationship("Employee", back_populates="expenses", foreign_keys=[employee_id])
    budget = relationship("DepartmentBudget", back_populates="expenses")

    # Indexes
    __table_args__ = (
        Index("idx_expenses_academy_id", "academy_id"),
        Index("idx_expenses_employee_id", "employee_id"),
        Index("idx_expenses_budget_id", "budget_id"),
        Index("idx_expenses_project_id", "project_id"),
        Index("idx_expenses_status", "status"),
        Index("idx_expenses_category", "category"),
        Index("idx_expenses_expense_date", "expense_date"),
        UniqueConstraint("academy_id", "expense_number", name="uq_expense_number"),
    )

    def __repr__(self) -> str:
        return f"<Expense {self.expense_number} ({self.amount} {self.currency})>"


# =============================================================================
# MODEL: PerformanceReview
# =============================================================================

class PerformanceReview(Base):
    """
    Performance review model with goals, ratings, and compensation recommendations.
    """
    __tablename__ = "performance_reviews"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Academy and Employee References
    academy_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academies.id", ondelete="CASCADE"),
        nullable=False
    )
    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )
    reviewer_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )

    # Review Period
    review_period_start: Mapped[date] = mapped_column(Date, nullable=False)
    review_period_end: Mapped[date] = mapped_column(Date, nullable=False)

    # Review Type and Status
    review_type: Mapped[ReviewType] = mapped_column(
        SQLEnum(ReviewType),
        default=ReviewType.ANNUAL
    )
    status: Mapped[ReviewStatus] = mapped_column(
        SQLEnum(ReviewStatus),
        default=ReviewStatus.SCHEDULED
    )

    # Overall Rating
    overall_rating: Mapped[Optional[PerformanceRating]] = mapped_column(
        SQLEnum(PerformanceRating)
    )
    rating_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2))  # 1.00 - 5.00

    # Category Ratings
    category_ratings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)
    # Structure: {"quality_of_work": 4, "productivity": 3.5, "teamwork": 4.5, "communication": 4}

    # Goals
    goals_achieved: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)
    # Structure: [{"goal": "...", "achievement_level": "exceeded", "comments": "..."}]

    goals_for_next_period: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)
    # Structure: [{"goal": "...", "target_date": "...", "priority": "high"}]

    # Feedback
    strengths: Mapped[Optional[str]] = mapped_column(Text)
    areas_for_improvement: Mapped[Optional[str]] = mapped_column(Text)
    reviewer_comments: Mapped[Optional[str]] = mapped_column(Text)

    # Self Assessment
    self_assessment: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)
    # Structure: {"strengths": "...", "improvements": "...", "goals_feedback": "..."}
    self_rating: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2))

    # Employee Feedback
    employee_comments: Mapped[Optional[str]] = mapped_column(Text)
    employee_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    employee_acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Compensation Recommendations
    salary_adjustment_percent: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    bonus_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    bonus_currency: Mapped[str] = mapped_column(String(3), default="EUR")
    promotion_recommended: Mapped[bool] = mapped_column(Boolean, default=False)
    promotion_to_title: Mapped[Optional[str]] = mapped_column(String(150))

    # Development Plan
    training_recommendations: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    career_discussion_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Meeting
    scheduled_meeting_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    meeting_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    meeting_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Calibration (for HR)
    calibration_notes: Mapped[Optional[str]] = mapped_column(Text)
    calibrated_by_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL")
    )
    calibrated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Custom Fields
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    employee = relationship("Employee", back_populates="performance_reviews", foreign_keys=[employee_id])

    # Indexes
    __table_args__ = (
        Index("idx_reviews_academy_id", "academy_id"),
        Index("idx_reviews_employee_id", "employee_id"),
        Index("idx_reviews_reviewer_id", "reviewer_id"),
        Index("idx_reviews_status", "status"),
        Index("idx_reviews_review_type", "review_type"),
        Index("idx_reviews_period", "review_period_start", "review_period_end"),
    )

    def __repr__(self) -> str:
        return f"<PerformanceReview {self.review_type.value} ({self.review_period_start} - {self.review_period_end})>"


# =============================================================================
# HELPER MODELS
# =============================================================================

class Holiday(Base):
    """
    Company holiday calendar.
    """
    __tablename__ = "holidays"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Academy Reference
    academy_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academies.id", ondelete="CASCADE"),
        nullable=False
    )

    # Holiday Details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=True)

    # Applicability
    applies_to_all: Mapped[bool] = mapped_column(Boolean, default=True)
    department_ids: Mapped[Optional[List[str]]] = mapped_column(ARRAY(UUID))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    country: Mapped[Optional[str]] = mapped_column(String(100))

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Indexes
    __table_args__ = (
        Index("idx_holidays_academy_id", "academy_id"),
        Index("idx_holidays_date", "date"),
    )


class Announcement(Base):
    """
    Company-wide announcements.
    """
    __tablename__ = "announcements"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Academy Reference
    academy_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academies.id", ondelete="CASCADE"),
        nullable=False
    )

    # Announcement Details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    announcement_type: Mapped[str] = mapped_column(String(50), default="general")

    # Visibility
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    publish_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Target Audience
    target_all: Mapped[bool] = mapped_column(Boolean, default=True)
    target_department_ids: Mapped[Optional[List[str]]] = mapped_column(ARRAY(UUID))

    # Priority
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    priority: Mapped[int] = mapped_column(Integer, default=0)

    # Author
    author_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False
    )

    # Attachments
    attachments: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)

    # Audit Fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Soft Delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Indexes
    __table_args__ = (
        Index("idx_announcements_academy_id", "academy_id"),
        Index("idx_announcements_is_published", "is_published"),
        Index("idx_announcements_publish_date", "publish_date"),
    )
