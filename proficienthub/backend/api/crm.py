"""
ProficientHub - CRM API Endpoints
50+ REST endpoints covering Lead, Contact, Deal, Communication, Task,
Campaign management, External CRM sync, and Analytics dashboards.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Optional, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from models_crm import (
    CRMLead, CRMContact, CRMDeal, CRMCommunication, CRMTask,
    CRMCampaign, CRMWorkflow, ExternalCRMIntegration,
    LeadSource, LeadStatus, LeadOrganizationType, IndustryType,
    ContactType, ContactMethod,
    DealStage, DealPriority,
    CommunicationType, CommunicationDirection,
    TaskType, TaskPriority, TaskStatus,
    CampaignType, CampaignStatus,
    WorkflowTrigger,
    ExternalCRMType, SyncDirection
)
from crm_service import CRMService, LeadScoringService, get_crm_service
from external_crm_connector import ExternalCRMService, CRMConnectorFactory


# =============================================================================
# ROUTER INITIALIZATION
# =============================================================================

router = APIRouter(prefix="/api/v1/crm", tags=["CRM"])


# =============================================================================
# DEPENDENCIES (Placeholder - would come from your auth module)
# =============================================================================

async def get_db_session() -> AsyncSession:
    """Get database session - placeholder for dependency injection"""
    # In production, this would yield a session from your session factory
    pass


async def get_current_user():
    """Get current authenticated user - placeholder"""
    pass


# =============================================================================
# PYDANTIC SCHEMAS - Lead
# =============================================================================

class LeadCreate(BaseModel):
    """Schema for creating a new lead"""
    organization_name: str = Field(..., min_length=1, max_length=255)
    organization_type: Optional[LeadOrganizationType] = LeadOrganizationType.LANGUAGE_SCHOOL
    website: Optional[str] = None
    industry: Optional[IndustryType] = None
    employee_count: Optional[int] = None

    contact_first_name: str = Field(..., min_length=1, max_length=100)
    contact_last_name: str = Field(..., min_length=1, max_length=100)
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    contact_title: Optional[str] = None

    source: LeadSource = LeadSource.WEBSITE
    source_details: Optional[str] = None

    interested_exams: Optional[List[str]] = None
    estimated_students: Optional[int] = None
    estimated_deal_value: Optional[Decimal] = None

    address_line1: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class LeadUpdate(BaseModel):
    """Schema for updating a lead"""
    organization_name: Optional[str] = None
    organization_type: Optional[LeadOrganizationType] = None
    website: Optional[str] = None
    industry: Optional[IndustryType] = None

    contact_first_name: Optional[str] = None
    contact_last_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    contact_title: Optional[str] = None

    interested_exams: Optional[List[str]] = None
    estimated_students: Optional[int] = None
    estimated_deal_value: Optional[Decimal] = None

    assigned_to_id: Optional[UUID] = None
    next_followup_date: Optional[datetime] = None

    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class LeadStatusUpdate(BaseModel):
    """Schema for updating lead status"""
    status: LeadStatus
    notes: Optional[str] = None


class LeadConvert(BaseModel):
    """Schema for converting lead to customer"""
    academy_id: UUID
    deal_name: str
    deal_amount: Decimal
    owner_id: UUID


class LeadLost(BaseModel):
    """Schema for marking lead as lost"""
    reason: str
    details: Optional[str] = None
    competitor: Optional[str] = None


class LeadResponse(BaseModel):
    """Schema for lead response"""
    id: UUID
    organization_name: str
    organization_type: LeadOrganizationType
    contact_first_name: str
    contact_last_name: str
    contact_email: str
    source: LeadSource
    status: LeadStatus
    lead_score: int
    is_qualified: bool
    estimated_students: Optional[int]
    estimated_deal_value: Optional[Decimal]
    assigned_to_id: Optional[UUID]
    next_followup_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# PYDANTIC SCHEMAS - Contact
# =============================================================================

class ContactCreate(BaseModel):
    """Schema for creating a contact"""
    lead_id: Optional[UUID] = None
    academy_id: Optional[UUID] = None

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    mobile: Optional[str] = None

    title: Optional[str] = None
    department: Optional[str] = None
    contact_type: ContactType = ContactType.OTHER
    is_primary: bool = False

    preferred_contact_method: Optional[ContactMethod] = None
    preferred_language: str = "en"
    timezone: Optional[str] = None

    linkedin_url: Optional[str] = None

    email_opt_in: bool = True
    sms_opt_in: bool = False

    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class ContactUpdate(BaseModel):
    """Schema for updating a contact"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None

    title: Optional[str] = None
    department: Optional[str] = None
    contact_type: Optional[ContactType] = None
    is_primary: Optional[bool] = None

    preferred_contact_method: Optional[ContactMethod] = None
    email_opt_in: Optional[bool] = None
    sms_opt_in: Optional[bool] = None

    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class ContactResponse(BaseModel):
    """Schema for contact response"""
    id: UUID
    lead_id: Optional[UUID]
    academy_id: Optional[UUID]
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    title: Optional[str]
    contact_type: ContactType
    is_primary: bool
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# PYDANTIC SCHEMAS - Deal
# =============================================================================

