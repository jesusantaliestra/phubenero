"""
ProficientHub - CRM Service
Business logic for CRM operations including lead scoring, deal pipeline,
workflow automation, and campaign management.
"""

import asyncio
import hashlib
import hmac
import json
import structlog
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional, Any, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, update, delete, func, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models_crm import (
    CRMLead, CRMContact, CRMDeal, CRMCommunication, CRMTask,
    CRMCampaign, CRMWorkflow, WorkflowExecutionLog, ExternalCRMIntegration,
    CRMSyncLog, CRMEmailTemplate, CRMNote,
    LeadSource, LeadStatus, LeadOrganizationType,
    ContactType, DealStage, DealPriority,
    CommunicationType, CommunicationDirection,
    TaskType, TaskPriority, TaskStatus,
    CampaignType, CampaignStatus,
    WorkflowTrigger, WorkflowActionType,
    SyncDirection, SyncStatus
)

logger = structlog.get_logger(__name__)


# =============================================================================
# LEAD SCORING SERVICE
# =============================================================================

class LeadScoringService:
    """
    Lead scoring algorithm that evaluates leads based on multiple factors.
    Scores range from 0-100 with detailed breakdown.
    """

    # Scoring weights
    WEIGHTS = {
        "fit": 30,          # How well the lead matches ideal customer profile
        "engagement": 30,   # How engaged the lead is with our content
        "behavior": 25,     # Actions taken by the lead
        "timing": 15        # Urgency and recency factors
    }

    # Fit score factors
    FIT_FACTORS = {
        "organization_type": {
            LeadOrganizationType.LANGUAGE_SCHOOL: 10,
            LeadOrganizationType.TEST_PREP_CENTER: 10,
            LeadOrganizationType.UNIVERSITY: 8,
            LeadOrganizationType.HIGH_SCHOOL: 6,
            LeadOrganizationType.CORPORATE: 7,
            LeadOrganizationType.ONLINE_PLATFORM: 8,
            LeadOrganizationType.INDIVIDUAL_TEACHER: 3,
            LeadOrganizationType.GOVERNMENT: 5,
            LeadOrganizationType.NONPROFIT: 4,
            LeadOrganizationType.OTHER: 2
        },
        "student_count_tiers": [
            (500, 15),   # 500+ students = 15 points
            (250, 12),   # 250-499 = 12 points
            (100, 10),   # 100-249 = 10 points
            (50, 7),     # 50-99 = 7 points
            (20, 5),     # 20-49 = 5 points
            (1, 3)       # 1-19 = 3 points
        ],
        "budget_confirmed": 5,
        "multiple_exams_interest": 3
    }

    # Engagement score factors
    ENGAGEMENT_FACTORS = {
        "email_opened": 2,      # Per email opened (max 10)
        "email_clicked": 3,     # Per email clicked (max 9)
        "website_visit": 1,     # Per visit (max 5)
        "content_download": 3,  # Per download (max 9)
        "meeting_attended": 7,  # Per meeting (max 14)
        "demo_attended": 10     # Demo attendance
    }

    # Behavior score factors
    BEHAVIOR_FACTORS = {
        "status_progression": {
            LeadStatus.NEW: 0,
            LeadStatus.CONTACTED: 3,
            LeadStatus.ENGAGED: 6,
            LeadStatus.QUALIFIED: 10,
            LeadStatus.DEMO_SCHEDULED: 12,
            LeadStatus.DEMO_COMPLETED: 15,
            LeadStatus.PROPOSAL_SENT: 18,
            LeadStatus.NEGOTIATION: 20
        },
        "call_participation": 3,     # Per call (max 9)
        "responded_quickly": 5,      # Responded within 24h
        "referred_others": 8         # Made referrals
    }

    # Timing score factors
    TIMING_FACTORS = {
        "urgency_levels": {
            "immediate": 15,
            "1_week": 12,
            "1_month": 10,
            "3_months": 6,
            "6_months": 3,
            "no_timeline": 0
        },
        "recency_bonus": {
            7: 10,    # Contact within 7 days = 10 points
            14: 7,    # Within 14 days = 7 points
            30: 4,    # Within 30 days = 4 points
            60: 1     # Within 60 days = 1 point
        }
    }

    async def calculate_score(
        self,
        lead: CRMLead,
        session: Optional[AsyncSession] = None
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Calculate lead score with detailed breakdown.

        Args:
            lead: The lead to score
            session: Optional database session for additional queries

        Returns:
            Tuple of (total_score, breakdown_dict)
        """
        breakdown = {
            "fit": self._calculate_fit_score(lead),
            "engagement": self._calculate_engagement_score(lead),
            "behavior": self._calculate_behavior_score(lead),
            "timing": self._calculate_timing_score(lead)
        }

        # Normalize scores to their weight limits
        breakdown["fit"]["normalized"] = min(
            self.WEIGHTS["fit"],
            int(breakdown["fit"]["raw"] * self.WEIGHTS["fit"] / 30)
        )
        breakdown["engagement"]["normalized"] = min(
            self.WEIGHTS["engagement"],
            int(breakdown["engagement"]["raw"] * self.WEIGHTS["engagement"] / 30)
        )
        breakdown["behavior"]["normalized"] = min(
            self.WEIGHTS["behavior"],
            int(breakdown["behavior"]["raw"] * self.WEIGHTS["behavior"] / 25)
        )
        breakdown["timing"]["normalized"] = min(
            self.WEIGHTS["timing"],
            int(breakdown["timing"]["raw"] * self.WEIGHTS["timing"] / 25)
        )

        total_score = sum(cat["normalized"] for cat in breakdown.values())
        total_score = min(100, max(0, total_score))

        return total_score, breakdown

    def _calculate_fit_score(self, lead: CRMLead) -> Dict[str, Any]:
        """Calculate fit score component"""
        score = 0
        factors = {}

        # Organization type
        org_score = self.FIT_FACTORS["organization_type"].get(
            lead.organization_type, 0
        )
        score += org_score
        factors["organization_type"] = org_score

        # Student count
        student_score = 0
        if lead.estimated_students:
            for threshold, points in self.FIT_FACTORS["student_count_tiers"]:
                if lead.estimated_students >= threshold:
                    student_score = points
                    break
        score += student_score
        factors["estimated_students"] = student_score

        # Budget confirmed
        if lead.budget_confirmed:
            score += self.FIT_FACTORS["budget_confirmed"]
            factors["budget_confirmed"] = self.FIT_FACTORS["budget_confirmed"]

        # Multiple exams interest
        if lead.interested_exams and len(lead.interested_exams) > 1:
            score += self.FIT_FACTORS["multiple_exams_interest"]
            factors["multiple_exams"] = self.FIT_FACTORS["multiple_exams_interest"]

        return {"raw": score, "factors": factors}

    def _calculate_engagement_score(self, lead: CRMLead) -> Dict[str, Any]:
        """Calculate engagement score component"""
        score = 0
        factors = {}

        # Email engagement
        email_open_score = min(10, lead.total_emails_opened * self.ENGAGEMENT_FACTORS["email_opened"])
        score += email_open_score
        factors["emails_opened"] = email_open_score

        # Website visits
        visit_score = min(5, lead.website_visits * self.ENGAGEMENT_FACTORS["website_visit"])
        score += visit_score
        factors["website_visits"] = visit_score

        # Content downloads
        download_score = min(9, lead.content_downloads * self.ENGAGEMENT_FACTORS["content_download"])
        score += download_score
        factors["content_downloads"] = download_score

        # Meetings
        meeting_score = min(14, lead.total_meetings * self.ENGAGEMENT_FACTORS["meeting_attended"])
        score += meeting_score
        factors["meetings"] = meeting_score

        return {"raw": score, "factors": factors}

    def _calculate_behavior_score(self, lead: CRMLead) -> Dict[str, Any]:
        """Calculate behavior score component"""
        score = 0
        factors = {}

        # Status progression
        status_score = self.BEHAVIOR_FACTORS["status_progression"].get(lead.status, 0)
        score += status_score
        factors["status_progression"] = status_score

        # Call participation
        call_score = min(9, lead.total_calls * self.BEHAVIOR_FACTORS["call_participation"])
        score += call_score
        factors["calls"] = call_score

        return {"raw": score, "factors": factors}

    def _calculate_timing_score(self, lead: CRMLead) -> Dict[str, Any]:
        """Calculate timing score component"""
        score = 0
        factors = {}

        # Urgency
        urgency_score = self.TIMING_FACTORS["urgency_levels"].get(
            lead.timeline_urgency, 0
        )
        score += urgency_score
        factors["urgency"] = urgency_score

        # Recency of contact
        days_since_contact = lead.days_since_last_contact
        recency_score = 0
        if days_since_contact is not None:
            for days, points in sorted(self.TIMING_FACTORS["recency_bonus"].items()):
                if days_since_contact <= days:
                    recency_score = points
                    break
        score += recency_score
        factors["recency"] = recency_score

        return {"raw": score, "factors": factors}

    async def update_lead_score(
        self,
        session: AsyncSession,
        lead_id: UUID
    ) -> CRMLead:
        """
        Update lead score in database.

        Args:
            session: Database session
            lead_id: Lead ID to update

        Returns:
            Updated lead
        """
        result = await session.execute(
            select(CRMLead).where(CRMLead.id == lead_id)
        )
        lead = result.scalar_one_or_none()

        if not lead:
            raise ValueError(f"Lead {lead_id} not found")

        total_score, breakdown = await self.calculate_score(lead)

        lead.lead_score = total_score
        lead.score_breakdown = breakdown
        lead.fit_score = breakdown["fit"]["normalized"]
        lead.engagement_score = breakdown["engagement"]["normalized"]
        lead.behavior_score = breakdown["behavior"]["normalized"]

        # Auto-qualify if score exceeds threshold
        if total_score >= 70 and not lead.is_qualified:
            lead.is_qualified = True
            lead.qualification_date = datetime.utcnow()

        await session.commit()
        await session.refresh(lead)

        logger.info(
            "lead_score_updated",
            lead_id=str(lead_id),
            score=total_score,
            is_qualified=lead.is_qualified
        )

        return lead

    async def batch_update_scores(
        self,
        session: AsyncSession,
        lead_ids: Optional[List[UUID]] = None
    ) -> int:
        """
        Batch update scores for multiple leads.

        Args:
            session: Database session
            lead_ids: Optional list of specific leads, or all if None

        Returns:
            Number of leads updated
        """
        query = select(CRMLead).where(CRMLead.is_deleted == False)
        if lead_ids:
            query = query.where(CRMLead.id.in_(lead_ids))

        result = await session.execute(query)
        leads = result.scalars().all()

        updated_count = 0
        for lead in leads:
            total_score, breakdown = await self.calculate_score(lead)
            lead.lead_score = total_score
            lead.score_breakdown = breakdown
            lead.fit_score = breakdown["fit"]["normalized"]
            lead.engagement_score = breakdown["engagement"]["normalized"]
            lead.behavior_score = breakdown["behavior"]["normalized"]

            if total_score >= 70 and not lead.is_qualified:
                lead.is_qualified = True
                lead.qualification_date = datetime.utcnow()

            updated_count += 1

        await session.commit()

        logger.info("batch_score_update_completed", updated_count=updated_count)
        return updated_count


# =============================================================================
# DEAL PIPELINE SERVICE
# =============================================================================

class DealPipelineService:
    """
    Deal pipeline management with stage tracking and probability calculations.
    """

    # Default stage probabilities
    STAGE_PROBABILITIES = {
        DealStage.QUALIFICATION: 10,
        DealStage.NEEDS_ANALYSIS: 20,
        DealStage.PROPOSAL: 50,
        DealStage.NEGOTIATION: 75,
        DealStage.CLOSED_WON: 100,
        DealStage.CLOSED_LOST: 0,
        DealStage.ON_HOLD: None,  # Keep current probability
        DealStage.RENEWAL: 80
    }

    # Average days expected in each stage
    EXPECTED_STAGE_DURATION = {
        DealStage.QUALIFICATION: 7,
        DealStage.NEEDS_ANALYSIS: 14,
        DealStage.PROPOSAL: 10,
        DealStage.NEGOTIATION: 14,
        DealStage.ON_HOLD: 30,
        DealStage.RENEWAL: 30
    }

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_deal(
        self,
        lead_id: Optional[UUID],
        academy_id: Optional[UUID],
        name: str,
        amount: Decimal,
        owner_id: UUID,
        expected_close_date: Optional[datetime] = None,
        products: Optional[List[Dict]] = None,
        **kwargs
    ) -> CRMDeal:
        """
        Create a new deal in the pipeline.

        Args:
            lead_id: Associated lead ID
            academy_id: Associated academy ID (for existing customers)
            name: Deal name
            amount: Deal amount
            owner_id: Sales rep owner
            expected_close_date: Expected close date
            products: List of products/services
            **kwargs: Additional deal attributes

        Returns:
            Created deal
        """
        deal = CRMDeal(
            lead_id=lead_id,
            academy_id=academy_id,
            name=name,
            amount=amount,
            owner_id=owner_id,
            expected_close_date=expected_close_date,
            products=products or [],
            stage=DealStage.QUALIFICATION,
            probability=self.STAGE_PROBABILITIES[DealStage.QUALIFICATION],
            stage_entered_at=datetime.utcnow(),
            stage_history=[{
                "stage": DealStage.QUALIFICATION.value,
                "entered_at": datetime.utcnow().isoformat(),
                "exited_at": None,
                "duration_hours": None
            }],
            **kwargs
        )

        # Generate deal number
        deal.deal_number = await self._generate_deal_number()

        # Calculate weighted amount
        deal.weighted_amount = amount * Decimal(deal.probability) / Decimal(100)

        self.session.add(deal)
        await self.session.commit()
        await self.session.refresh(deal)

        logger.info(
            "deal_created",
            deal_id=str(deal.id),
            deal_number=deal.deal_number,
            amount=str(amount)
        )

        return deal

    async def _generate_deal_number(self) -> str:
        """Generate unique deal number"""
        year = datetime.utcnow().year
        result = await self.session.execute(
            select(func.count(CRMDeal.id)).where(
                func.extract('year', CRMDeal.created_at) == year
            )
        )
        count = result.scalar() + 1
        return f"DEAL-{year}-{count:05d}"

    async def update_stage(
        self,
        deal_id: UUID,
        new_stage: DealStage,
        notes: Optional[str] = None,
        won_reason: Optional[str] = None,
        lost_reason: Optional[str] = None,
        competitor: Optional[str] = None
    ) -> CRMDeal:
        """
        Update deal stage with history tracking.

        Args:
            deal_id: Deal ID
            new_stage: New pipeline stage
            notes: Optional stage change notes
            won_reason: Reason for winning (if CLOSED_WON)
            lost_reason: Reason for losing (if CLOSED_LOST)
            competitor: Competitor that won (if CLOSED_LOST)

        Returns:
            Updated deal
        """
        result = await self.session.execute(
            select(CRMDeal).where(CRMDeal.id == deal_id)
        )
        deal = result.scalar_one_or_none()

        if not deal:
            raise ValueError(f"Deal {deal_id} not found")

        old_stage = deal.stage
        now = datetime.utcnow()

        # Update stage history
        if deal.stage_history and deal.stage_entered_at:
            duration = (now - deal.stage_entered_at.replace(tzinfo=None)).total_seconds() / 3600
            deal.stage_history[-1]["exited_at"] = now.isoformat()
            deal.stage_history[-1]["duration_hours"] = round(duration, 2)
            if notes:
                deal.stage_history[-1]["notes"] = notes

        # Add new stage entry
        if not deal.stage_history:
            deal.stage_history = []

        deal.stage_history.append({
            "stage": new_stage.value,
            "entered_at": now.isoformat(),
            "exited_at": None,
            "duration_hours": None
        })

        # Update deal
        deal.stage = new_stage
        deal.stage_entered_at = now
        deal.days_in_stage = 0
        deal.next_step = notes

        # Update probability
        new_probability = self.STAGE_PROBABILITIES.get(new_stage)
        if new_probability is not None:
            deal.probability = new_probability

        # Calculate weighted amount
        if deal.amount:
            deal.weighted_amount = deal.amount * Decimal(deal.probability) / Decimal(100)

        # Handle closed stages
        if new_stage == DealStage.CLOSED_WON:
            deal.actual_close_date = now.date()
            deal.won_reason = won_reason
        elif new_stage == DealStage.CLOSED_LOST:
            deal.actual_close_date = now.date()
            deal.lost_reason = lost_reason
            deal.lost_reason_details = notes
            deal.competitor = competitor

        await self.session.commit()
        await self.session.refresh(deal)

        logger.info(
            "deal_stage_updated",
            deal_id=str(deal_id),
            old_stage=old_stage.value,
            new_stage=new_stage.value
        )

        return deal

    async def get_pipeline_summary(
        self,
        academy_id: Optional[UUID] = None,
        owner_id: Optional[UUID] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Get pipeline summary with stage breakdown and forecasting.

        Args:
            academy_id: Optional filter by academy
            owner_id: Optional filter by owner
            date_range: Optional date range filter

        Returns:
            Pipeline summary dictionary
        """
        # Base query for open deals
        query = select(CRMDeal).where(
            CRMDeal.is_deleted == False,
            CRMDeal.stage.not_in([DealStage.CLOSED_WON, DealStage.CLOSED_LOST])
        )

        if academy_id:
            query = query.where(CRMDeal.academy_id == academy_id)
        if owner_id:
            query = query.where(CRMDeal.owner_id == owner_id)
        if date_range:
            query = query.where(
                CRMDeal.created_at.between(date_range[0], date_range[1])
            )

        result = await self.session.execute(query)
        deals = result.scalars().all()

        # Calculate summary
        summary = {
            "total_deals": len(deals),
            "total_value": Decimal("0"),
            "weighted_value": Decimal("0"),
            "stages": {},
            "forecast": {
                "pipeline": Decimal("0"),
                "best_case": Decimal("0"),
                "commit": Decimal("0")
            },
            "average_deal_size": Decimal("0"),
            "average_days_in_pipeline": 0
        }

        for stage in DealStage:
            if stage not in [DealStage.CLOSED_WON, DealStage.CLOSED_LOST]:
                summary["stages"][stage.value] = {
                    "count": 0,
                    "value": Decimal("0"),
                    "weighted_value": Decimal("0")
                }

        total_days = 0
        for deal in deals:
            if deal.amount:
                summary["total_value"] += deal.amount
                summary["weighted_value"] += deal.weighted_amount or Decimal("0")

                if deal.stage.value in summary["stages"]:
                    summary["stages"][deal.stage.value]["count"] += 1
                    summary["stages"][deal.stage.value]["value"] += deal.amount
                    summary["stages"][deal.stage.value]["weighted_value"] += deal.weighted_amount or Decimal("0")

                # Forecasting
                if deal.probability >= 90:
                    summary["forecast"]["commit"] += deal.amount
                elif deal.probability >= 50:
                    summary["forecast"]["best_case"] += deal.amount
                summary["forecast"]["pipeline"] += deal.amount

            # Calculate days in pipeline
            if deal.created_at:
                days = (datetime.utcnow() - deal.created_at.replace(tzinfo=None)).days
                total_days += days

        if deals:
            summary["average_deal_size"] = summary["total_value"] / len(deals)
            summary["average_days_in_pipeline"] = total_days // len(deals)

        return summary

    async def get_stale_deals(
        self,
        days_threshold: int = 14
    ) -> List[CRMDeal]:
        """
        Get deals that have been in current stage too long.

        Args:
            days_threshold: Number of days to consider stale

        Returns:
            List of stale deals
        """
        threshold_date = datetime.utcnow() - timedelta(days=days_threshold)

        result = await self.session.execute(
            select(CRMDeal).where(
                CRMDeal.is_deleted == False,
                CRMDeal.stage.not_in([DealStage.CLOSED_WON, DealStage.CLOSED_LOST]),
                or_(
                    CRMDeal.last_activity_date < threshold_date,
                    CRMDeal.last_activity_date.is_(None)
                )
            ).order_by(CRMDeal.last_activity_date.asc())
        )

        return result.scalars().all()

    async def calculate_win_rate(
        self,
        owner_id: Optional[UUID] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Calculate win rate statistics.

        Args:
            owner_id: Optional filter by owner
            date_range: Optional date range

        Returns:
            Win rate statistics
        """
        query = select(CRMDeal).where(
            CRMDeal.is_deleted == False,
            CRMDeal.stage.in_([DealStage.CLOSED_WON, DealStage.CLOSED_LOST])
        )

        if owner_id:
            query = query.where(CRMDeal.owner_id == owner_id)
        if date_range:
            query = query.where(
                CRMDeal.actual_close_date.between(date_range[0].date(), date_range[1].date())
            )

        result = await self.session.execute(query)
        deals = result.scalars().all()

        won = [d for d in deals if d.stage == DealStage.CLOSED_WON]
        lost = [d for d in deals if d.stage == DealStage.CLOSED_LOST]

        total = len(deals)
        win_rate = (len(won) / total * 100) if total > 0 else 0

        won_value = sum(d.amount or Decimal("0") for d in won)
        lost_value = sum(d.amount or Decimal("0") for d in lost)

        # Analyze lost reasons
        lost_reasons = {}
        for deal in lost:
            reason = deal.lost_reason or "Unknown"
            if reason not in lost_reasons:
                lost_reasons[reason] = 0
            lost_reasons[reason] += 1

        return {
            "total_closed": total,
            "won_count": len(won),
            "lost_count": len(lost),
            "win_rate": round(win_rate, 2),
            "won_value": won_value,
            "lost_value": lost_value,
            "lost_reasons": lost_reasons,
            "average_won_deal_size": won_value / len(won) if won else Decimal("0"),
            "average_lost_deal_size": lost_value / len(lost) if lost else Decimal("0")
        }


# =============================================================================
# WORKFLOW AUTOMATION ENGINE
# =============================================================================

class WorkflowAutomationEngine:
    """
    Workflow automation engine that processes triggers and executes actions.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self._action_handlers = {
            WorkflowActionType.SEND_EMAIL: self._handle_send_email,
            WorkflowActionType.CREATE_TASK: self._handle_create_task,
            WorkflowActionType.UPDATE_LEAD_STATUS: self._handle_update_lead_status,
            WorkflowActionType.UPDATE_DEAL_STAGE: self._handle_update_deal_stage,
            WorkflowActionType.ASSIGN_OWNER: self._handle_assign_owner,
            WorkflowActionType.ADD_TAG: self._handle_add_tag,
            WorkflowActionType.REMOVE_TAG: self._handle_remove_tag,
            WorkflowActionType.SEND_NOTIFICATION: self._handle_send_notification,
            WorkflowActionType.WEBHOOK: self._handle_webhook,
        }

    async def process_trigger(
        self,
        trigger_type: WorkflowTrigger,
        entity_id: UUID,
        entity_type: str,
        trigger_data: Dict[str, Any]
    ) -> List[str]:
        """
        Process a trigger event and execute matching workflows.

        Args:
            trigger_type: Type of trigger
            entity_id: ID of the entity that triggered
            entity_type: Type of entity (lead, deal, etc.)
            trigger_data: Additional trigger context

        Returns:
            List of execution IDs
        """
        # Find active workflows matching the trigger
        result = await self.session.execute(
            select(CRMWorkflow).where(
                CRMWorkflow.is_active == True,
                CRMWorkflow.is_deleted == False,
                CRMWorkflow.trigger_type == trigger_type
            )
        )
        workflows = result.scalars().all()

        execution_ids = []
        for workflow in workflows:
            # Check trigger conditions
            if not self._check_trigger_conditions(workflow, trigger_data):
                continue

            # Check filter conditions
            if not await self._check_filter_conditions(workflow, entity_id, entity_type):
                continue

            # Check cooldown
            if not await self._check_cooldown(workflow, entity_id):
                continue

            # Execute workflow
            execution_id = await self._execute_workflow(
                workflow,
                entity_id,
                entity_type,
                trigger_data
            )
            execution_ids.append(execution_id)

        return execution_ids

    def _check_trigger_conditions(
        self,
        workflow: CRMWorkflow,
        trigger_data: Dict[str, Any]
    ) -> bool:
        """Check if trigger conditions are met"""
        conditions = workflow.trigger_conditions or {}

        if not conditions:
            return True

        # Status change conditions
        if workflow.trigger_type == WorkflowTrigger.LEAD_STATUS_CHANGED:
            if "from_status" in conditions:
                if trigger_data.get("old_status") != conditions["from_status"]:
                    return False
            if "to_status" in conditions:
                if trigger_data.get("new_status") != conditions["to_status"]:
                    return False

        # Score threshold conditions
        if workflow.trigger_type == WorkflowTrigger.LEAD_SCORE_THRESHOLD:
            operator = conditions.get("operator", ">=")
            threshold = conditions.get("value", 0)
            score = trigger_data.get("score", 0)

            if operator == ">=" and score < threshold:
                return False
            elif operator == ">" and score <= threshold:
                return False
            elif operator == "==" and score != threshold:
                return False

        # Deal stage change conditions
        if workflow.trigger_type == WorkflowTrigger.DEAL_STAGE_CHANGED:
            if "from_stage" in conditions:
                if trigger_data.get("old_stage") != conditions["from_stage"]:
                    return False
            if "to_stage" in conditions:
                if trigger_data.get("new_stage") != conditions["to_stage"]:
                    return False

        return True

    async def _check_filter_conditions(
        self,
        workflow: CRMWorkflow,
        entity_id: UUID,
        entity_type: str
    ) -> bool:
        """Check if entity matches filter conditions"""
        filters = workflow.filter_conditions or {}

        if not filters:
            return True

        if entity_type == "lead":
            result = await self.session.execute(
                select(CRMLead).where(CRMLead.id == entity_id)
            )
            entity = result.scalar_one_or_none()
            if not entity:
                return False

            # Check lead source filter
            if "lead_source" in filters:
                if entity.source.value not in filters["lead_source"]:
                    return False

            # Check industry filter
            if "industry" in filters:
                if entity.industry and entity.industry.value not in filters["industry"]:
                    return False

            # Check organization type filter
            if "organization_type" in filters:
                if entity.organization_type.value not in filters["organization_type"]:
                    return False

        return True

    async def _check_cooldown(
        self,
        workflow: CRMWorkflow,
        entity_id: UUID
    ) -> bool:
        """Check if workflow is in cooldown for this entity"""
        if workflow.cooldown_hours == 0:
            return True

        # Check max executions
        result = await self.session.execute(
            select(func.count(WorkflowExecutionLog.id)).where(
                WorkflowExecutionLog.workflow_id == workflow.id,
                or_(
                    WorkflowExecutionLog.lead_id == entity_id,
                    WorkflowExecutionLog.deal_id == entity_id
                )
            )
        )
        execution_count = result.scalar()

        if execution_count >= workflow.max_executions_per_record:
            return False

        # Check cooldown period
        cooldown_start = datetime.utcnow() - timedelta(hours=workflow.cooldown_hours)
        result = await self.session.execute(
            select(WorkflowExecutionLog).where(
                WorkflowExecutionLog.workflow_id == workflow.id,
                or_(
                    WorkflowExecutionLog.lead_id == entity_id,
                    WorkflowExecutionLog.deal_id == entity_id
                ),
                WorkflowExecutionLog.started_at > cooldown_start
            )
        )
        recent_execution = result.scalar_one_or_none()

        return recent_execution is None

    async def _execute_workflow(
        self,
        workflow: CRMWorkflow,
        entity_id: UUID,
        entity_type: str,
        trigger_data: Dict[str, Any]
    ) -> str:
        """Execute workflow actions"""
        execution_id = str(uuid4())
        started_at = datetime.utcnow()

        # Create execution log
        log = WorkflowExecutionLog(
            workflow_id=workflow.id,
            execution_id=execution_id,
            trigger_data=trigger_data,
            status="in_progress",
            actions_executed=[]
        )

        if entity_type == "lead":
            log.lead_id = entity_id
        elif entity_type == "deal":
            log.deal_id = entity_id

        self.session.add(log)
        await self.session.commit()

        try:
            actions_executed = []
            for action in workflow.actions:
                action_type = WorkflowActionType(action["type"])
                delay_hours = action.get("delay_hours", 0)

                # Handle delay (in production, use task queue)
                if delay_hours > 0:
                    # Schedule for later execution
                    action_result = {
                        "action_type": action_type.value,
                        "status": "scheduled",
                        "scheduled_for": (datetime.utcnow() + timedelta(hours=delay_hours)).isoformat(),
                        "executed_at": None
                    }
                else:
                    # Execute immediately
                    handler = self._action_handlers.get(action_type)
                    if handler:
                        result = await handler(action, entity_id, entity_type, trigger_data)
                        action_result = {
                            "action_type": action_type.value,
                            "status": "completed",
                            "result": result,
                            "executed_at": datetime.utcnow().isoformat()
                        }
                    else:
                        action_result = {
                            "action_type": action_type.value,
                            "status": "skipped",
                            "error": "No handler for action type",
                            "executed_at": datetime.utcnow().isoformat()
                        }

                actions_executed.append(action_result)

            # Update log
            log.status = "completed"
            log.actions_executed = actions_executed
            log.completed_at = datetime.utcnow()
            log.duration_ms = int((datetime.utcnow() - started_at).total_seconds() * 1000)

            # Update workflow statistics
            workflow.execution_count += 1
            workflow.successful_executions += 1
            workflow.last_executed_at = datetime.utcnow()

            await self.session.commit()

            logger.info(
                "workflow_executed",
                workflow_id=str(workflow.id),
                execution_id=execution_id,
                actions_count=len(actions_executed)
            )

        except Exception as e:
            log.status = "failed"
            log.error_message = str(e)
            log.completed_at = datetime.utcnow()

            workflow.execution_count += 1
            workflow.failed_executions += 1
            workflow.last_error = str(e)

            await self.session.commit()

            logger.error(
                "workflow_execution_failed",
                workflow_id=str(workflow.id),
                execution_id=execution_id,
                error=str(e)
            )

        return execution_id

    async def _handle_send_email(
        self,
        action: Dict,
        entity_id: UUID,
        entity_type: str,
        trigger_data: Dict
    ) -> Dict:
        """Handle send email action"""
        template_id = action.get("template_id")

        # In production, integrate with email service
        return {
            "template_id": template_id,
            "sent": True,
            "message": "Email queued for delivery"
        }

    async def _handle_create_task(
        self,
        action: Dict,
        entity_id: UUID,
        entity_type: str,
        trigger_data: Dict
    ) -> Dict:
        """Handle create task action"""
        task_type = TaskType(action.get("task_type", "follow_up"))
        assigned_to = action.get("assigned_to")
        title = action.get("title", f"Follow up - {entity_type}")
        due_days = action.get("due_days", 1)

        # Resolve assignee
        assignee_id = None
        if assigned_to == "owner":
            if entity_type == "lead":
                result = await self.session.execute(
                    select(CRMLead.assigned_to_id).where(CRMLead.id == entity_id)
                )
                assignee_id = result.scalar()
            elif entity_type == "deal":
                result = await self.session.execute(
                    select(CRMDeal.owner_id).where(CRMDeal.id == entity_id)
                )
                assignee_id = result.scalar()
        elif assigned_to:
            assignee_id = UUID(assigned_to)

        task = CRMTask(
            title=title,
            task_type=task_type,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.PENDING,
            assigned_to_id=assignee_id,
            created_by_id=assignee_id,  # System-created
            due_date=datetime.utcnow() + timedelta(days=due_days)
        )

        if entity_type == "lead":
            task.lead_id = entity_id
        elif entity_type == "deal":
            task.deal_id = entity_id

        self.session.add(task)

        return {
            "task_id": str(task.id),
            "title": title,
            "due_date": task.due_date.isoformat()
        }

    async def _handle_update_lead_status(
        self,
        action: Dict,
        entity_id: UUID,
        entity_type: str,
        trigger_data: Dict
    ) -> Dict:
        """Handle update lead status action"""
        if entity_type != "lead":
            return {"error": "Not a lead entity"}

        new_status = LeadStatus(action.get("status"))

        result = await self.session.execute(
            select(CRMLead).where(CRMLead.id == entity_id)
        )
        lead = result.scalar_one_or_none()

        if lead:
            old_status = lead.status
            lead.status = new_status
            return {
                "old_status": old_status.value,
                "new_status": new_status.value
            }

        return {"error": "Lead not found"}

    async def _handle_update_deal_stage(
        self,
        action: Dict,
        entity_id: UUID,
        entity_type: str,
        trigger_data: Dict
    ) -> Dict:
        """Handle update deal stage action"""
        if entity_type != "deal":
            return {"error": "Not a deal entity"}

        new_stage = DealStage(action.get("stage"))

        result = await self.session.execute(
            select(CRMDeal).where(CRMDeal.id == entity_id)
        )
        deal = result.scalar_one_or_none()

        if deal:
            old_stage = deal.stage
            deal.update_stage(new_stage)
            return {
                "old_stage": old_stage.value,
                "new_stage": new_stage.value
            }

        return {"error": "Deal not found"}

    async def _handle_assign_owner(
        self,
        action: Dict,
        entity_id: UUID,
        entity_type: str,
        trigger_data: Dict
    ) -> Dict:
        """Handle assign owner action"""
        owner_id = action.get("owner_id")
        assignment_method = action.get("method", "specific")  # specific, round_robin

        if assignment_method == "round_robin":
            # Implement round-robin assignment logic
            pass

        if entity_type == "lead":
            await self.session.execute(
                update(CRMLead).where(CRMLead.id == entity_id).values(
                    assigned_to_id=owner_id
                )
            )
        elif entity_type == "deal":
            await self.session.execute(
                update(CRMDeal).where(CRMDeal.id == entity_id).values(
                    owner_id=owner_id
                )
            )

        return {"assigned_to": owner_id}

    async def _handle_add_tag(
        self,
        action: Dict,
        entity_id: UUID,
        entity_type: str,
        trigger_data: Dict
    ) -> Dict:
        """Handle add tag action"""
        tag = action.get("tag")

        if entity_type == "lead":
            result = await self.session.execute(
                select(CRMLead).where(CRMLead.id == entity_id)
            )
            entity = result.scalar_one_or_none()
            if entity:
                tags = entity.tags or []
                if tag not in tags:
                    tags.append(tag)
                    entity.tags = tags

        return {"tag_added": tag}

    async def _handle_remove_tag(
        self,
        action: Dict,
        entity_id: UUID,
        entity_type: str,
        trigger_data: Dict
    ) -> Dict:
        """Handle remove tag action"""
        tag = action.get("tag")

        if entity_type == "lead":
            result = await self.session.execute(
                select(CRMLead).where(CRMLead.id == entity_id)
            )
            entity = result.scalar_one_or_none()
            if entity and entity.tags and tag in entity.tags:
                entity.tags.remove(tag)

        return {"tag_removed": tag}

    async def _handle_send_notification(
        self,
        action: Dict,
        entity_id: UUID,
        entity_type: str,
        trigger_data: Dict
    ) -> Dict:
        """Handle send notification action"""
        channel = action.get("channel", "email")
        message = action.get("message", "")

        # In production, integrate with notification service
        return {
            "channel": channel,
            "sent": True,
            "message": message
        }

    async def _handle_webhook(
        self,
        action: Dict,
        entity_id: UUID,
        entity_type: str,
        trigger_data: Dict
    ) -> Dict:
        """Handle webhook action"""
        url = action.get("url")
        method = action.get("method", "POST")

        # In production, make actual HTTP request
        return {
            "url": url,
            "method": method,
            "sent": True
        }


# =============================================================================
# CAMPAIGN MANAGEMENT SERVICE
# =============================================================================

class CampaignManagementService:
    """
    Campaign management service with analytics and ROI tracking.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_campaign(
        self,
        name: str,
        campaign_type: CampaignType,
        owner_id: UUID,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        budget: Optional[Decimal] = None,
        target_audience: Optional[Dict] = None,
        content_template: Optional[Dict] = None,
        **kwargs
    ) -> CRMCampaign:
        """
        Create a new marketing campaign.

        Args:
            name: Campaign name
            campaign_type: Type of campaign
            owner_id: Campaign owner
            start_date: Start date
            end_date: Optional end date
            budget: Campaign budget
            target_audience: Audience targeting filters
            content_template: Email/content template
            **kwargs: Additional attributes

        Returns:
            Created campaign
        """
        campaign = CRMCampaign(
            name=name,
            campaign_type=campaign_type,
            owner_id=owner_id,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            target_audience=target_audience or {},
            content_template=content_template or {},
            status=CampaignStatus.DRAFT,
            **kwargs
        )

        # Generate campaign code
        campaign.campaign_code = await self._generate_campaign_code()

        # Set UTM parameters
        campaign.utm_params = {
            "utm_source": "proficienthub",
            "utm_medium": campaign_type.value,
            "utm_campaign": campaign.campaign_code
        }

        self.session.add(campaign)
        await self.session.commit()
        await self.session.refresh(campaign)

        logger.info(
            "campaign_created",
            campaign_id=str(campaign.id),
            campaign_code=campaign.campaign_code,
            type=campaign_type.value
        )

        return campaign

    async def _generate_campaign_code(self) -> str:
        """Generate unique campaign code"""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        result = await self.session.execute(
            select(func.count(CRMCampaign.id)).where(
                func.date(CRMCampaign.created_at) == datetime.utcnow().date()
            )
        )
        count = result.scalar() + 1
        return f"CAMP-{timestamp}-{count:03d}"

    async def update_campaign_status(
        self,
        campaign_id: UUID,
        new_status: CampaignStatus
    ) -> CRMCampaign:
        """
        Update campaign status.

        Args:
            campaign_id: Campaign ID
            new_status: New status

        Returns:
            Updated campaign
        """
        result = await self.session.execute(
            select(CRMCampaign).where(CRMCampaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()

        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        old_status = campaign.status
        campaign.status = new_status

        await self.session.commit()
        await self.session.refresh(campaign)

        logger.info(
            "campaign_status_updated",
            campaign_id=str(campaign_id),
            old_status=old_status.value,
            new_status=new_status.value
        )

        return campaign

    async def record_campaign_metrics(
        self,
        campaign_id: UUID,
        metrics: Dict[str, int]
    ) -> CRMCampaign:
        """
        Update campaign metrics.

        Args:
            campaign_id: Campaign ID
            metrics: Dict of metric updates

        Returns:
            Updated campaign
        """
        result = await self.session.execute(
            select(CRMCampaign).where(CRMCampaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()

        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        # Update metrics
        for metric, value in metrics.items():
            if hasattr(campaign, metric):
                current = getattr(campaign, metric) or 0
                setattr(campaign, metric, current + value)

        await self.session.commit()
        await self.session.refresh(campaign)

        return campaign

    async def get_campaign_analytics(
        self,
        campaign_id: UUID
    ) -> Dict[str, Any]:
        """
        Get comprehensive campaign analytics.

        Args:
            campaign_id: Campaign ID

        Returns:
            Analytics dictionary
        """
        result = await self.session.execute(
            select(CRMCampaign).where(CRMCampaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()

        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        # Calculate metrics
        analytics = {
            "campaign_id": str(campaign.id),
            "name": campaign.name,
            "status": campaign.status.value,
            "type": campaign.campaign_type.value,

            # Email Metrics
            "email_metrics": {
                "sent": campaign.emails_sent,
                "delivered": campaign.emails_delivered,
                "opened": campaign.emails_opened,
                "unique_opens": campaign.unique_opens,
                "clicked": campaign.emails_clicked,
                "unique_clicks": campaign.unique_clicks,
                "bounced": campaign.emails_bounced,
                "unsubscribes": campaign.unsubscribes,
                "open_rate": campaign.open_rate,
                "click_rate": campaign.click_rate,
                "click_to_open_rate": campaign.click_to_open_rate,
                "bounce_rate": campaign.bounce_rate
            },

            # Lead Metrics
            "lead_metrics": {
                "generated": campaign.leads_generated,
                "qualified": campaign.leads_qualified,
                "conversions": campaign.conversions,
                "conversion_rate": campaign.conversion_rate
            },

            # Financial Metrics
            "financial_metrics": {
                "budget": float(campaign.budget) if campaign.budget else 0,
                "actual_cost": float(campaign.actual_cost) if campaign.actual_cost else 0,
                "revenue_generated": float(campaign.revenue_generated),
                "roi": campaign.roi,
                "cost_per_lead": campaign.cost_per_lead,
                "cost_per_conversion": campaign.cost_per_conversion
            },

            # Goals vs Actuals
            "goals": {
                "leads": {
                    "goal": campaign.goal_leads,
                    "actual": campaign.leads_generated,
                    "achievement": (campaign.leads_generated / campaign.goal_leads * 100) if campaign.goal_leads else None
                },
                "conversions": {
                    "goal": campaign.goal_conversions,
                    "actual": campaign.conversions,
                    "achievement": (campaign.conversions / campaign.goal_conversions * 100) if campaign.goal_conversions else None
                },
                "revenue": {
                    "goal": float(campaign.goal_revenue) if campaign.goal_revenue else None,
                    "actual": float(campaign.revenue_generated),
                    "achievement": (float(campaign.revenue_generated / campaign.goal_revenue * 100)) if campaign.goal_revenue else None
                }
            },

            # Timeline
            "timeline": {
                "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
                "end_date": campaign.end_date.isoformat() if campaign.end_date else None,
                "days_active": (datetime.utcnow() - campaign.start_date.replace(tzinfo=None)).days if campaign.start_date else 0
            }
        }

        return analytics

    async def get_campaign_performance_comparison(
        self,
        campaign_ids: List[UUID]
    ) -> List[Dict[str, Any]]:
        """
        Compare performance across multiple campaigns.

        Args:
            campaign_ids: List of campaign IDs to compare

        Returns:
            List of campaign summaries for comparison
        """
        result = await self.session.execute(
            select(CRMCampaign).where(CRMCampaign.id.in_(campaign_ids))
        )
        campaigns = result.scalars().all()

        comparison = []
        for campaign in campaigns:
            comparison.append({
                "id": str(campaign.id),
                "name": campaign.name,
                "type": campaign.campaign_type.value,
                "status": campaign.status.value,
                "open_rate": campaign.open_rate,
                "click_rate": campaign.click_rate,
                "conversion_rate": campaign.conversion_rate,
                "leads_generated": campaign.leads_generated,
                "roi": campaign.roi,
                "cost_per_lead": campaign.cost_per_lead
            })

        return comparison

    async def get_best_performing_campaigns(
        self,
        limit: int = 10,
        metric: str = "roi"
    ) -> List[CRMCampaign]:
        """
        Get best performing campaigns by specified metric.

        Args:
            limit: Number of campaigns to return
            metric: Metric to sort by (roi, open_rate, conversion_rate)

        Returns:
            List of top performing campaigns
        """
        query = select(CRMCampaign).where(
            CRMCampaign.is_deleted == False,
            CRMCampaign.status.in_([CampaignStatus.ACTIVE, CampaignStatus.COMPLETED])
        )

        if metric == "leads":
            query = query.order_by(desc(CRMCampaign.leads_generated))
        elif metric == "conversions":
            query = query.order_by(desc(CRMCampaign.conversions))
        elif metric == "revenue":
            query = query.order_by(desc(CRMCampaign.revenue_generated))
        else:
            # Default to leads as ROI needs calculation
            query = query.order_by(desc(CRMCampaign.leads_generated))

        query = query.limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()


# =============================================================================
# CRM SERVICE FACADE
# =============================================================================

class CRMService:
    """
    Main CRM service facade that coordinates all CRM operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.lead_scoring = LeadScoringService()
        self.pipeline = DealPipelineService(session)
        self.workflow_engine = WorkflowAutomationEngine(session)
        self.campaigns = CampaignManagementService(session)

    # ==========================================================================
    # Lead Operations
    # ==========================================================================

    async def create_lead(
        self,
        organization_name: str,
        contact_first_name: str,
        contact_last_name: str,
        contact_email: str,
        source: LeadSource,
        created_by_id: UUID,
        **kwargs
    ) -> CRMLead:
        """Create a new lead"""
        lead = CRMLead(
            organization_name=organization_name,
            contact_first_name=contact_first_name,
            contact_last_name=contact_last_name,
            contact_email=contact_email,
            source=source,
            created_by_id=created_by_id,
            status=LeadStatus.NEW,
            first_contact_date=datetime.utcnow(),
            **kwargs
        )

        self.session.add(lead)
        await self.session.commit()
        await self.session.refresh(lead)

        # Calculate initial score
        await self.lead_scoring.update_lead_score(self.session, lead.id)

        # Trigger workflow
        await self.workflow_engine.process_trigger(
            WorkflowTrigger.LEAD_CREATED,
            lead.id,
            "lead",
            {"source": source.value}
        )

        logger.info(
            "lead_created",
            lead_id=str(lead.id),
            organization=organization_name,
            source=source.value
        )

        return lead

    async def update_lead_status(
        self,
        lead_id: UUID,
        new_status: LeadStatus,
        notes: Optional[str] = None
    ) -> CRMLead:
        """Update lead status"""
        result = await self.session.execute(
            select(CRMLead).where(CRMLead.id == lead_id)
        )
        lead = result.scalar_one_or_none()

        if not lead:
            raise ValueError(f"Lead {lead_id} not found")

        old_status = lead.status
        lead.status = new_status
        lead.last_activity_date = datetime.utcnow()

        if notes:
            lead.qualification_notes = notes

        await self.session.commit()
        await self.session.refresh(lead)

        # Trigger workflow
        await self.workflow_engine.process_trigger(
            WorkflowTrigger.LEAD_STATUS_CHANGED,
            lead.id,
            "lead",
            {"old_status": old_status.value, "new_status": new_status.value}
        )

        return lead

    async def convert_lead_to_customer(
        self,
        lead_id: UUID,
        academy_id: UUID,
        deal_name: str,
        deal_amount: Decimal,
        owner_id: UUID
    ) -> Tuple[CRMLead, CRMDeal]:
        """Convert lead to customer and create deal"""
        result = await self.session.execute(
            select(CRMLead).where(CRMLead.id == lead_id)
        )
        lead = result.scalar_one_or_none()

        if not lead:
            raise ValueError(f"Lead {lead_id} not found")

        # Update lead
        lead.status = LeadStatus.CONVERTED
        lead.converted_at = datetime.utcnow()
        lead.converted_to_academy_id = academy_id

        # Create deal
        deal = await self.pipeline.create_deal(
            lead_id=lead_id,
            academy_id=academy_id,
            name=deal_name,
            amount=deal_amount,
            owner_id=owner_id,
            products=[]
        )

        lead.converted_to_deal_id = deal.id

        await self.session.commit()

        logger.info(
            "lead_converted",
            lead_id=str(lead_id),
            academy_id=str(academy_id),
            deal_id=str(deal.id)
        )

        return lead, deal

    async def mark_lead_lost(
        self,
        lead_id: UUID,
        reason: str,
        details: Optional[str] = None,
        competitor: Optional[str] = None
    ) -> CRMLead:
        """Mark lead as lost"""
        result = await self.session.execute(
            select(CRMLead).where(CRMLead.id == lead_id)
        )
        lead = result.scalar_one_or_none()

        if not lead:
            raise ValueError(f"Lead {lead_id} not found")

        lead.status = LeadStatus.LOST
        lead.lost_at = datetime.utcnow()
        lead.lost_reason = reason
        lead.lost_reason_details = details
        lead.competitor_name = competitor

        await self.session.commit()
        await self.session.refresh(lead)

        return lead

    async def get_leads(
        self,
        status: Optional[LeadStatus] = None,
        source: Optional[LeadSource] = None,
        assigned_to: Optional[UUID] = None,
        min_score: Optional[int] = None,
        is_qualified: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[CRMLead], int]:
        """Get leads with filters"""
        query = select(CRMLead).where(CRMLead.is_deleted == False)

        if status:
            query = query.where(CRMLead.status == status)
        if source:
            query = query.where(CRMLead.source == source)
        if assigned_to:
            query = query.where(CRMLead.assigned_to_id == assigned_to)
        if min_score is not None:
            query = query.where(CRMLead.lead_score >= min_score)
        if is_qualified is not None:
            query = query.where(CRMLead.is_qualified == is_qualified)

        # Get total count
        count_result = await self.session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar()

        # Apply pagination
        query = query.order_by(desc(CRMLead.created_at)).offset(offset).limit(limit)

        result = await self.session.execute(query)
        leads = result.scalars().all()

        return leads, total

    # ==========================================================================
    # Contact Operations
    # ==========================================================================

    async def create_contact(
        self,
        first_name: str,
        last_name: str,
        email: str,
        lead_id: Optional[UUID] = None,
        academy_id: Optional[UUID] = None,
        created_by_id: Optional[UUID] = None,
        **kwargs
    ) -> CRMContact:
        """Create a new contact"""
        contact = CRMContact(
            first_name=first_name,
            last_name=last_name,
            email=email,
            lead_id=lead_id,
            academy_id=academy_id,
            created_by_id=created_by_id,
            **kwargs
        )

        self.session.add(contact)
        await self.session.commit()
        await self.session.refresh(contact)

        return contact

    async def get_contacts_for_lead(
        self,
        lead_id: UUID
    ) -> List[CRMContact]:
        """Get all contacts for a lead"""
        result = await self.session.execute(
            select(CRMContact).where(
                CRMContact.lead_id == lead_id,
                CRMContact.is_deleted == False
            ).order_by(desc(CRMContact.is_primary), CRMContact.created_at)
        )
        return result.scalars().all()

    # ==========================================================================
    # Communication Operations
    # ==========================================================================

    async def log_communication(
        self,
        user_id: UUID,
        comm_type: CommunicationType,
        direction: CommunicationDirection,
        lead_id: Optional[UUID] = None,
        academy_id: Optional[UUID] = None,
        contact_id: Optional[UUID] = None,
        deal_id: Optional[UUID] = None,
        **kwargs
    ) -> CRMCommunication:
        """Log a communication"""
        communication = CRMCommunication(
            user_id=user_id,
            comm_type=comm_type,
            direction=direction,
            lead_id=lead_id,
            academy_id=academy_id,
            contact_id=contact_id,
            deal_id=deal_id,
            **kwargs
        )

        self.session.add(communication)

        # Update last contact date on lead
        if lead_id:
            await self.session.execute(
                update(CRMLead).where(CRMLead.id == lead_id).values(
                    last_contact_date=datetime.utcnow(),
                    last_activity_date=datetime.utcnow()
                )
            )

            # Update counters based on type
            if comm_type == CommunicationType.EMAIL:
                await self.session.execute(
                    update(CRMLead).where(CRMLead.id == lead_id).values(
                        total_emails_sent=CRMLead.total_emails_sent + 1
                    )
                )
            elif comm_type == CommunicationType.CALL:
                await self.session.execute(
                    update(CRMLead).where(CRMLead.id == lead_id).values(
                        total_calls=CRMLead.total_calls + 1
                    )
                )
            elif comm_type in [CommunicationType.MEETING, CommunicationType.VIDEO_CALL]:
                await self.session.execute(
                    update(CRMLead).where(CRMLead.id == lead_id).values(
                        total_meetings=CRMLead.total_meetings + 1
                    )
                )

        await self.session.commit()
        await self.session.refresh(communication)

        # Update lead score after communication
        if lead_id:
            await self.lead_scoring.update_lead_score(self.session, lead_id)

        return communication

    async def get_communication_history(
        self,
        lead_id: Optional[UUID] = None,
        academy_id: Optional[UUID] = None,
        deal_id: Optional[UUID] = None,
        limit: int = 50
    ) -> List[CRMCommunication]:
        """Get communication history"""
        query = select(CRMCommunication).where(CRMCommunication.is_deleted == False)

        if lead_id:
            query = query.where(CRMCommunication.lead_id == lead_id)
        if academy_id:
            query = query.where(CRMCommunication.academy_id == academy_id)
        if deal_id:
            query = query.where(CRMCommunication.deal_id == deal_id)

        query = query.order_by(desc(CRMCommunication.created_at)).limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()

    # ==========================================================================
    # Task Operations
    # ==========================================================================

    async def create_task(
        self,
        title: str,
        created_by_id: UUID,
        task_type: TaskType = TaskType.OTHER,
        lead_id: Optional[UUID] = None,
        deal_id: Optional[UUID] = None,
        assigned_to_id: Optional[UUID] = None,
        due_date: Optional[datetime] = None,
        **kwargs
    ) -> CRMTask:
        """Create a new task"""
        task = CRMTask(
            title=title,
            created_by_id=created_by_id,
            task_type=task_type,
            lead_id=lead_id,
            deal_id=deal_id,
            assigned_to_id=assigned_to_id or created_by_id,
            due_date=due_date,
            status=TaskStatus.PENDING,
            **kwargs
        )

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def complete_task(
        self,
        task_id: UUID,
        outcome: Optional[str] = None
    ) -> CRMTask:
        """Complete a task"""
        result = await self.session.execute(
            select(CRMTask).where(CRMTask.id == task_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.mark_completed(outcome)
        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def get_overdue_tasks(
        self,
        assigned_to_id: Optional[UUID] = None
    ) -> List[CRMTask]:
        """Get overdue tasks"""
        query = select(CRMTask).where(
            CRMTask.is_deleted == False,
            CRMTask.status != TaskStatus.COMPLETED,
            CRMTask.due_date < datetime.utcnow()
        )

        if assigned_to_id:
            query = query.where(CRMTask.assigned_to_id == assigned_to_id)

        query = query.order_by(asc(CRMTask.due_date))

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_tasks_due_today(
        self,
        assigned_to_id: Optional[UUID] = None
    ) -> List[CRMTask]:
        """Get tasks due today"""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        query = select(CRMTask).where(
            CRMTask.is_deleted == False,
            CRMTask.status != TaskStatus.COMPLETED,
            CRMTask.due_date >= today_start,
            CRMTask.due_date < today_end
        )

        if assigned_to_id:
            query = query.where(CRMTask.assigned_to_id == assigned_to_id)

        query = query.order_by(asc(CRMTask.due_date))

        result = await self.session.execute(query)
        return result.scalars().all()

    # ==========================================================================
    # Analytics
    # ==========================================================================

    async def get_crm_dashboard_stats(
        self,
        academy_id: Optional[UUID] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Get CRM dashboard statistics"""
        # Lead stats
        lead_query = select(CRMLead).where(CRMLead.is_deleted == False)
        if academy_id:
            lead_query = lead_query.where(CRMLead.converted_to_academy_id == academy_id)
        if date_range:
            lead_query = lead_query.where(CRMLead.created_at.between(*date_range))

        lead_result = await self.session.execute(lead_query)
        leads = lead_result.scalars().all()

        lead_stats = {
            "total": len(leads),
            "by_status": {},
            "by_source": {},
            "qualified": len([l for l in leads if l.is_qualified]),
            "converted": len([l for l in leads if l.status == LeadStatus.CONVERTED])
        }

        for lead in leads:
            status = lead.status.value
            source = lead.source.value
            lead_stats["by_status"][status] = lead_stats["by_status"].get(status, 0) + 1
            lead_stats["by_source"][source] = lead_stats["by_source"].get(source, 0) + 1

        # Pipeline stats
        pipeline_summary = await self.pipeline.get_pipeline_summary(
            academy_id=academy_id,
            date_range=date_range
        )

        # Win rate
        win_rate_stats = await self.pipeline.calculate_win_rate(date_range=date_range)

        # Task stats
        overdue_tasks = await self.get_overdue_tasks()
        today_tasks = await self.get_tasks_due_today()

        return {
            "leads": lead_stats,
            "pipeline": pipeline_summary,
            "win_rate": win_rate_stats,
            "tasks": {
                "overdue_count": len(overdue_tasks),
                "due_today_count": len(today_tasks)
            }
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_crm_service: Optional[CRMService] = None


def get_crm_service(session: AsyncSession) -> CRMService:
    """Get CRM service instance"""
    return CRMService(session)
