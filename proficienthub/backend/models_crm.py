"""
ProficientHub - CRM Models
Complete CRM data models for lead, contact, deal, communication, task, campaign, and workflow management
Based on SQLAlchemy 2.0 with async support
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import List, Dict, Optional, Any
from uuid import uuid4

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date, Text,
    ForeignKey, Numeric, JSON, Enum as SQLEnum, Index, CheckConstraint,
    UniqueConstraint, Table
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


# =============================================================================
# ENUMS - Lead Management
# =============================================================================

class LeadSource(str, Enum):
    """Sources where leads can originate from"""
    WEBSITE = "website"
    REFERRAL = "referral"
    GOOGLE_ADS = "google_ads"
    FACEBOOK_ADS = "facebook_ads"
    LINKEDIN_ADS = "linkedin_ads"
    COLD_OUTREACH = "cold_outreach"
    TRADE_SHOW = "trade_show"
    WEBINAR = "webinar"
    CONTENT_DOWNLOAD = "content_download"
    EMAIL_CAMPAIGN = "email_campaign"
    PARTNER = "partner"
    ORGANIC_SEARCH = "organic_search"
    SOCIAL_MEDIA = "social_media"
    PHONE_INQUIRY = "phone_inquiry"
    OTHER = "other"


class LeadStatus(str, Enum):
    """Status stages for lead lifecycle"""
    NEW = "new"
    CONTACTED = "contacted"
    ENGAGED = "engaged"
    QUALIFIED = "qualified"
    DEMO_SCHEDULED = "demo_scheduled"
    DEMO_COMPLETED = "demo_completed"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATION = "negotiation"
    CONVERTED = "converted"
    LOST = "lost"


class LeadOrganizationType(str, Enum):
    """Types of organizations that can be leads"""
    LANGUAGE_SCHOOL = "language_school"
    UNIVERSITY = "university"
    HIGH_SCHOOL = "high_school"
    CORPORATE = "corporate"
    GOVERNMENT = "government"
    NONPROFIT = "nonprofit"
    INDIVIDUAL_TEACHER = "individual_teacher"
    TEST_PREP_CENTER = "test_prep_center"
    ONLINE_PLATFORM = "online_platform"
    OTHER = "other"


class IndustryType(str, Enum):
    """Industry classifications for organizations"""
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    GOVERNMENT = "government"
    HOSPITALITY = "hospitality"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    PROFESSIONAL_SERVICES = "professional_services"
    OTHER = "other"


# =============================================================================
# ENUMS - Contact Management
# =============================================================================

class ContactType(str, Enum):
    """Types of contacts within an organization"""
    DECISION_MAKER = "decision_maker"
    INFLUENCER = "influencer"
    CHAMPION = "champion"
    END_USER = "end_user"
    TECHNICAL = "technical"
    BILLING = "billing"
    OTHER = "other"


class ContactMethod(str, Enum):
    """Preferred contact methods"""
    EMAIL = "email"
    PHONE = "phone"
    WHATSAPP = "whatsapp"
    SMS = "sms"
    VIDEO_CALL = "video_call"
    IN_PERSON = "in_person"


# =============================================================================
# ENUMS - Deal Management
# =============================================================================

class DealStage(str, Enum):
    """Pipeline stages for deals"""
    QUALIFICATION = "qualification"
    NEEDS_ANALYSIS = "needs_analysis"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    ON_HOLD = "on_hold"
    RENEWAL = "renewal"


class DealPriority(str, Enum):
    """Priority levels for deals"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# =============================================================================
# ENUMS - Communication Management
# =============================================================================

class CommunicationType(str, Enum):
    """Types of communication interactions"""
    EMAIL = "email"
    CALL = "call"
    VIDEO_CALL = "video_call"
    MEETING = "meeting"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    LINKEDIN_MESSAGE = "linkedin_message"
    LIVE_CHAT = "live_chat"
    NOTE = "note"
    TASK = "task"


class CommunicationDirection(str, Enum):
    """Direction of communication"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    INTERNAL = "internal"


class CommunicationOutcome(str, Enum):
    """Outcomes for calls and meetings"""
    CONNECTED = "connected"
    VOICEMAIL = "voicemail"
    NO_ANSWER = "no_answer"
    BUSY = "busy"
    WRONG_NUMBER = "wrong_number"
    MEETING_HELD = "meeting_held"
    MEETING_CANCELLED = "meeting_cancelled"
    MEETING_RESCHEDULED = "meeting_rescheduled"


class SentimentLabel(str, Enum):
    """AI-analyzed sentiment classifications"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


# =============================================================================
# ENUMS - Task Management
# =============================================================================

class TaskType(str, Enum):
    """Types of CRM tasks"""
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    FOLLOW_UP = "follow_up"
    DEMO = "demo"
    PROPOSAL = "proposal"
    CONTRACT = "contract"
    ONBOARDING = "onboarding"
    RESEARCH = "research"
    OTHER = "other"


class TaskPriority(str, Enum):
    """Priority levels for tasks"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    """Status of tasks"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DEFERRED = "deferred"


class RecurrencePattern(str, Enum):
    """Patterns for recurring tasks"""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


# =============================================================================
# ENUMS - Campaign Management
# =============================================================================

class CampaignType(str, Enum):
    """Types of marketing campaigns"""
    EMAIL_DRIP = "email_drip"
    EMAIL_BLAST = "email_blast"
    WEBINAR = "webinar"
    CONTENT_MARKETING = "content_marketing"
    SOCIAL_MEDIA = "social_media"
    PAID_ADS = "paid_ads"
    REFERRAL_PROGRAM = "referral_program"
    TRADE_SHOW = "trade_show"
    PARTNERSHIP = "partnership"
    RETARGETING = "retargeting"
    PRODUCT_LAUNCH = "product_launch"