class DealCreate(BaseModel):
    """Schema for creating a deal"""
    lead_id: Optional[UUID] = None
    academy_id: Optional[UUID] = None

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

    amount: Decimal
    currency: str = "EUR"
    recurring_revenue: Optional[Decimal] = None
    contract_length_months: Optional[int] = None

    products: Optional[List[Dict[str, Any]]] = None

    owner_id: UUID
    expected_close_date: Optional[date] = None

    tags: Optional[List[str]] = None


class DealUpdate(BaseModel):
    """Schema for updating a deal"""
    name: Optional[str] = None
    description: Optional[str] = None

    amount: Optional[Decimal] = None
    recurring_revenue: Optional[Decimal] = None
    contract_length_months: Optional[int] = None

    products: Optional[List[Dict[str, Any]]] = None

    owner_id: Optional[UUID] = None
    expected_close_date: Optional[date] = None
    next_step: Optional[str] = None

    tags: Optional[List[str]] = None


class DealStageUpdate(BaseModel):
    """Schema for updating deal stage"""
    stage: DealStage
    notes: Optional[str] = None
    won_reason: Optional[str] = None
    lost_reason: Optional[str] = None
    competitor: Optional[str] = None


class DealResponse(BaseModel):
    """Schema for deal response"""
    id: UUID
    deal_number: Optional[str]
    name: str
    lead_id: Optional[UUID]
    academy_id: Optional[UUID]
    stage: DealStage
    probability: int
    amount: Optional[Decimal]
    currency: str
    expected_close_date: Optional[date]
    owner_id: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# PYDANTIC SCHEMAS - Communication
# =============================================================================

class CommunicationCreate(BaseModel):
    """Schema for logging communication"""
    lead_id: Optional[UUID] = None
    academy_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    deal_id: Optional[UUID] = None

    comm_type: CommunicationType
    direction: CommunicationDirection = CommunicationDirection.OUTBOUND

    subject: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None

    # Call-specific
    duration_minutes: Optional[int] = None
    outcome: Optional[str] = None

    # Meeting-specific
    meeting_start_time: Optional[datetime] = None
    meeting_end_time: Optional[datetime] = None
    meeting_location: Optional[str] = None
    meeting_attendees: Optional[List[str]] = None

    attachments: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None


class CommunicationResponse(BaseModel):
    """Schema for communication response"""
    id: UUID
    comm_type: CommunicationType
    direction: CommunicationDirection
    subject: Optional[str]
    content: Optional[str]
    summary: Optional[str]
    duration_minutes: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# PYDANTIC SCHEMAS - Task
# =============================================================================

class TaskCreate(BaseModel):
    """Schema for creating a task"""
    lead_id: Optional[UUID] = None
    academy_id: Optional[UUID] = None
    deal_id: Optional[UUID] = None

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    task_type: TaskType = TaskType.OTHER

    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_to_id: Optional[UUID] = None

    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None

    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None

    checklist: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    title: Optional[str] = None
    description: Optional[str] = None
    task_type: Optional[TaskType] = None

    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    assigned_to_id: Optional[UUID] = None

    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None

    progress_percent: Optional[int] = None
    checklist: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None


class TaskComplete(BaseModel):
    """Schema for completing a task"""
    outcome: Optional[str] = None


class TaskResponse(BaseModel):
    """Schema for task response"""
    id: UUID
    title: str
    task_type: TaskType
    priority: TaskPriority
    status: TaskStatus
    assigned_to_id: Optional[UUID]
    due_date: Optional[datetime]
    progress_percent: int
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# PYDANTIC SCHEMAS - Campaign
# =============================================================================

class CampaignCreate(BaseModel):
    """Schema for creating a campaign"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

    campaign_type: CampaignType
    start_date: datetime
    end_date: Optional[datetime] = None

    budget: Optional[Decimal] = None
    currency: str = "EUR"

    target_audience: Optional[Dict[str, Any]] = None
    content_template: Optional[Dict[str, Any]] = None

    goal_leads: Optional[int] = None
    goal_conversions: Optional[int] = None
    goal_revenue: Optional[Decimal] = None

    tags: Optional[List[str]] = None


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CampaignStatus] = None

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    budget: Optional[Decimal] = None
    target_audience: Optional[Dict[str, Any]] = None
    content_template: Optional[Dict[str, Any]] = None

    goal_leads: Optional[int] = None
    goal_conversions: Optional[int] = None
    goal_revenue: Optional[Decimal] = None

    tags: Optional[List[str]] = None


class CampaignMetricsUpdate(BaseModel):
    """Schema for updating campaign metrics"""
    emails_sent: Optional[int] = None
    emails_opened: Optional[int] = None
    emails_clicked: Optional[int] = None
    leads_generated: Optional[int] = None
    conversions: Optional[int] = None
    revenue_generated: Optional[Decimal] = None


class CampaignResponse(BaseModel):
    """Schema for campaign response"""
    id: UUID
    name: str
    campaign_type: CampaignType
    status: CampaignStatus
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    budget: Optional[Decimal]
    leads_generated: int
    conversions: int
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# PYDANTIC SCHEMAS - Workflow
# =============================================================================

class WorkflowCreate(BaseModel):
    """Schema for creating a workflow"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

    trigger_type: WorkflowTrigger
    trigger_conditions: Optional[Dict[str, Any]] = None
    filter_conditions: Optional[Dict[str, Any]] = None

    actions: List[Dict[str, Any]]

    max_executions_per_record: int = 1
    cooldown_hours: int = 0

    tags: Optional[List[str]] = None