class CampaignStatus(str, Enum):
    """Status of campaigns"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# =============================================================================
# ENUMS - Workflow Automation
# =============================================================================

class WorkflowTrigger(str, Enum):
    """Events that can trigger workflow automation"""
    LEAD_CREATED = "lead_created"
    LEAD_STATUS_CHANGED = "lead_status_changed"
    LEAD_SCORE_THRESHOLD = "lead_score_threshold"
    DEAL_CREATED = "deal_created"
    DEAL_STAGE_CHANGED = "deal_stage_changed"
    DEAL_WON = "deal_won"
    DEAL_LOST = "deal_lost"
    TASK_DUE = "task_due"
    TASK_OVERDUE = "task_overdue"
    NO_ACTIVITY_DAYS = "no_activity_days"
    EMAIL_OPENED = "email_opened"
    EMAIL_CLICKED = "email_clicked"


class WorkflowActionType(str, Enum):
    """Types of actions that workflows can perform"""
    SEND_EMAIL = "send_email"
    CREATE_TASK = "create_task"
    UPDATE_LEAD_STATUS = "update_lead_status"
    UPDATE_DEAL_STAGE = "update_deal_stage"
    ASSIGN_OWNER = "assign_owner"
    ADD_TAG = "add_tag"
    REMOVE_TAG = "remove_tag"
    SEND_NOTIFICATION = "send_notification"
    SEND_SLACK_MESSAGE = "send_slack_message"
    WEBHOOK = "webhook"
    DELAY = "delay"


# =============================================================================
# ENUMS - External CRM Integration
# =============================================================================

class ExternalCRMType(str, Enum):
    """Supported external CRM systems"""
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    ZOHO = "zoho"
    PIPEDRIVE = "pipedrive"
    FRESHSALES = "freshsales"
    DYNAMICS365 = "dynamics365"
    COPPER = "copper"
    INSIGHTLY = "insightly"
    CUSTOM_WEBHOOK = "custom_webhook"


class SyncDirection(str, Enum):
    """Direction of data synchronization"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(str, Enum):
    """Status of synchronization operations"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"


# =============================================================================
# MODEL: CRMLead - Lead/Prospect Management with Scoring
# =============================================================================

class CRMLead(Base):
    """
    Lead/prospect management model with comprehensive scoring system.
    Tracks potential customers from first contact to conversion.
    """
    __tablename__ = "crm_leads"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Organization Information
    organization_name: Mapped[str] = mapped_column(String(255), nullable=False)
    organization_type: Mapped[LeadOrganizationType] = mapped_column(
        SQLEnum(LeadOrganizationType),
        default=LeadOrganizationType.LANGUAGE_SCHOOL
    )
    website: Mapped[Optional[str]] = mapped_column(String(500))
    industry: Mapped[Optional[IndustryType]] = mapped_column(SQLEnum(IndustryType))
    employee_count: Mapped[Optional[int]] = mapped_column(Integer)
    annual_revenue: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))

    # Primary Contact Information
    contact_first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50))
    contact_title: Mapped[Optional[str]] = mapped_column(String(150))

    # Source Tracking
    source: Mapped[LeadSource] = mapped_column(
        SQLEnum(LeadSource),
        default=LeadSource.WEBSITE
    )
    source_details: Mapped[Optional[str]] = mapped_column(Text)
    source_campaign_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_campaigns.id", ondelete="SET NULL")
    )
    utm_source: Mapped[Optional[str]] = mapped_column(String(100))
    utm_medium: Mapped[Optional[str]] = mapped_column(String(100))
    utm_campaign: Mapped[Optional[str]] = mapped_column(String(100))
    utm_content: Mapped[Optional[str]] = mapped_column(String(100))
    referrer_url: Mapped[Optional[str]] = mapped_column(String(1000))

    # Status and Qualification
    status: Mapped[LeadStatus] = mapped_column(
        SQLEnum(LeadStatus),
        default=LeadStatus.NEW
    )
    lead_score: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    is_qualified: Mapped[bool] = mapped_column(Boolean, default=False)
    qualification_notes: Mapped[Optional[str]] = mapped_column(Text)
    qualification_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Business Interest
    interested_exams: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    estimated_students: Mapped[Optional[int]] = mapped_column(Integer)
    estimated_deal_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    budget_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    timeline_urgency: Mapped[Optional[str]] = mapped_column(String(50))
    decision_timeline: Mapped[Optional[str]] = mapped_column(String(100))

    # Assignment
    assigned_to_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL")
    )
    team_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="SET NULL")
    )

    # Important Dates
    first_contact_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_contact_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    next_followup_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_activity_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Conversion Tracking
    converted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    converted_to_academy_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academies.id", ondelete="SET NULL")
    )
    converted_to_deal_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_deals.id", ondelete="SET NULL")
    )

    # Lost Lead Tracking
    lost_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    lost_reason: Mapped[Optional[str]] = mapped_column(String(255))
    lost_reason_details: Mapped[Optional[str]] = mapped_column(Text)
    competitor_name: Mapped[Optional[str]] = mapped_column(String(255))

    # External CRM Integration
    external_crm_id: Mapped[Optional[str]] = mapped_column(String(255))
    external_crm_type: Mapped[Optional[ExternalCRMType]] = mapped_column(
        SQLEnum(ExternalCRMType)
    )
    external_crm_url: Mapped[Optional[str]] = mapped_column(String(500))
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    sync_status: Mapped[Optional[SyncStatus]] = mapped_column(SQLEnum(SyncStatus))

    # Organization and Tagging
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Scoring Components (for detailed analysis)
    score_breakdown: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)
    engagement_score: Mapped[int] = mapped_column(Integer, default=0)
    fit_score: Mapped[int] = mapped_column(Integer, default=0)
    behavior_score: Mapped[int] = mapped_column(Integer, default=0)

    # Activity Counters
    total_emails_sent: Mapped[int] = mapped_column(Integer, default=0)
    total_emails_opened: Mapped[int] = mapped_column(Integer, default=0)
    total_calls: Mapped[int] = mapped_column(Integer, default=0)
    total_meetings: Mapped[int] = mapped_column(Integer, default=0)
    website_visits: Mapped[int] = mapped_column(Integer, default=0)
    content_downloads: Mapped[int] = mapped_column(Integer, default=0)

    # Location Information
    address_line1: Mapped[Optional[str]] = mapped_column(String(255))
    address_line2: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    country: Mapped[Optional[str]] = mapped_column(String(100))
    timezone: Mapped[Optional[str]] = mapped_column(String(50))

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
    contacts = relationship("CRMContact", back_populates="lead", cascade="all, delete-orphan")
    deals = relationship("CRMDeal", back_populates="lead")
    communications = relationship("CRMCommunication", back_populates="lead")
    tasks = relationship("CRMTask", back_populates="lead")

    # Indexes
    __table_args__ = (
        Index("idx_crm_leads_status", "status"),
        Index("idx_crm_leads_source", "source"),
        Index("idx_crm_leads_assigned_to", "assigned_to_id"),
        Index("idx_crm_leads_lead_score", "lead_score"),
        Index("idx_crm_leads_created_at", "created_at"),
        Index("idx_crm_leads_next_followup", "next_followup_date"),
        Index("idx_crm_leads_email", "contact_email"),
        Index("idx_crm_leads_external_crm", "external_crm_type", "external_crm_id"),
        Index("idx_crm_leads_is_qualified", "is_qualified"),
        CheckConstraint("lead_score >= 0 AND lead_score <= 100", name="ck_lead_score_range"),
    )

    def __repr__(self) -> str:
        return f"<CRMLead {self.organization_name} ({self.status.value})>"

    @property
    def full_contact_name(self) -> str:
        """Return full name of primary contact"""
        return f"{self.contact_first_name} {self.contact_last_name}"

    @property
    def days_since_last_contact(self) -> Optional[int]:
        """Calculate days since last contact"""
        if self.last_contact_date:
            delta = datetime.utcnow() - self.last_contact_date.replace(tzinfo=None)
            return delta.days
        return None

    @property
    def is_stale(self) -> bool:
        """Check if lead has been inactive for more than 30 days"""
        days = self.days_since_last_contact
        return days is not None and days > 30


# =============================================================================
# MODEL: CRMContact - Multi-Contact per Organization
# =============================================================================

class CRMContact(Base):
    """
    Contact management model supporting multiple contacts per lead/academy.
    Tracks individual contact preferences and engagement.
    """
    __tablename__ = "crm_contacts"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Parent References (one of these should be set)
    lead_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_leads.id", ondelete="CASCADE")
    )
    academy_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academies.id", ondelete="CASCADE")
    )

    # Contact Information
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    mobile: Mapped[Optional[str]] = mapped_column(String(50))

    # Professional Information
    title: Mapped[Optional[str]] = mapped_column(String(150))
    department: Mapped[Optional[str]] = mapped_column(String(100))
    contact_type: Mapped[ContactType] = mapped_column(
        SQLEnum(ContactType),
        default=ContactType.OTHER
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    # Communication Preferences
    preferred_contact_method: Mapped[Optional[ContactMethod]] = mapped_column(
        SQLEnum(ContactMethod)
    )
    preferred_language: Mapped[str] = mapped_column(String(10), default="en")
    timezone: Mapped[Optional[str]] = mapped_column(String(50))
    best_time_to_contact: Mapped[Optional[str]] = mapped_column(String(100))

    # Social Media
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500))
    twitter_handle: Mapped[Optional[str]] = mapped_column(String(100))
    facebook_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Marketing Preferences
    email_opt_in: Mapped[bool] = mapped_column(Boolean, default=True)
    sms_opt_in: Mapped[bool] = mapped_column(Boolean, default=False)
    marketing_opt_in: Mapped[bool] = mapped_column(Boolean, default=True)
    newsletter_subscribed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Email Engagement Tracking
    last_email_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_email_opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_email_clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    emails_sent_count: Mapped[int] = mapped_column(Integer, default=0)
    emails_opened_count: Mapped[int] = mapped_column(Integer, default=0)
    emails_clicked_count: Mapped[int] = mapped_column(Integer, default=0)
    email_bounce_count: Mapped[int] = mapped_column(Integer, default=0)
    unsubscribed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Personal Details
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date)
    anniversary_date: Mapped[Optional[date]] = mapped_column(Date)

    # Organization
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Avatar and Profile
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Engagement Scoring
    engagement_score: Mapped[int] = mapped_column(Integer, default=0)
    last_interaction_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # External CRM Integration
    external_crm_id: Mapped[Optional[str]] = mapped_column(String(255))
    external_crm_type: Mapped[Optional[ExternalCRMType]] = mapped_column(
        SQLEnum(ExternalCRMType)
    )
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

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
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    lead = relationship("CRMLead", back_populates="contacts")
    communications = relationship("CRMCommunication", back_populates="contact")

    # Indexes
    __table_args__ = (
        Index("idx_crm_contacts_lead_id", "lead_id"),
        Index("idx_crm_contacts_academy_id", "academy_id"),
        Index("idx_crm_contacts_email", "email"),
        Index("idx_crm_contacts_is_primary", "is_primary"),
        Index("idx_crm_contacts_contact_type", "contact_type"),
        Index("idx_crm_contacts_external_crm", "external_crm_type", "external_crm_id"),
        UniqueConstraint("email", "lead_id", name="uq_contact_email_lead"),
        UniqueConstraint("email", "academy_id", name="uq_contact_email_academy"),
    )

    def __repr__(self) -> str:
        return f"<CRMContact {self.first_name} {self.last_name} ({self.email})>"

    @property
    def full_name(self) -> str:
        """Return full name of contact"""
        return f"{self.first_name} {self.last_name}"

    @property
    def email_open_rate(self) -> float:
        """Calculate email open rate"""
        if self.emails_sent_count == 0:
            return 0.0
        return (self.emails_opened_count / self.emails_sent_count) * 100

    @property
    def email_click_rate(self) -> float:
        """Calculate email click rate"""
        if self.emails_opened_count == 0:
            return 0.0
        return (self.emails_clicked_count / self.emails_opened_count) * 100


# =============================================================================
# MODEL: CRMDeal - Sales Pipeline with Stage History
# =============================================================================

class CRMDeal(Base):
    """
    Deal/opportunity management model with full pipeline tracking.
    Supports stage history, probability tracking, and forecasting.
    """
    __tablename__ = "crm_deals"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Parent References
    lead_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_leads.id", ondelete="SET NULL")
    )
    academy_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academies.id", ondelete="SET NULL")
    )

    # Deal Information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    deal_number: Mapped[Optional[str]] = mapped_column(String(50), unique=True)

    # Pipeline Stage
    stage: Mapped[DealStage] = mapped_column(
        SQLEnum(DealStage),
        default=DealStage.QUALIFICATION
    )
    probability: Mapped[int] = mapped_column(Integer, default=10)  # 0-100%
    priority: Mapped[DealPriority] = mapped_column(
        SQLEnum(DealPriority),
        default=DealPriority.MEDIUM
    )

    # Financial Information
    amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    recurring_revenue: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    contract_length_months: Mapped[Optional[int]] = mapped_column(Integer)
    discount_percent: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    discount_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))

    # Products/Services
    products: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)
    # Structure: [{"product_id": "...", "name": "...", "quantity": 1, "price": 100.00}]

    # Ownership
    owner_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL")
    )
    team_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="SET NULL")
    )

    # Important Dates
    expected_close_date: Mapped[Optional[date]] = mapped_column(Date)
    actual_close_date: Mapped[Optional[date]] = mapped_column(Date)
    contract_start_date: Mapped[Optional[date]] = mapped_column(Date)
    contract_end_date: Mapped[Optional[date]] = mapped_column(Date)
    next_step_date: Mapped[Optional[date]] = mapped_column(Date)

    # Stage History
    stage_history: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)
    # Structure: [{"stage": "qualification", "entered_at": "...", "exited_at": "...", "duration_hours": 24}]

    # Current Stage Metrics
    stage_entered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    days_in_stage: Mapped[int] = mapped_column(Integer, default=0)

    # Win/Loss Information
    won_reason: Mapped[Optional[str]] = mapped_column(String(255))
    lost_reason: Mapped[Optional[str]] = mapped_column(String(255))
    lost_reason_details: Mapped[Optional[str]] = mapped_column(Text)
    competitor: Mapped[Optional[str]] = mapped_column(String(255))

    # Next Steps
    next_step: Mapped[Optional[str]] = mapped_column(Text)

    # Forecasting
    forecast_category: Mapped[Optional[str]] = mapped_column(String(50))
    # Values: "pipeline", "best_case", "commit", "closed"
    is_in_forecast: Mapped[bool] = mapped_column(Boolean, default=True)
    weighted_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))

    # Activity Tracking
    last_activity_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    total_activities: Mapped[int] = mapped_column(Integer, default=0)

    # Organization
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)

    # External CRM Integration
    external_crm_id: Mapped[Optional[str]] = mapped_column(String(255))
    external_crm_type: Mapped[Optional[ExternalCRMType]] = mapped_column(
        SQLEnum(ExternalCRMType)
    )
    external_crm_url: Mapped[Optional[str]] = mapped_column(String(500))
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

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
    lead = relationship("CRMLead", back_populates="deals")
    communications = relationship("CRMCommunication", back_populates="deal")
    tasks = relationship("CRMTask", back_populates="deal")

    # Indexes
    __table_args__ = (
        Index("idx_crm_deals_stage", "stage"),
        Index("idx_crm_deals_owner_id", "owner_id"),
        Index("idx_crm_deals_lead_id", "lead_id"),
        Index("idx_crm_deals_academy_id", "academy_id"),
        Index("idx_crm_deals_expected_close", "expected_close_date"),
        Index("idx_crm_deals_amount", "amount"),
        Index("idx_crm_deals_created_at", "created_at"),
        Index("idx_crm_deals_external_crm", "external_crm_type", "external_crm_id"),
        CheckConstraint("probability >= 0 AND probability <= 100", name="ck_deal_probability_range"),
    )

    def __repr__(self) -> str:
        return f"<CRMDeal {self.name} ({self.stage.value})>"

    @property
    def total_value(self) -> Decimal:
        """Calculate total deal value including recurring"""
        base = self.amount or Decimal("0")
        recurring = (self.recurring_revenue or Decimal("0")) * (self.contract_length_months or 0)
        return base + recurring

    @property
    def weighted_value(self) -> Decimal:
        """Calculate probability-weighted deal value"""
        return (self.amount or Decimal("0")) * Decimal(self.probability) / Decimal("100")

    @property
    def is_open(self) -> bool:
        """Check if deal is still open"""
        return self.stage not in [DealStage.CLOSED_WON, DealStage.CLOSED_LOST]

    @property
    def is_won(self) -> bool:
        """Check if deal was won"""
        return self.stage == DealStage.CLOSED_WON

    def update_stage(self, new_stage: DealStage) -> None:
        """Update deal stage and record in history"""
        now = datetime.utcnow()

        # Record exit from current stage
        if self.stage_history and self.stage_entered_at:
            duration = (now - self.stage_entered_at).total_seconds() / 3600
            self.stage_history[-1]["exited_at"] = now.isoformat()
            self.stage_history[-1]["duration_hours"] = round(duration, 2)

        # Enter new stage
        if not self.stage_history:
            self.stage_history = []

        self.stage_history.append({
            "stage": new_stage.value,
            "entered_at": now.isoformat(),
            "exited_at": None,
            "duration_hours": None
        })

        self.stage = new_stage
        self.stage_entered_at = now
        self.days_in_stage = 0

        # Update probability based on stage
        stage_probabilities = {
            DealStage.QUALIFICATION: 10,
            DealStage.NEEDS_ANALYSIS: 20,
            DealStage.PROPOSAL: 50,
            DealStage.NEGOTIATION: 75,
            DealStage.CLOSED_WON: 100,
            DealStage.CLOSED_LOST: 0,
            DealStage.ON_HOLD: self.probability,
            DealStage.RENEWAL: 80,
        }
        self.probability = stage_probabilities.get(new_stage, self.probability)


# =============================================================================
# MODEL: CRMCommunication - Interaction Tracking
# =============================================================================

class CRMCommunication(Base):
    """
    Communication/interaction tracking model.
    Records all touchpoints with leads and customers.
    """
    __tablename__ = "crm_communications"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Parent References
    lead_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_leads.id", ondelete="CASCADE")
    )
    academy_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academies.id", ondelete="CASCADE")
    )
    contact_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_contacts.id", ondelete="SET NULL")
    )
    deal_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_deals.id", ondelete="SET NULL")
    )

    # User who created/made the communication
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Communication Type and Direction
    comm_type: Mapped[CommunicationType] = mapped_column(
        SQLEnum(CommunicationType),
        nullable=False
    )
    direction: Mapped[CommunicationDirection] = mapped_column(
        SQLEnum(CommunicationDirection),
        default=CommunicationDirection.OUTBOUND
    )

    # Content
    subject: Mapped[Optional[str]] = mapped_column(String(500))
    content: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)

    # Call-specific Fields
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    outcome: Mapped[Optional[CommunicationOutcome]] = mapped_column(
        SQLEnum(CommunicationOutcome)
    )
    call_recording_url: Mapped[Optional[str]] = mapped_column(String(500))
    call_transcription: Mapped[Optional[str]] = mapped_column(Text)

    # Email-specific Fields
    email_message_id: Mapped[Optional[str]] = mapped_column(String(255))
    email_thread_id: Mapped[Optional[str]] = mapped_column(String(255))
    email_from: Mapped[Optional[str]] = mapped_column(String(255))
    email_to: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    email_cc: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    email_bcc: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    email_opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    email_clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    email_bounced: Mapped[bool] = mapped_column(Boolean, default=False)
    email_bounce_reason: Mapped[Optional[str]] = mapped_column(String(255))

    # Meeting-specific Fields
    meeting_start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    meeting_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    meeting_location: Mapped[Optional[str]] = mapped_column(String(255))
    meeting_url: Mapped[Optional[str]] = mapped_column(String(500))
    meeting_attendees: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    meeting_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Attachments
    attachments: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)
    # Structure: [{"name": "...", "url": "...", "size": 1024, "type": "application/pdf"}]

    # AI Analysis
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float)  # -1 to 1
    sentiment_label: Mapped[Optional[SentimentLabel]] = mapped_column(
        SQLEnum(SentimentLabel)
    )
    ai_summary: Mapped[Optional[str]] = mapped_column(Text)
    key_points: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    action_items: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    # Status
    is_scheduled: Mapped[bool] = mapped_column(Boolean, default=False)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_important: Mapped[bool] = mapped_column(Boolean, default=False)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)

    # Campaign Tracking
    campaign_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_campaigns.id", ondelete="SET NULL")
    )

    # Organization
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)

    # External CRM Integration
    external_crm_id: Mapped[Optional[str]] = mapped_column(String(255))
    external_crm_type: Mapped[Optional[ExternalCRMType]] = mapped_column(
        SQLEnum(ExternalCRMType)
    )
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

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
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    lead = relationship("CRMLead", back_populates="communications")
    contact = relationship("CRMContact", back_populates="communications")
    deal = relationship("CRMDeal", back_populates="communications")

    # Indexes
    __table_args__ = (
        Index("idx_crm_comm_lead_id", "lead_id"),
        Index("idx_crm_comm_academy_id", "academy_id"),
        Index("idx_crm_comm_contact_id", "contact_id"),
        Index("idx_crm_comm_deal_id", "deal_id"),
        Index("idx_crm_comm_user_id", "user_id"),
        Index("idx_crm_comm_type", "comm_type"),
        Index("idx_crm_comm_direction", "direction"),
        Index("idx_crm_comm_created_at", "created_at"),
        Index("idx_crm_comm_email_thread", "email_thread_id"),
        Index("idx_crm_comm_scheduled", "is_scheduled", "scheduled_at"),
    )

    def __repr__(self) -> str:
        return f"<CRMCommunication {self.comm_type.value} ({self.direction.value})>"


# =============================================================================
# MODEL: CRMTask - Task/Reminder System
# =============================================================================

class CRMTask(Base):
    """
    Task and reminder management model.
    Supports recurring tasks and deadline tracking.
    """
    __tablename__ = "crm_tasks"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Parent References
    lead_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_leads.id", ondelete="CASCADE")
    )
    academy_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academies.id", ondelete="CASCADE")
    )
    deal_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_deals.id", ondelete="SET NULL")
    )
    contact_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_contacts.id", ondelete="SET NULL")
    )

    # Task Information
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    task_type: Mapped[TaskType] = mapped_column(
        SQLEnum(TaskType),
        default=TaskType.OTHER
    )

    # Priority and Status
    priority: Mapped[TaskPriority] = mapped_column(
        SQLEnum(TaskPriority),
        default=TaskPriority.MEDIUM
    )
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus),
        default=TaskStatus.PENDING
    )

    # Assignment
    assigned_to_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL")
    )
    created_by_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Dates
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    reminder_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Recurrence
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_pattern: Mapped[Optional[RecurrencePattern]] = mapped_column(
        SQLEnum(RecurrencePattern)
    )
    recurrence_end_date: Mapped[Optional[date]] = mapped_column(Date)
    recurrence_count: Mapped[Optional[int]] = mapped_column(Integer)
    parent_task_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_tasks.id", ondelete="SET NULL")
    )

    # Progress and Outcome
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    outcome: Mapped[Optional[str]] = mapped_column(Text)
    outcome_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Time Tracking
    estimated_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    actual_minutes: Mapped[Optional[int]] = mapped_column(Integer)

    # Communication Link (auto-created from task)
    related_communication_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_communications.id", ondelete="SET NULL")
    )

    # Reminders
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    snooze_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Organization
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)

    # Checklist
    checklist: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)
    # Structure: [{"item": "...", "completed": false}]

    # Workflow Reference
    workflow_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_workflows.id", ondelete="SET NULL")
    )
    workflow_execution_id: Mapped[Optional[str]] = mapped_column(String(255))

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
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    lead = relationship("CRMLead", back_populates="tasks")
    deal = relationship("CRMDeal", back_populates="tasks")
    subtasks = relationship(
        "CRMTask",
        backref=backref("parent_task", remote_side="CRMTask.id"),
        foreign_keys=[parent_task_id]
    )

    # Indexes
    __table_args__ = (
        Index("idx_crm_tasks_lead_id", "lead_id"),
        Index("idx_crm_tasks_academy_id", "academy_id"),
        Index("idx_crm_tasks_deal_id", "deal_id"),
        Index("idx_crm_tasks_assigned_to", "assigned_to_id"),
        Index("idx_crm_tasks_status", "status"),
        Index("idx_crm_tasks_priority", "priority"),
        Index("idx_crm_tasks_due_date", "due_date"),
        Index("idx_crm_tasks_created_at", "created_at"),
        Index("idx_crm_tasks_is_recurring", "is_recurring"),
        CheckConstraint("progress_percent >= 0 AND progress_percent <= 100", name="ck_task_progress_range"),
    )

    def __repr__(self) -> str:
        return f"<CRMTask {self.title} ({self.status.value})>"

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if not self.due_date or self.status == TaskStatus.COMPLETED:
            return False
        return datetime.utcnow() > self.due_date.replace(tzinfo=None)

    @property
    def days_until_due(self) -> Optional[int]:
        """Calculate days until due date"""
        if not self.due_date:
            return None
        delta = self.due_date.replace(tzinfo=None) - datetime.utcnow()
        return delta.days

    def mark_completed(self, outcome: Optional[str] = None) -> None:
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress_percent = 100
        if outcome:
            self.outcome = outcome


# =============================================================================
# MODEL: CRMCampaign - Marketing Campaigns
# =============================================================================

class CRMCampaign(Base):
    """
    Marketing campaign management model.
    Tracks campaign performance, costs, and ROI.
    """
    __tablename__ = "crm_campaigns"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Academy Reference (optional for platform-wide campaigns)
    academy_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academies.id", ondelete="CASCADE")
    )

    # Campaign Information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    campaign_code: Mapped[Optional[str]] = mapped_column(String(50), unique=True)

    # Type and Status
    campaign_type: Mapped[CampaignType] = mapped_column(
        SQLEnum(CampaignType),
        nullable=False
    )
    status: Mapped[CampaignStatus] = mapped_column(
        SQLEnum(CampaignStatus),
        default=CampaignStatus.DRAFT
    )

    # Target Audience
    target_audience: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)
    # Structure: {"filters": {"industry": [...], "size": [...], "location": [...]}, "segment_ids": [...]}
    target_leads_count: Mapped[int] = mapped_column(Integer, default=0)

    # Schedule
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")

    # Budget
    budget: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    actual_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")

    # Goals
    goal_leads: Mapped[Optional[int]] = mapped_column(Integer)
    goal_conversions: Mapped[Optional[int]] = mapped_column(Integer)
    goal_revenue: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    goal_open_rate: Mapped[Optional[float]] = mapped_column(Float)
    goal_click_rate: Mapped[Optional[float]] = mapped_column(Float)

    # Results - Leads
    leads_generated: Mapped[int] = mapped_column(Integer, default=0)
    leads_qualified: Mapped[int] = mapped_column(Integer, default=0)
    conversions: Mapped[int] = mapped_column(Integer, default=0)
    revenue_generated: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))

    # Results - Email Metrics
    emails_sent: Mapped[int] = mapped_column(Integer, default=0)
    emails_delivered: Mapped[int] = mapped_column(Integer, default=0)
    emails_opened: Mapped[int] = mapped_column(Integer, default=0)
    unique_opens: Mapped[int] = mapped_column(Integer, default=0)
    emails_clicked: Mapped[int] = mapped_column(Integer, default=0)
    unique_clicks: Mapped[int] = mapped_column(Integer, default=0)
    emails_bounced: Mapped[int] = mapped_column(Integer, default=0)
    unsubscribes: Mapped[int] = mapped_column(Integer, default=0)
    spam_reports: Mapped[int] = mapped_column(Integer, default=0)

    # Results - Other Metrics
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    page_views: Mapped[int] = mapped_column(Integer, default=0)
    form_submissions: Mapped[int] = mapped_column(Integer, default=0)
    downloads: Mapped[int] = mapped_column(Integer, default=0)
    registrations: Mapped[int] = mapped_column(Integer, default=0)

    # Content Template
    content_template: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)
    # Structure: {"subject": "...", "body_html": "...", "body_text": "...", "from_name": "...", "reply_to": "..."}

    # A/B Testing
    is_ab_test: Mapped[bool] = mapped_column(Boolean, default=False)
    ab_variants: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)
    # Structure: [{"name": "A", "subject": "...", "content": "...", "percentage": 50}]
    winning_variant: Mapped[Optional[str]] = mapped_column(String(50))

    # Automation
    is_automated: Mapped[bool] = mapped_column(Boolean, default=False)
    automation_trigger: Mapped[Optional[str]] = mapped_column(String(100))
    automation_delay_hours: Mapped[Optional[int]] = mapped_column(Integer)

    # External Integration
    external_campaign_id: Mapped[Optional[str]] = mapped_column(String(255))
    external_platform: Mapped[Optional[str]] = mapped_column(String(100))
    tracking_url: Mapped[Optional[str]] = mapped_column(String(500))
    utm_params: Mapped[Optional[Dict[str, str]]] = mapped_column(JSONB, default=dict)

    # Owner
    owner_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL")
    )
    team_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="SET NULL")
    )

    # Organization
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
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

    # Indexes
    __table_args__ = (
        Index("idx_crm_campaigns_academy_id", "academy_id"),
        Index("idx_crm_campaigns_status", "status"),
        Index("idx_crm_campaigns_type", "campaign_type"),
        Index("idx_crm_campaigns_start_date", "start_date"),
        Index("idx_crm_campaigns_end_date", "end_date"),
        Index("idx_crm_campaigns_owner_id", "owner_id"),
        Index("idx_crm_campaigns_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<CRMCampaign {self.name} ({self.status.value})>"

    @property
    def open_rate(self) -> float:
        """Calculate email open rate"""
        if self.emails_delivered == 0:
            return 0.0
        return (self.unique_opens / self.emails_delivered) * 100

    @property
    def click_rate(self) -> float:
        """Calculate email click rate"""
        if self.unique_opens == 0:
            return 0.0
        return (self.unique_clicks / self.unique_opens) * 100

    @property
    def click_to_open_rate(self) -> float:
        """Calculate click-to-open rate (CTOR)"""
        if self.unique_opens == 0:
            return 0.0
        return (self.unique_clicks / self.unique_opens) * 100

    @property
    def bounce_rate(self) -> float:
        """Calculate email bounce rate"""
        if self.emails_sent == 0:
            return 0.0
        return (self.emails_bounced / self.emails_sent) * 100

    @property
    def conversion_rate(self) -> float:
        """Calculate lead-to-conversion rate"""
        if self.leads_generated == 0:
            return 0.0
        return (self.conversions / self.leads_generated) * 100

    @property
    def roi(self) -> float:
        """Calculate return on investment"""
        if not self.actual_cost or self.actual_cost == 0:
            return 0.0
        return float((self.revenue_generated - self.actual_cost) / self.actual_cost * 100)

    @property
    def cost_per_lead(self) -> float:
        """Calculate cost per lead"""
        if self.leads_generated == 0 or not self.actual_cost:
            return 0.0
        return float(self.actual_cost / self.leads_generated)

    @property
    def cost_per_conversion(self) -> float:
        """Calculate cost per conversion"""
        if self.conversions == 0 or not self.actual_cost:
            return 0.0
        return float(self.actual_cost / self.conversions)


# =============================================================================
# MODEL: CRMWorkflow - Automation with Triggers/Actions
# =============================================================================

class CRMWorkflow(Base):
    """
    Workflow automation model with triggers and actions.
    Enables automated CRM processes based on events.
    """
    __tablename__ = "crm_workflows"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Academy Reference (optional for platform-wide workflows)
    academy_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academies.id", ondelete="CASCADE")
    )

    # Workflow Information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    # Trigger Configuration
    trigger_type: Mapped[WorkflowTrigger] = mapped_column(
        SQLEnum(WorkflowTrigger),
        nullable=False
    )
    trigger_conditions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)
    # Structure depends on trigger type:
    # LEAD_STATUS_CHANGED: {"from_status": "new", "to_status": "contacted"}
    # LEAD_SCORE_THRESHOLD: {"operator": ">=", "value": 80}
    # NO_ACTIVITY_DAYS: {"days": 14}

    # Actions
    actions: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list)
    # Structure: [
    #   {"type": "send_email", "template_id": "...", "delay_hours": 0},
    #   {"type": "create_task", "task_type": "call", "assigned_to": "owner", "delay_hours": 24},
    #   {"type": "update_lead_status", "status": "engaged", "delay_hours": 0},
    #   {"type": "send_notification", "channel": "slack", "message": "...", "delay_hours": 0}
    # ]

    # Execution Settings
    max_executions_per_record: Mapped[int] = mapped_column(Integer, default=1)
    cooldown_hours: Mapped[int] = mapped_column(Integer, default=0)
    run_on_existing: Mapped[bool] = mapped_column(Boolean, default=False)

    # Filters
    filter_conditions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)
    # Structure: {"lead_source": ["website", "referral"], "industry": ["education"]}

    # Scheduling
    schedule_type: Mapped[str] = mapped_column(String(50), default="immediate")
    # Values: "immediate", "scheduled", "recurring"
    schedule_time: Mapped[Optional[str]] = mapped_column(String(10))  # HH:MM format
    schedule_timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    schedule_days: Mapped[Optional[List[int]]] = mapped_column(ARRAY(Integer))  # 0-6 for days

    # Execution Statistics
    execution_count: Mapped[int] = mapped_column(Integer, default=0)
    successful_executions: Mapped[int] = mapped_column(Integer, default=0)
    failed_executions: Mapped[int] = mapped_column(Integer, default=0)
    last_executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[Optional[str]] = mapped_column(Text)

    # Version Control
    version: Mapped[int] = mapped_column(Integer, default=1)
    parent_workflow_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_workflows.id", ondelete="SET NULL")
    )

    # A/B Testing
    is_ab_test: Mapped[bool] = mapped_column(Boolean, default=False)
    ab_variants: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)

    # Owner
    created_by_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Organization
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
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
    activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    deactivated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Soft Delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    execution_logs = relationship("WorkflowExecutionLog", back_populates="workflow")

    # Indexes
    __table_args__ = (
        Index("idx_crm_workflows_academy_id", "academy_id"),
        Index("idx_crm_workflows_trigger_type", "trigger_type"),
        Index("idx_crm_workflows_is_active", "is_active"),
        Index("idx_crm_workflows_created_by", "created_by_id"),
        Index("idx_crm_workflows_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<CRMWorkflow {self.name} ({'active' if self.is_active else 'inactive'})>"

    @property
    def success_rate(self) -> float:
        """Calculate workflow success rate"""
        if self.execution_count == 0:
            return 0.0
        return (self.successful_executions / self.execution_count) * 100

    def activate(self) -> None:
        """Activate the workflow"""
        self.is_active = True
        self.activated_at = datetime.utcnow()
        self.deactivated_at = None

    def deactivate(self) -> None:
        """Deactivate the workflow"""
        self.is_active = False
        self.deactivated_at = datetime.utcnow()


# =============================================================================
# MODEL: WorkflowExecutionLog - Track Workflow Executions
# =============================================================================

class WorkflowExecutionLog(Base):
    """
    Log of workflow executions for auditing and debugging.
    """
    __tablename__ = "crm_workflow_execution_logs"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # References
    workflow_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_workflows.id", ondelete="CASCADE"),
        nullable=False
    )
    lead_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_leads.id", ondelete="SET NULL")
    )
    deal_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_deals.id", ondelete="SET NULL")
    )

    # Execution Details
    execution_id: Mapped[str] = mapped_column(String(255), nullable=False)
    trigger_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)

    # Status
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    # Values: "pending", "in_progress", "completed", "failed", "cancelled"

    # Actions Executed
    actions_executed: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)
    # Structure: [{"action_type": "...", "status": "...", "result": {...}, "executed_at": "..."}]

    # Error Information
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    error_stack: Mapped[Optional[str]] = mapped_column(Text)

    # Timing
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)

    # Relationships
    workflow = relationship("CRMWorkflow", back_populates="execution_logs")

    # Indexes
    __table_args__ = (
        Index("idx_wf_exec_log_workflow_id", "workflow_id"),
        Index("idx_wf_exec_log_lead_id", "lead_id"),
        Index("idx_wf_exec_log_deal_id", "deal_id"),
        Index("idx_wf_exec_log_status", "status"),
        Index("idx_wf_exec_log_started_at", "started_at"),
        Index("idx_wf_exec_log_execution_id", "execution_id"),
    )

    def __repr__(self) -> str:
        return f"<WorkflowExecutionLog {self.execution_id} ({self.status})>"


# =============================================================================
# MODEL: ExternalCRMIntegration - Integration Configuration
# =============================================================================

class ExternalCRMIntegration(Base):
    """
    External CRM integration configuration model.
    Manages connections to Salesforce, HubSpot, Zoho, etc.
    """
    __tablename__ = "crm_external_integrations"

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

    # Integration Type
    crm_type: Mapped[ExternalCRMType] = mapped_column(
        SQLEnum(ExternalCRMType),
        nullable=False
    )
    integration_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # OAuth Tokens
    access_token: Mapped[Optional[str]] = mapped_column(Text)  # Encrypted
    refresh_token: Mapped[Optional[str]] = mapped_column(Text)  # Encrypted
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    token_type: Mapped[str] = mapped_column(String(50), default="Bearer")

    # API Credentials (for non-OAuth)
    api_key: Mapped[Optional[str]] = mapped_column(Text)  # Encrypted
    api_secret: Mapped[Optional[str]] = mapped_column(Text)  # Encrypted
    instance_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Webhook Configuration
    webhook_url: Mapped[Optional[str]] = mapped_column(String(500))
    webhook_secret: Mapped[Optional[str]] = mapped_column(String(255))  # For HMAC signing
    webhook_events: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    # Sync Configuration
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sync_direction: Mapped[SyncDirection] = mapped_column(
        SQLEnum(SyncDirection),
        default=SyncDirection.BIDIRECTIONAL
    )
    sync_interval_minutes: Mapped[int] = mapped_column(Integer, default=60)

    # Entity Sync Settings
    sync_leads: Mapped[bool] = mapped_column(Boolean, default=True)
    sync_contacts: Mapped[bool] = mapped_column(Boolean, default=True)
    sync_deals: Mapped[bool] = mapped_column(Boolean, default=True)
    sync_communications: Mapped[bool] = mapped_column(Boolean, default=False)
    sync_tasks: Mapped[bool] = mapped_column(Boolean, default=False)

    # Field Mappings
    field_mappings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)
    # Structure: {
    #   "leads": {"organization_name": "Company", "contact_email": "Email"},
    #   "contacts": {"first_name": "FirstName", "last_name": "LastName"},
    #   "deals": {"name": "Name", "amount": "Amount"}
    # }

    # Custom Object Mappings
    custom_object_mappings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)

    # Sync Status
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_sync_status: Mapped[Optional[SyncStatus]] = mapped_column(SQLEnum(SyncStatus))
    last_sync_error: Mapped[Optional[str]] = mapped_column(Text)
    last_sync_records_synced: Mapped[int] = mapped_column(Integer, default=0)

    # Sync Statistics
    total_records_synced: Mapped[int] = mapped_column(Integer, default=0)
    total_sync_errors: Mapped[int] = mapped_column(Integer, default=0)

    # Sync Cursors (for pagination/delta sync)
    sync_cursors: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, default=dict)
    # Structure: {"leads": {"last_modified": "2024-01-01T00:00:00Z"}, ...}

    # Rate Limiting
    rate_limit_remaining: Mapped[Optional[int]] = mapped_column(Integer)
    rate_limit_reset_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Error Handling
    consecutive_errors: Mapped[int] = mapped_column(Integer, default=0)
    error_backoff_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    max_retry_attempts: Mapped[int] = mapped_column(Integer, default=3)

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
    sync_logs = relationship("CRMSyncLog", back_populates="integration")

    # Indexes
    __table_args__ = (
        Index("idx_crm_ext_int_academy_id", "academy_id"),
        Index("idx_crm_ext_int_crm_type", "crm_type"),
        Index("idx_crm_ext_int_is_active", "is_active"),
        Index("idx_crm_ext_int_last_sync", "last_sync_at"),
        UniqueConstraint("academy_id", "crm_type", name="uq_academy_crm_type"),
    )

    def __repr__(self) -> str:
        return f"<ExternalCRMIntegration {self.crm_type.value} ({self.academy_id})>"

    @property
    def is_token_expired(self) -> bool:
        """Check if OAuth token is expired"""
        if not self.token_expires_at:
            return False
        return datetime.utcnow() > self.token_expires_at.replace(tzinfo=None)

    @property
    def needs_reauth(self) -> bool:
        """Check if integration needs re-authentication"""
        return self.is_token_expired and not self.refresh_token

    def should_sync(self) -> bool:
        """Check if sync should run based on interval"""
        if not self.is_active:
            return False
        if not self.last_sync_at:
            return True
        elapsed = (datetime.utcnow() - self.last_sync_at.replace(tzinfo=None)).total_seconds() / 60
        return elapsed >= self.sync_interval_minutes


# =============================================================================
# MODEL: CRMSyncLog - Sync Operation Logging
# =============================================================================

class CRMSyncLog(Base):
    """
    Log of CRM sync operations for auditing and debugging.
    """
    __tablename__ = "crm_sync_logs"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # References
    integration_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_external_integrations.id", ondelete="CASCADE"),
        nullable=False
    )

    # Sync Details
    sync_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Values: "full", "incremental", "webhook"
    direction: Mapped[SyncDirection] = mapped_column(SQLEnum(SyncDirection), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Values: "leads", "contacts", "deals", "communications"

    # Status
    status: Mapped[SyncStatus] = mapped_column(SQLEnum(SyncStatus), nullable=False)

    # Statistics
    records_processed: Mapped[int] = mapped_column(Integer, default=0)
    records_created: Mapped[int] = mapped_column(Integer, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, default=0)
    records_deleted: Mapped[int] = mapped_column(Integer, default=0)
    records_failed: Mapped[int] = mapped_column(Integer, default=0)

    # Error Details
    errors: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list)
    # Structure: [{"record_id": "...", "error": "...", "field": "..."}]

    # Timing
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)

    # Cursor Information
    start_cursor: Mapped[Optional[str]] = mapped_column(String(255))
    end_cursor: Mapped[Optional[str]] = mapped_column(String(255))

    # Relationships
    integration = relationship("ExternalCRMIntegration", back_populates="sync_logs")

    # Indexes
    __table_args__ = (
        Index("idx_crm_sync_log_integration", "integration_id"),
        Index("idx_crm_sync_log_status", "status"),
        Index("idx_crm_sync_log_entity", "entity_type"),
        Index("idx_crm_sync_log_started", "started_at"),
    )

    def __repr__(self) -> str:
        return f"<CRMSyncLog {self.entity_type} {self.direction.value} ({self.status.value})>"


# =============================================================================
# MODEL: CRMEmailTemplate - Email Templates for Campaigns/Workflows
# =============================================================================

class CRMEmailTemplate(Base):
    """
    Email template model for campaigns and workflows.
    """
    __tablename__ = "crm_email_templates"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Academy Reference
    academy_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academies.id", ondelete="CASCADE")
    )

    # Template Information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(100))

    # Email Content
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body_html: Mapped[str] = mapped_column(Text, nullable=False)
    body_text: Mapped[Optional[str]] = mapped_column(Text)
    preview_text: Mapped[Optional[str]] = mapped_column(String(255))

    # Sender Configuration
    from_name: Mapped[Optional[str]] = mapped_column(String(255))
    from_email: Mapped[Optional[str]] = mapped_column(String(255))
    reply_to: Mapped[Optional[str]] = mapped_column(String(255))

    # Template Variables
    variables: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    # Available placeholders: ["{{first_name}}", "{{company}}", "{{exam_type}}"]

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Usage Statistics
    times_used: Mapped[int] = mapped_column(Integer, default=0)
    total_sent: Mapped[int] = mapped_column(Integer, default=0)
    total_opened: Mapped[int] = mapped_column(Integer, default=0)
    total_clicked: Mapped[int] = mapped_column(Integer, default=0)

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

    # Indexes
    __table_args__ = (
        Index("idx_crm_email_tmpl_academy", "academy_id"),
        Index("idx_crm_email_tmpl_category", "category"),
        Index("idx_crm_email_tmpl_is_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<CRMEmailTemplate {self.name}>"

    @property
    def open_rate(self) -> float:
        """Calculate template open rate"""
        if self.total_sent == 0:
            return 0.0
        return (self.total_opened / self.total_sent) * 100

    @property
    def click_rate(self) -> float:
        """Calculate template click rate"""
        if self.total_opened == 0:
            return 0.0
        return (self.total_clicked / self.total_opened) * 100


# =============================================================================
# MODEL: CRMNote - General Notes
# =============================================================================

class CRMNote(Base):
    """
    General notes attached to CRM entities.
    """
    __tablename__ = "crm_notes"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Parent References (one should be set)
    lead_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_leads.id", ondelete="CASCADE")
    )
    contact_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_contacts.id", ondelete="CASCADE")
    )
    deal_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_deals.id", ondelete="CASCADE")
    )
    academy_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academies.id", ondelete="CASCADE")
    )

    # Note Content
    title: Mapped[Optional[str]] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Classification
    note_type: Mapped[str] = mapped_column(String(50), default="general")
    # Values: "general", "meeting", "call", "important", "follow_up"
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)

    # Author
    author_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
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
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Indexes
    __table_args__ = (
        Index("idx_crm_notes_lead_id", "lead_id"),
        Index("idx_crm_notes_contact_id", "contact_id"),
        Index("idx_crm_notes_deal_id", "deal_id"),
        Index("idx_crm_notes_academy_id", "academy_id"),
        Index("idx_crm_notes_author_id", "author_id"),
        Index("idx_crm_notes_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<CRMNote {self.title or 'Untitled'}>"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_lead_score_breakdown(lead: CRMLead) -> Dict[str, int]:
    """
    Generate a detailed breakdown of lead scoring components.

    Args:
        lead: The lead to score

    Returns:
        Dict with score components
    """
    breakdown = {
        "fit_score": 0,
        "engagement_score": 0,
        "behavior_score": 0,
        "timing_score": 0
    }

    # Fit Score (max 25)
    if lead.organization_type in [LeadOrganizationType.LANGUAGE_SCHOOL, LeadOrganizationType.TEST_PREP_CENTER]:
        breakdown["fit_score"] += 10
    if lead.estimated_students and lead.estimated_students >= 100:
        breakdown["fit_score"] += 10
    if lead.budget_confirmed:
        breakdown["fit_score"] += 5

    # Engagement Score (max 25)
    if lead.total_emails_opened > 0:
        breakdown["engagement_score"] += min(10, lead.total_emails_opened * 2)
    if lead.total_meetings > 0:
        breakdown["engagement_score"] += min(10, lead.total_meetings * 5)
    if lead.website_visits > 0:
        breakdown["engagement_score"] += min(5, lead.website_visits)

    # Behavior Score (max 25)
    if lead.content_downloads > 0:
        breakdown["behavior_score"] += min(10, lead.content_downloads * 3)
    if lead.total_calls > 0:
        breakdown["behavior_score"] += min(10, lead.total_calls * 2)
    if lead.status in [LeadStatus.DEMO_COMPLETED, LeadStatus.PROPOSAL_SENT]:
        breakdown["behavior_score"] += 5

    # Timing Score (max 25)
    if lead.timeline_urgency == "immediate":
        breakdown["timing_score"] += 15
    elif lead.timeline_urgency == "1_month":
        breakdown["timing_score"] += 10
    elif lead.timeline_urgency == "3_months":
        breakdown["timing_score"] += 5

    if lead.days_since_last_contact is not None and lead.days_since_last_contact < 7:
        breakdown["timing_score"] += 10

    return breakdown


def calculate_total_lead_score(breakdown: Dict[str, int]) -> int:
    """
    Calculate total lead score from breakdown.

    Args:
        breakdown: Score breakdown dict

    Returns:
        Total score (0-100)
    """
    total = sum(breakdown.values())
    return min(100, max(0, total))