class WorkflowUpdate(BaseModel):
    """Schema for updating a workflow"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

    trigger_conditions: Optional[Dict[str, Any]] = None
    filter_conditions: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None

    max_executions_per_record: Optional[int] = None
    cooldown_hours: Optional[int] = None

    tags: Optional[List[str]] = None


class WorkflowResponse(BaseModel):
    """Schema for workflow response"""
    id: UUID
    name: str
    trigger_type: WorkflowTrigger
    is_active: bool
    execution_count: int
    successful_executions: int
    failed_executions: int
    last_executed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# PYDANTIC SCHEMAS - Integration
# =============================================================================

class IntegrationCreate(BaseModel):
    """Schema for creating an integration"""
    crm_type: ExternalCRMType
    integration_name: str = Field(..., min_length=1, max_length=255)

    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    instance_url: Optional[str] = None

    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None

    sync_direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    sync_interval_minutes: int = 60

    sync_leads: bool = True
    sync_contacts: bool = True
    sync_deals: bool = True

    field_mappings: Optional[Dict[str, Any]] = None


class IntegrationUpdate(BaseModel):
    """Schema for updating an integration"""
    integration_name: Optional[str] = None
    is_active: Optional[bool] = None

    sync_direction: Optional[SyncDirection] = None
    sync_interval_minutes: Optional[int] = None

    sync_leads: Optional[bool] = None
    sync_contacts: Optional[bool] = None
    sync_deals: Optional[bool] = None

    field_mappings: Optional[Dict[str, Any]] = None


class IntegrationResponse(BaseModel):
    """Schema for integration response"""
    id: UUID
    crm_type: ExternalCRMType
    integration_name: str
    is_active: bool
    sync_direction: SyncDirection
    last_sync_at: Optional[datetime]
    last_sync_status: Optional[str]
    total_records_synced: int
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# PYDANTIC SCHEMAS - Analytics
# =============================================================================

class PipelineSummary(BaseModel):
    """Schema for pipeline summary"""
    total_deals: int
    total_value: Decimal
    weighted_value: Decimal
    stages: Dict[str, Any]
    forecast: Dict[str, Decimal]
    average_deal_size: Decimal
    average_days_in_pipeline: int


class WinRateStats(BaseModel):
    """Schema for win rate statistics"""
    total_closed: int
    won_count: int
    lost_count: int
    win_rate: float
    won_value: Decimal
    lost_value: Decimal
    lost_reasons: Dict[str, int]


class CampaignAnalytics(BaseModel):
    """Schema for campaign analytics"""
    campaign_id: UUID
    name: str
    status: str
    email_metrics: Dict[str, Any]
    lead_metrics: Dict[str, Any]
    financial_metrics: Dict[str, Any]
    goals: Dict[str, Any]


class DashboardStats(BaseModel):
    """Schema for CRM dashboard statistics"""
    leads: Dict[str, Any]
    pipeline: Dict[str, Any]
    win_rate: Dict[str, Any]
    tasks: Dict[str, int]


# =============================================================================
# LEAD ENDPOINTS
# =============================================================================

@router.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead_data: LeadCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Create a new lead"""
    crm_service = get_crm_service(session)
    lead = await crm_service.create_lead(
        organization_name=lead_data.organization_name,
        contact_first_name=lead_data.contact_first_name,
        contact_last_name=lead_data.contact_last_name,
        contact_email=lead_data.contact_email,
        source=lead_data.source,
        created_by_id=current_user.id,
        **lead_data.model_dump(exclude={"organization_name", "contact_first_name", "contact_last_name", "contact_email", "source"})
    )
    return lead


@router.get("/leads", response_model=Dict[str, Any])
async def get_leads(
    status: Optional[LeadStatus] = None,
    source: Optional[LeadSource] = None,
    assigned_to: Optional[UUID] = None,
    min_score: Optional[int] = Query(None, ge=0, le=100),
    is_qualified: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get leads with filters and pagination"""
    crm_service = get_crm_service(session)
    leads, total = await crm_service.get_leads(
        status=status,
        source=source,
        assigned_to=assigned_to,
        min_score=min_score,
        is_qualified=is_qualified,
        limit=limit,
        offset=offset
    )
    return {
        "data": leads,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get a specific lead by ID"""
    from sqlalchemy import select
    result = await session.execute(select(CRMLead).where(CRMLead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: UUID,
    lead_data: LeadUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Update a lead"""
    from sqlalchemy import select
    result = await session.execute(select(CRMLead).where(CRMLead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    update_data = lead_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)

    lead.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(lead)
    return lead


@router.patch("/leads/{lead_id}/status", response_model=LeadResponse)
async def update_lead_status(
    lead_id: UUID,
    status_data: LeadStatusUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Update lead status"""
    crm_service = get_crm_service(session)
    lead = await crm_service.update_lead_status(
        lead_id=lead_id,
        new_status=status_data.status,
        notes=status_data.notes
    )
    return lead


@router.post("/leads/{lead_id}/convert")
async def convert_lead(
    lead_id: UUID,
    convert_data: LeadConvert,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Convert lead to customer and create deal"""
    crm_service = get_crm_service(session)
    lead, deal = await crm_service.convert_lead_to_customer(
        lead_id=lead_id,
        academy_id=convert_data.academy_id,
        deal_name=convert_data.deal_name,
        deal_amount=convert_data.deal_amount,
        owner_id=convert_data.owner_id
    )
    return {"lead": lead, "deal": deal}


@router.post("/leads/{lead_id}/lost", response_model=LeadResponse)
async def mark_lead_lost(
    lead_id: UUID,
    lost_data: LeadLost,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Mark lead as lost"""
    crm_service = get_crm_service(session)
    lead = await crm_service.mark_lead_lost(
        lead_id=lead_id,
        reason=lost_data.reason,
        details=lost_data.details,
        competitor=lost_data.competitor
    )
    return lead


@router.post("/leads/{lead_id}/score", response_model=LeadResponse)
async def recalculate_lead_score(
    lead_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Recalculate lead score"""
    scoring_service = LeadScoringService()
    lead = await scoring_service.update_lead_score(session, lead_id)
    return lead


@router.get("/leads/{lead_id}/score-breakdown")
async def get_lead_score_breakdown(
    lead_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get detailed lead score breakdown"""
    from sqlalchemy import select
    result = await session.execute(select(CRMLead).where(CRMLead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    scoring_service = LeadScoringService()
    total_score, breakdown = await scoring_service.calculate_score(lead)
    return {
        "lead_id": str(lead_id),
        "total_score": total_score,
        "breakdown": breakdown
    }


# =============================================================================
# CONTACT ENDPOINTS
# =============================================================================

@router.post("/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_data: ContactCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Create a new contact"""
    crm_service = get_crm_service(session)
    contact = await crm_service.create_contact(
        created_by_id=current_user.id,
        **contact_data.model_dump()
    )
    return contact


@router.get("/contacts", response_model=List[ContactResponse])
async def get_contacts(
    lead_id: Optional[UUID] = None,
    academy_id: Optional[UUID] = None,
    is_primary: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get contacts with filters"""
    from sqlalchemy import select
    query = select(CRMContact).where(CRMContact.is_deleted == False)

    if lead_id:
        query = query.where(CRMContact.lead_id == lead_id)
    if academy_id:
        query = query.where(CRMContact.academy_id == academy_id)
    if is_primary is not None:
        query = query.where(CRMContact.is_primary == is_primary)

    query = query.offset(offset).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get a specific contact"""
    from sqlalchemy import select
    result = await session.execute(select(CRMContact).where(CRMContact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.patch("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: UUID,
    contact_data: ContactUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Update a contact"""
    from sqlalchemy import select
    result = await session.execute(select(CRMContact).where(CRMContact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    update_data = contact_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)

    await session.commit()
    await session.refresh(contact)
    return contact


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Soft delete a contact"""
    from sqlalchemy import select
    result = await session.execute(select(CRMContact).where(CRMContact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    contact.is_deleted = True
    contact.deleted_at = datetime.utcnow()
    await session.commit()


# =============================================================================
# DEAL ENDPOINTS
# =============================================================================

@router.post("/deals", response_model=DealResponse, status_code=status.HTTP_201_CREATED)
async def create_deal(
    deal_data: DealCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Create a new deal"""
    crm_service = get_crm_service(session)
    deal = await crm_service.pipeline.create_deal(
        lead_id=deal_data.lead_id,
        academy_id=deal_data.academy_id,
        name=deal_data.name,
        amount=deal_data.amount,
        owner_id=deal_data.owner_id,
        expected_close_date=deal_data.expected_close_date,
        products=deal_data.products,
        description=deal_data.description,
        currency=deal_data.currency,
        recurring_revenue=deal_data.recurring_revenue,
        contract_length_months=deal_data.contract_length_months,
        tags=deal_data.tags
    )
    return deal


@router.get("/deals", response_model=Dict[str, Any])
async def get_deals(
    stage: Optional[DealStage] = None,
    owner_id: Optional[UUID] = None,
    lead_id: Optional[UUID] = None,
    academy_id: Optional[UUID] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get deals with filters"""
    from sqlalchemy import select, desc
    query = select(CRMDeal).where(CRMDeal.is_deleted == False)

    if stage:
        query = query.where(CRMDeal.stage == stage)
    if owner_id:
        query = query.where(CRMDeal.owner_id == owner_id)
    if lead_id:
        query = query.where(CRMDeal.lead_id == lead_id)
    if academy_id:
        query = query.where(CRMDeal.academy_id == academy_id)
    if min_amount:
        query = query.where(CRMDeal.amount >= min_amount)
    if max_amount:
        query = query.where(CRMDeal.amount <= max_amount)

    # Get total count
    from sqlalchemy import func
    count_result = await session.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    # Apply pagination
    query = query.order_by(desc(CRMDeal.created_at)).offset(offset).limit(limit)
    result = await session.execute(query)
    deals = result.scalars().all()

    return {"data": deals, "total": total, "limit": limit, "offset": offset}


@router.get("/deals/{deal_id}", response_model=DealResponse)
async def get_deal(
    deal_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get a specific deal"""
    from sqlalchemy import select
    result = await session.execute(select(CRMDeal).where(CRMDeal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.patch("/deals/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: UUID,
    deal_data: DealUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Update a deal"""
    from sqlalchemy import select
    result = await session.execute(select(CRMDeal).where(CRMDeal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    update_data = deal_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(deal, field, value)

    await session.commit()
    await session.refresh(deal)
    return deal


@router.patch("/deals/{deal_id}/stage", response_model=DealResponse)
async def update_deal_stage(
    deal_id: UUID,
    stage_data: DealStageUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Update deal stage"""
    crm_service = get_crm_service(session)
    deal = await crm_service.pipeline.update_stage(
        deal_id=deal_id,
        new_stage=stage_data.stage,
        notes=stage_data.notes,
        won_reason=stage_data.won_reason,
        lost_reason=stage_data.lost_reason,
        competitor=stage_data.competitor
    )
    return deal


@router.get("/deals/pipeline/summary", response_model=PipelineSummary)
async def get_pipeline_summary(
    academy_id: Optional[UUID] = None,
    owner_id: Optional[UUID] = None,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get pipeline summary"""
    crm_service = get_crm_service(session)
    summary = await crm_service.pipeline.get_pipeline_summary(
        academy_id=academy_id,
        owner_id=owner_id
    )
    return summary


@router.get("/deals/pipeline/stale", response_model=List[DealResponse])
async def get_stale_deals(
    days_threshold: int = Query(14, ge=1),
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get deals that have been stale"""
    crm_service = get_crm_service(session)
    deals = await crm_service.pipeline.get_stale_deals(days_threshold)
    return deals


@router.get("/deals/stats/win-rate", response_model=WinRateStats)
async def get_win_rate_stats(
    owner_id: Optional[UUID] = None,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get win rate statistics"""
    crm_service = get_crm_service(session)
    stats = await crm_service.pipeline.calculate_win_rate(owner_id=owner_id)
    return stats


# =============================================================================
# COMMUNICATION ENDPOINTS
# =============================================================================

@router.post("/communications", response_model=CommunicationResponse, status_code=status.HTTP_201_CREATED)
async def log_communication(
    comm_data: CommunicationCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Log a communication"""
    crm_service = get_crm_service(session)
    communication = await crm_service.log_communication(
        user_id=current_user.id,
        **comm_data.model_dump()
    )
    return communication


@router.get("/communications", response_model=List[CommunicationResponse])
async def get_communications(
    lead_id: Optional[UUID] = None,
    academy_id: Optional[UUID] = None,
    deal_id: Optional[UUID] = None,
    comm_type: Optional[CommunicationType] = None,
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get communication history"""
    crm_service = get_crm_service(session)
    communications = await crm_service.get_communication_history(
        lead_id=lead_id,
        academy_id=academy_id,
        deal_id=deal_id,
        limit=limit
    )
    return communications


@router.get("/communications/{comm_id}", response_model=CommunicationResponse)
async def get_communication(
    comm_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get a specific communication"""
    from sqlalchemy import select
    result = await session.execute(select(CRMCommunication).where(CRMCommunication.id == comm_id))
    comm = result.scalar_one_or_none()
    if not comm:
        raise HTTPException(status_code=404, detail="Communication not found")
    return comm


# =============================================================================
# TASK ENDPOINTS
# =============================================================================

@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Create a new task"""
    crm_service = get_crm_service(session)
    task = await crm_service.create_task(
        created_by_id=current_user.id,
        **task_data.model_dump()
    )
    return task


@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    lead_id: Optional[UUID] = None,
    deal_id: Optional[UUID] = None,
    assigned_to_id: Optional[UUID] = None,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    due_before: Optional[datetime] = None,
    due_after: Optional[datetime] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get tasks with filters"""
    from sqlalchemy import select, asc
    query = select(CRMTask).where(CRMTask.is_deleted == False)

    if lead_id:
        query = query.where(CRMTask.lead_id == lead_id)
    if deal_id:
        query = query.where(CRMTask.deal_id == deal_id)
    if assigned_to_id:
        query = query.where(CRMTask.assigned_to_id == assigned_to_id)
    if status:
        query = query.where(CRMTask.status == status)
    if priority:
        query = query.where(CRMTask.priority == priority)
    if due_before:
        query = query.where(CRMTask.due_date <= due_before)
    if due_after:
        query = query.where(CRMTask.due_date >= due_after)

    query = query.order_by(asc(CRMTask.due_date)).offset(offset).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/tasks/overdue", response_model=List[TaskResponse])
async def get_overdue_tasks(
    assigned_to_id: Optional[UUID] = None,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get overdue tasks"""
    crm_service = get_crm_service(session)
    tasks = await crm_service.get_overdue_tasks(assigned_to_id)
    return tasks


@router.get("/tasks/due-today", response_model=List[TaskResponse])
async def get_tasks_due_today(
    assigned_to_id: Optional[UUID] = None,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get tasks due today"""
    crm_service = get_crm_service(session)
    tasks = await crm_service.get_tasks_due_today(assigned_to_id)
    return tasks


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get a specific task"""
    from sqlalchemy import select
    result = await session.execute(select(CRMTask).where(CRMTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Update a task"""
    from sqlalchemy import select
    result = await session.execute(select(CRMTask).where(CRMTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    await session.commit()
    await session.refresh(task)
    return task


@router.post("/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: UUID,
    complete_data: TaskComplete,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Complete a task"""
    crm_service = get_crm_service(session)
    task = await crm_service.complete_task(task_id, complete_data.outcome)
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Soft delete a task"""
    from sqlalchemy import select
    result = await session.execute(select(CRMTask).where(CRMTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_deleted = True
    task.deleted_at = datetime.utcnow()
    await session.commit()


# =============================================================================
# CAMPAIGN ENDPOINTS
# =============================================================================

@router.post("/campaigns", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Create a new campaign"""
    crm_service = get_crm_service(session)
    campaign = await crm_service.campaigns.create_campaign(
        owner_id=current_user.id,
        **campaign_data.model_dump()
    )
    return campaign


@router.get("/campaigns", response_model=List[CampaignResponse])
async def get_campaigns(
    status: Optional[CampaignStatus] = None,
    campaign_type: Optional[CampaignType] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get campaigns with filters"""
    from sqlalchemy import select, desc
    query = select(CRMCampaign).where(CRMCampaign.is_deleted == False)

    if status:
        query = query.where(CRMCampaign.status == status)
    if campaign_type:
        query = query.where(CRMCampaign.campaign_type == campaign_type)

    query = query.order_by(desc(CRMCampaign.created_at)).offset(offset).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get a specific campaign"""
    from sqlalchemy import select
    result = await session.execute(select(CRMCampaign).where(CRMCampaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.patch("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: UUID,
    campaign_data: CampaignUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Update a campaign"""
    from sqlalchemy import select
    result = await session.execute(select(CRMCampaign).where(CRMCampaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    update_data = campaign_data.model_dump(exclude_unset=True)

    # Handle status update separately
    if "status" in update_data:
        crm_service = get_crm_service(session)
        campaign = await crm_service.campaigns.update_campaign_status(
            campaign_id, update_data.pop("status")
        )

    for field, value in update_data.items():
        setattr(campaign, field, value)

    await session.commit()
    await session.refresh(campaign)
    return campaign


@router.post("/campaigns/{campaign_id}/metrics", response_model=CampaignResponse)
async def update_campaign_metrics(
    campaign_id: UUID,
    metrics: CampaignMetricsUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Update campaign metrics"""
    crm_service = get_crm_service(session)
    campaign = await crm_service.campaigns.record_campaign_metrics(
        campaign_id,
        metrics.model_dump(exclude_unset=True)
    )
    return campaign


@router.get("/campaigns/{campaign_id}/analytics", response_model=CampaignAnalytics)
async def get_campaign_analytics(
    campaign_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get detailed campaign analytics"""
    crm_service = get_crm_service(session)
    analytics = await crm_service.campaigns.get_campaign_analytics(campaign_id)
    return analytics


@router.get("/campaigns/best-performing", response_model=List[CampaignResponse])
async def get_best_performing_campaigns(
    metric: str = Query("leads", regex="^(leads|conversions|revenue)$"),
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get best performing campaigns"""
    crm_service = get_crm_service(session)
    campaigns = await crm_service.campaigns.get_best_performing_campaigns(limit, metric)
    return campaigns


# =============================================================================
# WORKFLOW ENDPOINTS
# =============================================================================

@router.post("/workflows", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow_data: WorkflowCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Create a new workflow"""
    workflow = CRMWorkflow(
        created_by_id=current_user.id,
        **workflow_data.model_dump()
    )
    session.add(workflow)
    await session.commit()
    await session.refresh(workflow)
    return workflow


@router.get("/workflows", response_model=List[WorkflowResponse])
async def get_workflows(
    is_active: Optional[bool] = None,
    trigger_type: Optional[WorkflowTrigger] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get workflows with filters"""
    from sqlalchemy import select, desc
    query = select(CRMWorkflow).where(CRMWorkflow.is_deleted == False)

    if is_active is not None:
        query = query.where(CRMWorkflow.is_active == is_active)
    if trigger_type:
        query = query.where(CRMWorkflow.trigger_type == trigger_type)

    query = query.order_by(desc(CRMWorkflow.created_at)).offset(offset).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get a specific workflow"""
    from sqlalchemy import select
    result = await session.execute(select(CRMWorkflow).where(CRMWorkflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.patch("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: UUID,
    workflow_data: WorkflowUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Update a workflow"""
    from sqlalchemy import select
    result = await session.execute(select(CRMWorkflow).where(CRMWorkflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    update_data = workflow_data.model_dump(exclude_unset=True)

    # Handle activation/deactivation
    if "is_active" in update_data:
        if update_data["is_active"]:
            workflow.activate()
        else:
            workflow.deactivate()
        del update_data["is_active"]

    for field, value in update_data.items():
        setattr(workflow, field, value)

    workflow.version += 1
    await session.commit()
    await session.refresh(workflow)
    return workflow


@router.post("/workflows/{workflow_id}/activate", response_model=WorkflowResponse)
async def activate_workflow(
    workflow_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Activate a workflow"""
    from sqlalchemy import select
    result = await session.execute(select(CRMWorkflow).where(CRMWorkflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow.activate()
    await session.commit()
    await session.refresh(workflow)
    return workflow


@router.post("/workflows/{workflow_id}/deactivate", response_model=WorkflowResponse)
async def deactivate_workflow(
    workflow_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Deactivate a workflow"""
    from sqlalchemy import select
    result = await session.execute(select(CRMWorkflow).where(CRMWorkflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow.deactivate()
    await session.commit()
    await session.refresh(workflow)
    return workflow


@router.delete("/workflows/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Soft delete a workflow"""
    from sqlalchemy import select
    result = await session.execute(select(CRMWorkflow).where(CRMWorkflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow.is_deleted = True
    workflow.deleted_at = datetime.utcnow()
    workflow.is_active = False
    await session.commit()


# =============================================================================
# EXTERNAL INTEGRATION ENDPOINTS
# =============================================================================

@router.post("/integrations/{academy_id}", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    academy_id: UUID,
    integration_data: IntegrationCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Create a new external CRM integration"""
    integration_service = ExternalCRMService(session)
    integration = await integration_service.create_integration(
        academy_id=academy_id,
        **integration_data.model_dump()
    )
    return integration


@router.get("/integrations/{academy_id}", response_model=List[IntegrationResponse])
async def get_integrations(
    academy_id: UUID,
    is_active: Optional[bool] = None,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get integrations for an academy"""
    from sqlalchemy import select
    query = select(ExternalCRMIntegration).where(
        ExternalCRMIntegration.academy_id == academy_id,
        ExternalCRMIntegration.is_deleted == False
    )

    if is_active is not None:
        query = query.where(ExternalCRMIntegration.is_active == is_active)

    result = await session.execute(query)
    return result.scalars().all()


@router.get("/integrations/{academy_id}/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    academy_id: UUID,
    integration_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get a specific integration"""
    from sqlalchemy import select
    result = await session.execute(
        select(ExternalCRMIntegration).where(
            ExternalCRMIntegration.id == integration_id,
            ExternalCRMIntegration.academy_id == academy_id
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.patch("/integrations/{academy_id}/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    academy_id: UUID,
    integration_id: UUID,
    integration_data: IntegrationUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Update an integration"""
    from sqlalchemy import select
    result = await session.execute(
        select(ExternalCRMIntegration).where(
            ExternalCRMIntegration.id == integration_id,
            ExternalCRMIntegration.academy_id == academy_id
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    update_data = integration_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(integration, field, value)

    await session.commit()
    await session.refresh(integration)
    return integration


@router.get("/integrations/{academy_id}/{integration_id}/oauth-url")
async def get_oauth_url(
    academy_id: UUID,
    integration_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get OAuth URL for an integration"""
    integration_service = ExternalCRMService(session)
    url = await integration_service.get_oauth_url(integration_id)
    if not url:
        raise HTTPException(status_code=400, detail="OAuth not supported for this integration type")
    return {"oauth_url": url}


@router.post("/integrations/{academy_id}/{integration_id}/oauth-callback")
async def complete_oauth(
    academy_id: UUID,
    integration_id: UUID,
    code: str = Query(...),
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Complete OAuth flow with authorization code"""
    integration_service = ExternalCRMService(session)
    success = await integration_service.complete_oauth(integration_id, code)
    if not success:
        raise HTTPException(status_code=400, detail="OAuth authentication failed")
    return {"status": "authenticated"}


@router.post("/integrations/{academy_id}/{integration_id}/sync")
async def trigger_sync(
    academy_id: UUID,
    integration_id: UUID,
    background_tasks: BackgroundTasks,
    full_sync: bool = Query(False),
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Trigger sync for an integration"""
    integration_service = ExternalCRMService(session)

    # Run sync in background
    async def run_sync():
        logs = await integration_service.trigger_sync(integration_id, full_sync)
        return logs

    background_tasks.add_task(run_sync)
    return {"status": "sync_started", "integration_id": str(integration_id)}


@router.post("/integrations/{academy_id}/{integration_id}/test")
async def test_connection(
    academy_id: UUID,
    integration_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Test connection to external CRM"""
    integration_service = ExternalCRMService(session)
    result = await integration_service.test_connection(integration_id)
    return result


@router.delete("/integrations/{academy_id}/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    academy_id: UUID,
    integration_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Soft delete an integration"""
    from sqlalchemy import select
    result = await session.execute(
        select(ExternalCRMIntegration).where(
            ExternalCRMIntegration.id == integration_id,
            ExternalCRMIntegration.academy_id == academy_id
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    integration.is_deleted = True
    integration.deleted_at = datetime.utcnow()
    integration.is_active = False
    await session.commit()


# =============================================================================
# ANALYTICS/DASHBOARD ENDPOINTS
# =============================================================================

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    academy_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get CRM dashboard statistics"""
    date_range = None
    if start_date and end_date:
        date_range = (start_date, end_date)

    crm_service = get_crm_service(session)
    stats = await crm_service.get_crm_dashboard_stats(
        academy_id=academy_id,
        date_range=date_range
    )
    return stats


@router.get("/analytics/lead-sources")
async def get_lead_source_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get lead source analytics"""
    from sqlalchemy import select, func
    query = select(
        CRMLead.source,
        func.count(CRMLead.id).label("count"),
        func.avg(CRMLead.lead_score).label("avg_score")
    ).where(CRMLead.is_deleted == False)

    if start_date:
        query = query.where(CRMLead.created_at >= start_date)
    if end_date:
        query = query.where(CRMLead.created_at <= end_date)

    query = query.group_by(CRMLead.source)
    result = await session.execute(query)

    analytics = []
    for row in result.all():
        analytics.append({
            "source": row.source.value,
            "count": row.count,
            "avg_score": float(row.avg_score) if row.avg_score else 0
        })

    return {"data": analytics}


@router.get("/analytics/conversion-funnel")
async def get_conversion_funnel(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get conversion funnel analytics"""
    from sqlalchemy import select, func
    query = select(
        CRMLead.status,
        func.count(CRMLead.id).label("count")
    ).where(CRMLead.is_deleted == False)

    if start_date:
        query = query.where(CRMLead.created_at >= start_date)
    if end_date:
        query = query.where(CRMLead.created_at <= end_date)

    query = query.group_by(CRMLead.status)
    result = await session.execute(query)

    funnel = {}
    for row in result.all():
        funnel[row.status.value] = row.count

    # Calculate conversion rates
    total_leads = sum(funnel.values())
    funnel_with_rates = {
        "stages": funnel,
        "total_leads": total_leads,
        "conversion_rates": {}
    }

    if total_leads > 0:
        funnel_with_rates["conversion_rates"]["qualified"] = (funnel.get("qualified", 0) + funnel.get("converted", 0)) / total_leads * 100
        funnel_with_rates["conversion_rates"]["converted"] = funnel.get("converted", 0) / total_leads * 100

    return funnel_with_rates


@router.get("/analytics/activity-summary")
async def get_activity_summary(
    user_id: Optional[UUID] = None,
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user)
):
    """Get activity summary for users"""
    from sqlalchemy import select, func
    from datetime import timedelta

    start_date = datetime.utcnow() - timedelta(days=days)

    # Communications by type
    comm_query = select(
        CRMCommunication.comm_type,
        func.count(CRMCommunication.id).label("count")
    ).where(
        CRMCommunication.created_at >= start_date,
        CRMCommunication.is_deleted == False
    )

    if user_id:
        comm_query = comm_query.where(CRMCommunication.user_id == user_id)

    comm_query = comm_query.group_by(CRMCommunication.comm_type)
    comm_result = await session.execute(comm_query)

    communications = {}
    for row in comm_result.all():
        communications[row.comm_type.value] = row.count

    # Tasks completed
    task_query = select(func.count(CRMTask.id)).where(
        CRMTask.completed_at >= start_date,
        CRMTask.status == TaskStatus.COMPLETED,
        CRMTask.is_deleted == False
    )

    if user_id:
        task_query = task_query.where(CRMTask.assigned_to_id == user_id)

    task_result = await session.execute(task_query)
    tasks_completed = task_result.scalar()

    return {
        "period_days": days,
        "communications": communications,
        "total_communications": sum(communications.values()),
        "tasks_completed": tasks_completed
    }
