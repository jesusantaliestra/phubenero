"""
ProficientHub - External CRM Connectors
Full API integrations for Salesforce, HubSpot, Zoho CRM, and Custom Webhooks.
Handles bidirectional sync, field mappings, and OAuth flows.
"""

import asyncio
import hashlib
import hmac
import json
import time
import structlog
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional, Any, Tuple, Type
from urllib.parse import urlencode, urljoin
from uuid import UUID, uuid4

import httpx
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models_crm import (
    CRMLead, CRMContact, CRMDeal, CRMCommunication,
    ExternalCRMIntegration, CRMSyncLog,
    LeadSource, LeadStatus, LeadOrganizationType,
    ContactType, DealStage,
    ExternalCRMType, SyncDirection, SyncStatus
)

logger = structlog.get_logger(__name__)


# =============================================================================
# BASE CONNECTOR INTERFACE
# =============================================================================

class BaseCRMConnector(ABC):
    """
    Abstract base class for CRM connectors.
    Defines the interface for all external CRM integrations.
    """

    def __init__(
        self,
        integration: ExternalCRMIntegration,
        session: AsyncSession
    ):
        self.integration = integration
        self.session = session
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()

    # ==========================================================================
    # Authentication
    # ==========================================================================

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the external CRM"""
        pass

    @abstractmethod
    async def refresh_access_token(self) -> bool:
        """Refresh OAuth access token"""
        pass

    async def ensure_authenticated(self) -> bool:
        """Ensure we have valid authentication"""
        if self.integration.is_token_expired:
            if self.integration.refresh_token:
                return await self.refresh_access_token()
            return False
        return True

    # ==========================================================================
    # Lead Operations
    # ==========================================================================

    @abstractmethod
    async def get_leads(
        self,
        modified_since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch leads from external CRM"""
        pass

    @abstractmethod
    async def create_lead(self, lead: CRMLead) -> Optional[str]:
        """Create lead in external CRM, returns external ID"""
        pass

    @abstractmethod
    async def update_lead(
        self,
        external_id: str,
        lead: CRMLead
    ) -> bool:
        """Update lead in external CRM"""
        pass

    @abstractmethod
    async def delete_lead(self, external_id: str) -> bool:
        """Delete lead in external CRM"""
        pass

    # ==========================================================================
    # Contact Operations
    # ==========================================================================

    @abstractmethod
    async def get_contacts(
        self,
        modified_since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch contacts from external CRM"""
        pass

    @abstractmethod
    async def create_contact(self, contact: CRMContact) -> Optional[str]:
        """Create contact in external CRM, returns external ID"""
        pass

    @abstractmethod
    async def update_contact(
        self,
        external_id: str,
        contact: CRMContact
    ) -> bool:
        """Update contact in external CRM"""
        pass

    # ==========================================================================
    # Deal/Opportunity Operations
    # ==========================================================================

    @abstractmethod
    async def get_deals(
        self,
        modified_since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch deals/opportunities from external CRM"""
        pass

    @abstractmethod
    async def create_deal(self, deal: CRMDeal) -> Optional[str]:
        """Create deal in external CRM, returns external ID"""
        pass

    @abstractmethod
    async def update_deal(
        self,
        external_id: str,
        deal: CRMDeal
    ) -> bool:
        """Update deal in external CRM"""
        pass

    # ==========================================================================
    # Field Mapping
    # ==========================================================================

    def map_fields_outbound(
        self,
        entity: Any,
        entity_type: str
    ) -> Dict[str, Any]:
        """Map internal fields to external CRM fields"""
        mappings = self.integration.field_mappings or {}
        entity_mappings = mappings.get(entity_type, {})

        result = {}
        for internal_field, external_field in entity_mappings.items():
            value = getattr(entity, internal_field, None)
            if value is not None:
                # Handle enums
                if hasattr(value, 'value'):
                    value = value.value
                # Handle datetimes
                elif isinstance(value, datetime):
                    value = value.isoformat()
                # Handle Decimal
                elif isinstance(value, Decimal):
                    value = float(value)
                result[external_field] = value

        return result

    def map_fields_inbound(
        self,
        external_data: Dict[str, Any],
        entity_type: str
    ) -> Dict[str, Any]:
        """Map external CRM fields to internal fields"""
        mappings = self.integration.field_mappings or {}
        entity_mappings = mappings.get(entity_type, {})

        # Reverse the mapping
        reverse_mappings = {v: k for k, v in entity_mappings.items()}

        result = {}
        for external_field, internal_field in reverse_mappings.items():
            if external_field in external_data:
                result[internal_field] = external_data[external_field]

        return result

    # ==========================================================================
    # Sync Operations
    # ==========================================================================

    async def sync_leads_inbound(self) -> CRMSyncLog:
        """Sync leads from external CRM to ProficientHub"""
        log = CRMSyncLog(
            integration_id=self.integration.id,
            sync_type="incremental",
            direction=SyncDirection.INBOUND,
            entity_type="leads",
            status=SyncStatus.IN_PROGRESS
        )
        self.session.add(log)
        await self.session.commit()

        try:
            # Get last sync cursor
            cursors = self.integration.sync_cursors or {}
            last_modified = None
            if "leads" in cursors and "last_modified" in cursors["leads"]:
                last_modified = datetime.fromisoformat(cursors["leads"]["last_modified"])

            # Fetch external leads
            external_leads = await self.get_leads(modified_since=last_modified)

            records_created = 0
            records_updated = 0
            records_failed = 0
            errors = []

            for external_lead in external_leads:
                try:
                    external_id = external_lead.get("id") or external_lead.get("Id")
                    mapped_data = self.map_fields_inbound(external_lead, "leads")

                    # Check if lead exists
                    result = await self.session.execute(
                        select(CRMLead).where(
                            CRMLead.external_crm_id == external_id,
                            CRMLead.external_crm_type == self.integration.crm_type
                        )
                    )
                    existing_lead = result.scalar_one_or_none()

                    if existing_lead:
                        # Update existing lead
                        for field, value in mapped_data.items():
                            setattr(existing_lead, field, value)
                        existing_lead.last_synced_at = datetime.utcnow()
                        records_updated += 1
                    else:
                        # Create new lead
                        new_lead = CRMLead(
                            external_crm_id=external_id,
                            external_crm_type=self.integration.crm_type,
                            last_synced_at=datetime.utcnow(),
                            **mapped_data
                        )
                        self.session.add(new_lead)
                        records_created += 1

                except Exception as e:
                    records_failed += 1
                    errors.append({
                        "record_id": external_id,
                        "error": str(e)
                    })

            await self.session.commit()

            # Update sync cursor
            if external_leads:
                cursors["leads"] = {"last_modified": datetime.utcnow().isoformat()}
                self.integration.sync_cursors = cursors

            # Update log
            log.status = SyncStatus.SUCCESS if not errors else SyncStatus.PARTIAL
            log.records_processed = len(external_leads)
            log.records_created = records_created
            log.records_updated = records_updated
            log.records_failed = records_failed
            log.errors = errors
            log.completed_at = datetime.utcnow()
            log.duration_seconds = int((datetime.utcnow() - log.started_at.replace(tzinfo=None)).total_seconds())

            # Update integration stats
            self.integration.last_sync_at = datetime.utcnow()
            self.integration.last_sync_status = log.status
            self.integration.total_records_synced += records_created + records_updated
            self.integration.consecutive_errors = 0

            await self.session.commit()

            logger.info(
                "leads_sync_inbound_completed",
                integration_id=str(self.integration.id),
                created=records_created,
                updated=records_updated,
                failed=records_failed
            )

            return log

        except Exception as e:
            log.status = SyncStatus.FAILED
            log.errors = [{"error": str(e)}]
            log.completed_at = datetime.utcnow()

            self.integration.last_sync_status = SyncStatus.FAILED
            self.integration.last_sync_error = str(e)
            self.integration.consecutive_errors += 1
            self.integration.total_sync_errors += 1

            await self.session.commit()

            logger.error(
                "leads_sync_inbound_failed",
                integration_id=str(self.integration.id),
                error=str(e)
            )

            return log

    async def sync_leads_outbound(self) -> CRMSyncLog:
        """Sync leads from ProficientHub to external CRM"""
        log = CRMSyncLog(
            integration_id=self.integration.id,
            sync_type="incremental",
            direction=SyncDirection.OUTBOUND,
            entity_type="leads",
            status=SyncStatus.IN_PROGRESS
        )
        self.session.add(log)
        await self.session.commit()

        try:
            # Get leads modified since last sync
            last_sync = self.integration.last_sync_at
            query = select(CRMLead).where(CRMLead.is_deleted == False)
            if last_sync:
                query = query.where(CRMLead.updated_at > last_sync)

            result = await self.session.execute(query)
            leads = result.scalars().all()

            records_created = 0
            records_updated = 0
            records_failed = 0
            errors = []

            for lead in leads:
                try:
                    if lead.external_crm_id:
                        # Update existing
                        success = await self.update_lead(lead.external_crm_id, lead)
                        if success:
                            records_updated += 1
                            lead.last_synced_at = datetime.utcnow()
                        else:
                            records_failed += 1
                    else:
                        # Create new
                        external_id = await self.create_lead(lead)
                        if external_id:
                            lead.external_crm_id = external_id
                            lead.external_crm_type = self.integration.crm_type
                            lead.last_synced_at = datetime.utcnow()
                            records_created += 1
                        else:
                            records_failed += 1

                except Exception as e:
                    records_failed += 1
                    errors.append({
                        "record_id": str(lead.id),
                        "error": str(e)
                    })

            await self.session.commit()

            # Update log
            log.status = SyncStatus.SUCCESS if not errors else SyncStatus.PARTIAL
            log.records_processed = len(leads)
            log.records_created = records_created
            log.records_updated = records_updated
            log.records_failed = records_failed
            log.errors = errors
            log.completed_at = datetime.utcnow()
            log.duration_seconds = int((datetime.utcnow() - log.started_at.replace(tzinfo=None)).total_seconds())

            # Update integration stats
            self.integration.last_sync_at = datetime.utcnow()
            self.integration.last_sync_status = log.status
            self.integration.total_records_synced += records_created + records_updated
            self.integration.consecutive_errors = 0

            await self.session.commit()

            return log

        except Exception as e:
            log.status = SyncStatus.FAILED
            log.errors = [{"error": str(e)}]
            log.completed_at = datetime.utcnow()

            self.integration.last_sync_status = SyncStatus.FAILED
            self.integration.last_sync_error = str(e)
            self.integration.consecutive_errors += 1

            await self.session.commit()

            logger.error(
                "leads_sync_outbound_failed",
                integration_id=str(self.integration.id),
                error=str(e)
            )

            return log

    async def full_sync(self) -> List[CRMSyncLog]:
        """Perform full bidirectional sync"""
        logs = []

        if self.integration.sync_leads:
            if self.integration.sync_direction in [SyncDirection.INBOUND, SyncDirection.BIDIRECTIONAL]:
                logs.append(await self.sync_leads_inbound())
            if self.integration.sync_direction in [SyncDirection.OUTBOUND, SyncDirection.BIDIRECTIONAL]:
                logs.append(await self.sync_leads_outbound())

        # Add similar sync for contacts and deals...
        return logs


# =============================================================================
# SALESFORCE CONNECTOR
# =============================================================================

class SalesforceConnector(BaseCRMConnector):
    """
    Salesforce CRM connector with full API integration.
    Supports OAuth 2.0, SOQL queries, and REST API.
    """

    API_VERSION = "v59.0"
    AUTH_URL = "https://login.salesforce.com/services/oauth2"

    def __init__(self, integration: ExternalCRMIntegration, session: AsyncSession):
        super().__init__(integration, session)
        self.base_url = integration.instance_url or ""

    @property
    def api_url(self) -> str:
        """Get Salesforce API base URL"""
        return f"{self.base_url}/services/data/{self.API_VERSION}"

    @property
    def auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        return {
            "Authorization": f"Bearer {self.integration.access_token}",
            "Content-Type": "application/json"
        }

    async def authenticate(self) -> bool:
        """
        Authenticate with Salesforce using OAuth 2.0.
        This should be called after receiving the authorization code.
        """
        try:
            response = await self.http_client.post(
                f"{self.AUTH_URL}/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.integration.api_key,
                    "client_secret": self.integration.api_secret,
                    "redirect_uri": self._get_redirect_uri(),
                    "code": self.integration.access_token  # Temporarily stored auth code
                }
            )

            if response.status_code == 200:
                data = response.json()
                self.integration.access_token = data["access_token"]
                self.integration.refresh_token = data.get("refresh_token")
                self.integration.instance_url = data["instance_url"]
                self.base_url = data["instance_url"]

                # Token expires in specified time, default 2 hours
                expires_in = data.get("expires_in", 7200)
                self.integration.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

                await self.session.commit()

                logger.info(
                    "salesforce_authenticated",
                    integration_id=str(self.integration.id)
                )
                return True

            logger.error(
                "salesforce_auth_failed",
                status=response.status_code,
                response=response.text
            )
            return False

        except Exception as e:
            logger.error("salesforce_auth_error", error=str(e))
            return False

    async def refresh_access_token(self) -> bool:
        """Refresh Salesforce OAuth token"""
        try:
            response = await self.http_client.post(
                f"{self.AUTH_URL}/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.integration.api_key,
                    "client_secret": self.integration.api_secret,
                    "refresh_token": self.integration.refresh_token
                }
            )

            if response.status_code == 200:
                data = response.json()
                self.integration.access_token = data["access_token"]
                expires_in = data.get("expires_in", 7200)
                self.integration.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

                await self.session.commit()

                logger.info(
                    "salesforce_token_refreshed",
                    integration_id=str(self.integration.id)
                )
                return True

            return False

        except Exception as e:
            logger.error("salesforce_token_refresh_error", error=str(e))
            return False

    def _get_redirect_uri(self) -> str:
        """Get OAuth redirect URI"""
        return "https://app.proficienthub.com/integrations/salesforce/callback"

    async def _soql_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute SOQL query"""
        if not await self.ensure_authenticated():
            raise Exception("Not authenticated with Salesforce")

        encoded_query = urlencode({"q": query})
        response = await self.http_client.get(
            f"{self.api_url}/query?{encoded_query}",
            headers=self.auth_headers
        )

        if response.status_code == 200:
            data = response.json()
            records = data.get("records", [])

            # Handle pagination
            while data.get("nextRecordsUrl"):
                next_response = await self.http_client.get(
                    f"{self.base_url}{data['nextRecordsUrl']}",
                    headers=self.auth_headers
                )
                if next_response.status_code == 200:
                    data = next_response.json()
                    records.extend(data.get("records", []))
                else:
                    break

            return records

        raise Exception(f"SOQL query failed: {response.text}")

    async def _api_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None
    ) -> Tuple[bool, Optional[Dict]]:
        """Make API request to Salesforce"""
        if not await self.ensure_authenticated():
            return False, None

        url = f"{self.api_url}{endpoint}"

        try:
            if method == "GET":
                response = await self.http_client.get(url, headers=self.auth_headers)
            elif method == "POST":
                response = await self.http_client.post(
                    url, headers=self.auth_headers, json=data
                )
            elif method == "PATCH":
                response = await self.http_client.patch(
                    url, headers=self.auth_headers, json=data
                )
            elif method == "DELETE":
                response = await self.http_client.delete(url, headers=self.auth_headers)
            else:
                return False, None

            # Handle rate limiting
            if response.status_code == 429:
                self.integration.rate_limit_remaining = 0
                retry_after = response.headers.get("Retry-After", "60")
                self.integration.rate_limit_reset_at = datetime.utcnow() + timedelta(seconds=int(retry_after))
                await self.session.commit()
                return False, None

            # Update rate limit info
            if "Sforce-Limit-Info" in response.headers:
                limit_info = response.headers["Sforce-Limit-Info"]
                # Parse "api-usage=X/Y" format
                if "api-usage=" in limit_info:
                    usage = limit_info.split("api-usage=")[1].split(",")[0]
                    used, total = usage.split("/")
                    self.integration.rate_limit_remaining = int(total) - int(used)

            if response.status_code in [200, 201, 204]:
                return True, response.json() if response.text else None

            return False, {"error": response.text}

        except Exception as e:
            logger.error("salesforce_api_error", error=str(e))
            return False, {"error": str(e)}

    # ==========================================================================
    # Lead Operations
    # ==========================================================================

    async def get_leads(
        self,
        modified_since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch leads from Salesforce"""
        # Build SOQL query
        fields = [
            "Id", "Company", "FirstName", "LastName", "Email", "Phone",
            "Title", "Website", "Industry", "NumberOfEmployees", "AnnualRevenue",
            "Status", "LeadSource", "Description", "Street", "City", "State",
            "PostalCode", "Country", "CreatedDate", "LastModifiedDate"
        ]

        query = f"SELECT {', '.join(fields)} FROM Lead"

        conditions = []
        if modified_since:
            conditions.append(f"LastModifiedDate > {modified_since.strftime('%Y-%m-%dT%H:%M:%SZ')}")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += f" ORDER BY LastModifiedDate ASC LIMIT {limit}"

        return await self._soql_query(query)

    async def create_lead(self, lead: CRMLead) -> Optional[str]:
        """Create lead in Salesforce"""
        # Map internal fields to Salesforce fields
        sf_data = {
            "Company": lead.organization_name,
            "FirstName": lead.contact_first_name,
            "LastName": lead.contact_last_name,
            "Email": lead.contact_email,
            "Phone": lead.contact_phone,
            "Title": lead.contact_title,
            "Website": lead.website,
            "Description": lead.notes,
            "Street": lead.address_line1,
            "City": lead.city,
            "State": lead.state,
            "PostalCode": lead.postal_code,
            "Country": lead.country
        }

        # Map industry
        if lead.industry:
            sf_industry_map = {
                "education": "Education",
                "healthcare": "Healthcare",
                "technology": "Technology",
                "finance": "Banking",
                "government": "Government"
            }
            sf_data["Industry"] = sf_industry_map.get(lead.industry.value, "Other")

        # Map lead source
        if lead.source:
            sf_source_map = {
                "website": "Web",
                "referral": "Partner Referral",
                "google_ads": "Google AdWords",
                "facebook_ads": "Social Media",
                "trade_show": "Trade Show",
                "email_campaign": "Email"
            }
            sf_data["LeadSource"] = sf_source_map.get(lead.source.value, "Other")

        # Map status
        sf_status_map = {
            "new": "Open - Not Contacted",
            "contacted": "Working - Contacted",
            "qualified": "Closed - Converted",
            "lost": "Closed - Not Converted"
        }
        sf_data["Status"] = sf_status_map.get(lead.status.value, "Open - Not Contacted")

        # Apply custom field mappings
        custom_mappings = self.map_fields_outbound(lead, "leads")
        sf_data.update(custom_mappings)

        # Remove None values
        sf_data = {k: v for k, v in sf_data.items() if v is not None}

        success, response = await self._api_request("POST", "/sobjects/Lead", sf_data)

        if success and response:
            return response.get("id")
        return None

    async def update_lead(self, external_id: str, lead: CRMLead) -> bool:
        """Update lead in Salesforce"""
        sf_data = {
            "Company": lead.organization_name,
            "FirstName": lead.contact_first_name,
            "LastName": lead.contact_last_name,
            "Email": lead.contact_email,
            "Phone": lead.contact_phone,
            "Title": lead.contact_title,
            "Website": lead.website
        }

        # Apply custom field mappings
        custom_mappings = self.map_fields_outbound(lead, "leads")
        sf_data.update(custom_mappings)

        # Remove None values
        sf_data = {k: v for k, v in sf_data.items() if v is not None}

        success, _ = await self._api_request("PATCH", f"/sobjects/Lead/{external_id}", sf_data)
        return success

    async def delete_lead(self, external_id: str) -> bool:
        """Delete lead in Salesforce"""
        success, _ = await self._api_request("DELETE", f"/sobjects/Lead/{external_id}")
        return success

    # ==========================================================================
    # Contact Operations
    # ==========================================================================

    async def get_contacts(
        self,
        modified_since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch contacts from Salesforce"""
        fields = [
            "Id", "FirstName", "LastName", "Email", "Phone", "MobilePhone",
            "Title", "Department", "AccountId", "MailingStreet", "MailingCity",
            "MailingState", "MailingPostalCode", "MailingCountry",
            "CreatedDate", "LastModifiedDate"
        ]

        query = f"SELECT {', '.join(fields)} FROM Contact"

        if modified_since:
            query += f" WHERE LastModifiedDate > {modified_since.strftime('%Y-%m-%dT%H:%M:%SZ')}"

        query += f" ORDER BY LastModifiedDate ASC LIMIT {limit}"

        return await self._soql_query(query)

    async def create_contact(self, contact: CRMContact) -> Optional[str]:
        """Create contact in Salesforce"""
        sf_data = {
            "FirstName": contact.first_name,
            "LastName": contact.last_name,
            "Email": contact.email,
            "Phone": contact.phone,
            "MobilePhone": contact.mobile,
            "Title": contact.title,
            "Department": contact.department
        }

        # Apply custom field mappings
        custom_mappings = self.map_fields_outbound(contact, "contacts")
        sf_data.update(custom_mappings)

        sf_data = {k: v for k, v in sf_data.items() if v is not None}

        success, response = await self._api_request("POST", "/sobjects/Contact", sf_data)

        if success and response:
            return response.get("id")
        return None

    async def update_contact(self, external_id: str, contact: CRMContact) -> bool:
        """Update contact in Salesforce"""
        sf_data = {
            "FirstName": contact.first_name,
            "LastName": contact.last_name,
            "Email": contact.email,
            "Phone": contact.phone,
            "MobilePhone": contact.mobile,
            "Title": contact.title,
            "Department": contact.department
        }

        custom_mappings = self.map_fields_outbound(contact, "contacts")
        sf_data.update(custom_mappings)

        sf_data = {k: v for k, v in sf_data.items() if v is not None}

        success, _ = await self._api_request("PATCH", f"/sobjects/Contact/{external_id}", sf_data)
        return success

    # ==========================================================================
    # Deal/Opportunity Operations
    # ==========================================================================

    async def get_deals(
        self,
        modified_since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch opportunities from Salesforce"""
        fields = [
            "Id", "Name", "Description", "Amount", "StageName", "Probability",
            "CloseDate", "AccountId", "LeadSource", "Type", "NextStep",
            "CreatedDate", "LastModifiedDate"
        ]

        query = f"SELECT {', '.join(fields)} FROM Opportunity"

        if modified_since:
            query += f" WHERE LastModifiedDate > {modified_since.strftime('%Y-%m-%dT%H:%M:%SZ')}"

        query += f" ORDER BY LastModifiedDate ASC LIMIT {limit}"

        return await self._soql_query(query)

    async def create_deal(self, deal: CRMDeal) -> Optional[str]:
        """Create opportunity in Salesforce"""
        # Map stage to Salesforce stage names
        stage_map = {
            DealStage.QUALIFICATION: "Qualification",
            DealStage.NEEDS_ANALYSIS: "Needs Analysis",
            DealStage.PROPOSAL: "Proposal/Price Quote",
            DealStage.NEGOTIATION: "Negotiation/Review",
            DealStage.CLOSED_WON: "Closed Won",
            DealStage.CLOSED_LOST: "Closed Lost"
        }

        sf_data = {
            "Name": deal.name,
            "Description": deal.description,
            "Amount": float(deal.amount) if deal.amount else None,
            "StageName": stage_map.get(deal.stage, "Qualification"),
            "Probability": deal.probability,
            "CloseDate": deal.expected_close_date.isoformat() if deal.expected_close_date else None,
            "NextStep": deal.next_step
        }

        custom_mappings = self.map_fields_outbound(deal, "deals")
        sf_data.update(custom_mappings)

        sf_data = {k: v for k, v in sf_data.items() if v is not None}

        success, response = await self._api_request("POST", "/sobjects/Opportunity", sf_data)

        if success and response:
            return response.get("id")
        return None

    async def update_deal(self, external_id: str, deal: CRMDeal) -> bool:
        """Update opportunity in Salesforce"""
        stage_map = {
            DealStage.QUALIFICATION: "Qualification",
            DealStage.NEEDS_ANALYSIS: "Needs Analysis",
            DealStage.PROPOSAL: "Proposal/Price Quote",
            DealStage.NEGOTIATION: "Negotiation/Review",
            DealStage.CLOSED_WON: "Closed Won",
            DealStage.CLOSED_LOST: "Closed Lost"
        }

        sf_data = {
            "Name": deal.name,
            "Description": deal.description,
            "Amount": float(deal.amount) if deal.amount else None,
            "StageName": stage_map.get(deal.stage, "Qualification"),
            "Probability": deal.probability
        }

        custom_mappings = self.map_fields_outbound(deal, "deals")
        sf_data.update(custom_mappings)

        sf_data = {k: v for k, v in sf_data.items() if v is not None}

        success, _ = await self._api_request("PATCH", f"/sobjects/Opportunity/{external_id}", sf_data)
        return success


# =============================================================================
# HUBSPOT CONNECTOR
# =============================================================================

class HubSpotConnector(BaseCRMConnector):
    """
    HubSpot CRM connector with full API integration.
    Supports OAuth 2.0 and REST API for contacts, deals, and companies.
    """

    BASE_URL = "https://api.hubapi.com"
    AUTH_URL = "https://app.hubspot.com/oauth/authorize"
    TOKEN_URL = "https://api.hubapi.com/oauth/v1/token"

    def __init__(self, integration: ExternalCRMIntegration, session: AsyncSession):
        super().__init__(integration, session)

    @property
    def auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        return {
            "Authorization": f"Bearer {self.integration.access_token}",
            "Content-Type": "application/json"
        }

    async def authenticate(self) -> bool:
        """Authenticate with HubSpot using OAuth 2.0"""
        try:
            response = await self.http_client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.integration.api_key,
                    "client_secret": self.integration.api_secret,
                    "redirect_uri": self._get_redirect_uri(),
                    "code": self.integration.access_token
                }
            )

            if response.status_code == 200:
                data = response.json()
                self.integration.access_token = data["access_token"]
                self.integration.refresh_token = data.get("refresh_token")

                expires_in = data.get("expires_in", 21600)  # Default 6 hours
                self.integration.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

                await self.session.commit()

                logger.info(
                    "hubspot_authenticated",
                    integration_id=str(self.integration.id)
                )
                return True

            return False

        except Exception as e:
            logger.error("hubspot_auth_error", error=str(e))
            return False

    async def refresh_access_token(self) -> bool:
        """Refresh HubSpot OAuth token"""
        try:
            response = await self.http_client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.integration.api_key,
                    "client_secret": self.integration.api_secret,
                    "refresh_token": self.integration.refresh_token
                }
            )

            if response.status_code == 200:
                data = response.json()
                self.integration.access_token = data["access_token"]
                self.integration.refresh_token = data.get("refresh_token", self.integration.refresh_token)

                expires_in = data.get("expires_in", 21600)
                self.integration.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

                await self.session.commit()
                return True

            return False

        except Exception as e:
            logger.error("hubspot_token_refresh_error", error=str(e))
            return False

    def _get_redirect_uri(self) -> str:
        """Get OAuth redirect URI"""
        return "https://app.proficienthub.com/integrations/hubspot/callback"

    async def _api_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Tuple[bool, Optional[Dict]]:
        """Make API request to HubSpot"""
        if not await self.ensure_authenticated():
            return False, None

        url = f"{self.BASE_URL}{endpoint}"

        try:
            if method == "GET":
                response = await self.http_client.get(
                    url, headers=self.auth_headers, params=params
                )
            elif method == "POST":
                response = await self.http_client.post(
                    url, headers=self.auth_headers, json=data
                )
            elif method == "PATCH":
                response = await self.http_client.patch(
                    url, headers=self.auth_headers, json=data
                )
            elif method == "DELETE":
                response = await self.http_client.delete(url, headers=self.auth_headers)
            else:
                return False, None

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After", "10")
                self.integration.rate_limit_remaining = 0
                self.integration.rate_limit_reset_at = datetime.utcnow() + timedelta(seconds=int(retry_after))
                await self.session.commit()
                return False, None

            if response.status_code in [200, 201, 204]:
                return True, response.json() if response.text else None

            return False, {"error": response.text}

        except Exception as e:
            logger.error("hubspot_api_error", error=str(e))
            return False, {"error": str(e)}

    # ==========================================================================
    # Contact Operations (HubSpot uses Contacts, not Leads)
    # ==========================================================================

    async def get_leads(
        self,
        modified_since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch contacts from HubSpot (HubSpot treats leads as contacts)"""
        params = {
            "limit": limit,
            "properties": "firstname,lastname,email,phone,company,jobtitle,website,industry,lifecyclestage"
        }

        if modified_since:
            # HubSpot uses millisecond timestamps
            params["filterGroups"] = json.dumps([{
                "filters": [{
                    "propertyName": "lastmodifieddate",
                    "operator": "GTE",
                    "value": int(modified_since.timestamp() * 1000)
                }]
            }])

        success, response = await self._api_request(
            "GET",
            "/crm/v3/objects/contacts",
            params=params
        )

        if success and response:
            return response.get("results", [])
        return []

    async def create_lead(self, lead: CRMLead) -> Optional[str]:
        """Create contact in HubSpot"""
        hs_data = {
            "properties": {
                "firstname": lead.contact_first_name,
                "lastname": lead.contact_last_name,
                "email": lead.contact_email,
                "phone": lead.contact_phone,
                "company": lead.organization_name,
                "jobtitle": lead.contact_title,
                "website": lead.website,
                "address": lead.address_line1,
                "city": lead.city,
                "state": lead.state,
                "zip": lead.postal_code,
                "country": lead.country,
                "lifecyclestage": "lead"
            }
        }

        # Map lead source
        source_map = {
            "website": "ORGANIC_SEARCH",
            "referral": "REFERRALS",
            "google_ads": "PAID_SEARCH",
            "facebook_ads": "PAID_SOCIAL",
            "email_campaign": "EMAIL_MARKETING"
        }
        if lead.source:
            hs_data["properties"]["hs_lead_status"] = source_map.get(lead.source.value, "OTHER")

        # Remove None values
        hs_data["properties"] = {k: v for k, v in hs_data["properties"].items() if v is not None}

        success, response = await self._api_request("POST", "/crm/v3/objects/contacts", hs_data)

        if success and response:
            return response.get("id")
        return None

    async def update_lead(self, external_id: str, lead: CRMLead) -> bool:
        """Update contact in HubSpot"""
        hs_data = {
            "properties": {
                "firstname": lead.contact_first_name,
                "lastname": lead.contact_last_name,
                "email": lead.contact_email,
                "phone": lead.contact_phone,
                "company": lead.organization_name,
                "jobtitle": lead.contact_title,
                "website": lead.website
            }
        }

        hs_data["properties"] = {k: v for k, v in hs_data["properties"].items() if v is not None}

        success, _ = await self._api_request("PATCH", f"/crm/v3/objects/contacts/{external_id}", hs_data)
        return success

    async def delete_lead(self, external_id: str) -> bool:
        """Delete contact in HubSpot"""
        success, _ = await self._api_request("DELETE", f"/crm/v3/objects/contacts/{external_id}")
        return success

    # ==========================================================================
    # Contact Operations
    # ==========================================================================

    async def get_contacts(
        self,
        modified_since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch contacts from HubSpot"""
        return await self.get_leads(modified_since, limit)

    async def create_contact(self, contact: CRMContact) -> Optional[str]:
        """Create contact in HubSpot"""
        hs_data = {
            "properties": {
                "firstname": contact.first_name,
                "lastname": contact.last_name,
                "email": contact.email,
                "phone": contact.phone,
                "mobilephone": contact.mobile,
                "jobtitle": contact.title
            }
        }

        hs_data["properties"] = {k: v for k, v in hs_data["properties"].items() if v is not None}

        success, response = await self._api_request("POST", "/crm/v3/objects/contacts", hs_data)

        if success and response:
            return response.get("id")
        return None

    async def update_contact(self, external_id: str, contact: CRMContact) -> bool:
        """Update contact in HubSpot"""
        hs_data = {
            "properties": {
                "firstname": contact.first_name,
                "lastname": contact.last_name,
                "email": contact.email,
                "phone": contact.phone,
                "mobilephone": contact.mobile,
                "jobtitle": contact.title
            }
        }

        hs_data["properties"] = {k: v for k, v in hs_data["properties"].items() if v is not None}

        success, _ = await self._api_request("PATCH", f"/crm/v3/objects/contacts/{external_id}", hs_data)
        return success

    # ==========================================================================
    # Deal Operations
    # ==========================================================================

    async def get_deals(
        self,
        modified_since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch deals from HubSpot"""
        params = {
            "limit": limit,
            "properties": "dealname,description,amount,dealstage,closedate,pipeline"
        }

        success, response = await self._api_request(
            "GET",
            "/crm/v3/objects/deals",
            params=params
        )

        if success and response:
            return response.get("results", [])
        return []

    async def create_deal(self, deal: CRMDeal) -> Optional[str]:
        """Create deal in HubSpot"""
        # Map stage to HubSpot default stages
        stage_map = {
            DealStage.QUALIFICATION: "appointmentscheduled",
            DealStage.NEEDS_ANALYSIS: "qualifiedtobuy",
            DealStage.PROPOSAL: "presentationscheduled",
            DealStage.NEGOTIATION: "decisionmakerboughtin",
            DealStage.CLOSED_WON: "closedwon",
            DealStage.CLOSED_LOST: "closedlost"
        }

        hs_data = {
            "properties": {
                "dealname": deal.name,
                "description": deal.description,
                "amount": str(deal.amount) if deal.amount else None,
                "dealstage": stage_map.get(deal.stage, "appointmentscheduled"),
                "closedate": deal.expected_close_date.isoformat() if deal.expected_close_date else None
            }
        }

        hs_data["properties"] = {k: v for k, v in hs_data["properties"].items() if v is not None}

        success, response = await self._api_request("POST", "/crm/v3/objects/deals", hs_data)

        if success and response:
            return response.get("id")
        return None

    async def update_deal(self, external_id: str, deal: CRMDeal) -> bool:
        """Update deal in HubSpot"""
        stage_map = {
            DealStage.QUALIFICATION: "appointmentscheduled",
            DealStage.NEEDS_ANALYSIS: "qualifiedtobuy",
            DealStage.PROPOSAL: "presentationscheduled",
            DealStage.NEGOTIATION: "decisionmakerboughtin",
            DealStage.CLOSED_WON: "closedwon",
            DealStage.CLOSED_LOST: "closedlost"
        }

        hs_data = {
            "properties": {
                "dealname": deal.name,
                "description": deal.description,
                "amount": str(deal.amount) if deal.amount else None,
                "dealstage": stage_map.get(deal.stage, "appointmentscheduled")
            }
        }

        hs_data["properties"] = {k: v for k, v in hs_data["properties"].items() if v is not None}

        success, _ = await self._api_request("PATCH", f"/crm/v3/objects/deals/{external_id}", hs_data)
        return success


# =============================================================================
# ZOHO CRM CONNECTOR
# =============================================================================

class ZohoCRMConnector(BaseCRMConnector):
    """
    Zoho CRM connector with full API integration.
    Supports OAuth 2.0 and REST API for leads, contacts, and deals.
    """

    AUTH_URL = "https://accounts.zoho.com/oauth/v2"
    API_URL = "https://www.zohoapis.com/crm/v3"

    def __init__(self, integration: ExternalCRMIntegration, session: AsyncSession):
        super().__init__(integration, session)
        # Zoho has region-specific URLs
        self.api_url = integration.instance_url or self.API_URL

    @property
    def auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        return {
            "Authorization": f"Zoho-oauthtoken {self.integration.access_token}",
            "Content-Type": "application/json"
        }

    async def authenticate(self) -> bool:
        """Authenticate with Zoho using OAuth 2.0"""
        try:
            response = await self.http_client.post(
                f"{self.AUTH_URL}/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.integration.api_key,
                    "client_secret": self.integration.api_secret,
                    "redirect_uri": self._get_redirect_uri(),
                    "code": self.integration.access_token
                }
            )

            if response.status_code == 200:
                data = response.json()
                self.integration.access_token = data["access_token"]
                self.integration.refresh_token = data.get("refresh_token")

                # Zoho tokens expire in 1 hour
                expires_in = data.get("expires_in", 3600)
                self.integration.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

                # Store API domain
                if "api_domain" in data:
                    self.integration.instance_url = data["api_domain"]
                    self.api_url = f"{data['api_domain']}/crm/v3"

                await self.session.commit()

                logger.info(
                    "zoho_authenticated",
                    integration_id=str(self.integration.id)
                )
                return True

            return False

        except Exception as e:
            logger.error("zoho_auth_error", error=str(e))
            return False

    async def refresh_access_token(self) -> bool:
        """Refresh Zoho OAuth token"""
        try:
            response = await self.http_client.post(
                f"{self.AUTH_URL}/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.integration.api_key,
                    "client_secret": self.integration.api_secret,
                    "refresh_token": self.integration.refresh_token
                }
            )

            if response.status_code == 200:
                data = response.json()
                self.integration.access_token = data["access_token"]

                expires_in = data.get("expires_in", 3600)
                self.integration.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

                await self.session.commit()
                return True

            return False

        except Exception as e:
            logger.error("zoho_token_refresh_error", error=str(e))
            return False

    def _get_redirect_uri(self) -> str:
        """Get OAuth redirect URI"""
        return "https://app.proficienthub.com/integrations/zoho/callback"

    async def _api_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Tuple[bool, Optional[Dict]]:
        """Make API request to Zoho CRM"""
        if not await self.ensure_authenticated():
            return False, None

        url = f"{self.api_url}{endpoint}"

        try:
            if method == "GET":
                response = await self.http_client.get(
                    url, headers=self.auth_headers, params=params
                )
            elif method == "POST":
                response = await self.http_client.post(
                    url, headers=self.auth_headers, json=data
                )
            elif method == "PUT":
                response = await self.http_client.put(
                    url, headers=self.auth_headers, json=data
                )
            elif method == "DELETE":
                response = await self.http_client.delete(url, headers=self.auth_headers)
            else:
                return False, None

            # Handle rate limiting
            if response.status_code == 429:
                self.integration.rate_limit_remaining = 0
                self.integration.rate_limit_reset_at = datetime.utcnow() + timedelta(minutes=1)
                await self.session.commit()
                return False, None

            if response.status_code in [200, 201, 202, 204]:
                return True, response.json() if response.text else None

            return False, {"error": response.text}

        except Exception as e:
            logger.error("zoho_api_error", error=str(e))
            return False, {"error": str(e)}

    # ==========================================================================
    # Lead Operations
    # ==========================================================================

    async def get_leads(
        self,
        modified_since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch leads from Zoho CRM"""
        params = {"per_page": limit}

        if modified_since:
            # Use If-Modified-Since header instead of query param
            self.http_client.headers["If-Modified-Since"] = modified_since.strftime("%Y-%m-%dT%H:%M:%S%z")

        success, response = await self._api_request("GET", "/Leads", params=params)

        if success and response:
            return response.get("data", [])
        return []

    async def create_lead(self, lead: CRMLead) -> Optional[str]:
        """Create lead in Zoho CRM"""
        zoho_data = {
            "data": [{
                "Company": lead.organization_name,
                "First_Name": lead.contact_first_name,
                "Last_Name": lead.contact_last_name,
                "Email": lead.contact_email,
                "Phone": lead.contact_phone,
                "Designation": lead.contact_title,
                "Website": lead.website,
                "Description": lead.notes,
                "Street": lead.address_line1,
                "City": lead.city,
                "State": lead.state,
                "Zip_Code": lead.postal_code,
                "Country": lead.country
            }]
        }

        # Map lead source
        source_map = {
            "website": "Website",
            "referral": "Referral",
            "google_ads": "Google AdWords",
            "facebook_ads": "Facebook",
            "trade_show": "Trade Show",
            "email_campaign": "Email"
        }
        if lead.source:
            zoho_data["data"][0]["Lead_Source"] = source_map.get(lead.source.value, "Other")

        # Map lead status
        status_map = {
            "new": "Not Contacted",
            "contacted": "Contacted",
            "qualified": "Contact in Future",
            "lost": "Lost Lead"
        }
        zoho_data["data"][0]["Lead_Status"] = status_map.get(lead.status.value, "Not Contacted")

        # Remove None values
        zoho_data["data"][0] = {k: v for k, v in zoho_data["data"][0].items() if v is not None}

        success, response = await self._api_request("POST", "/Leads", zoho_data)

        if success and response:
            data = response.get("data", [])
            if data:
                return data[0].get("details", {}).get("id")
        return None

    async def update_lead(self, external_id: str, lead: CRMLead) -> bool:
        """Update lead in Zoho CRM"""
        zoho_data = {
            "data": [{
                "id": external_id,
                "Company": lead.organization_name,
                "First_Name": lead.contact_first_name,
                "Last_Name": lead.contact_last_name,
                "Email": lead.contact_email,
                "Phone": lead.contact_phone,
                "Designation": lead.contact_title,
                "Website": lead.website
            }]
        }

        zoho_data["data"][0] = {k: v for k, v in zoho_data["data"][0].items() if v is not None}

        success, _ = await self._api_request("PUT", "/Leads", zoho_data)
        return success

    async def delete_lead(self, external_id: str) -> bool:
        """Delete lead in Zoho CRM"""
        success, _ = await self._api_request("DELETE", f"/Leads/{external_id}")
        return success

    # ==========================================================================
    # Contact Operations
    # ==========================================================================

    async def get_contacts(
        self,
        modified_since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch contacts from Zoho CRM"""
        params = {"per_page": limit}

        success, response = await self._api_request("GET", "/Contacts", params=params)

        if success and response:
            return response.get("data", [])
        return []

    async def create_contact(self, contact: CRMContact) -> Optional[str]:
        """Create contact in Zoho CRM"""
        zoho_data = {
            "data": [{
                "First_Name": contact.first_name,
                "Last_Name": contact.last_name,
                "Email": contact.email,
                "Phone": contact.phone,
                "Mobile": contact.mobile,
                "Title": contact.title,
                "Department": contact.department
            }]
        }

        zoho_data["data"][0] = {k: v for k, v in zoho_data["data"][0].items() if v is not None}

        success, response = await self._api_request("POST", "/Contacts", zoho_data)

        if success and response:
            data = response.get("data", [])
            if data:
                return data[0].get("details", {}).get("id")
        return None

    async def update_contact(self, external_id: str, contact: CRMContact) -> bool:
        """Update contact in Zoho CRM"""
        zoho_data = {
            "data": [{
                "id": external_id,
                "First_Name": contact.first_name,
                "Last_Name": contact.last_name,
                "Email": contact.email,
                "Phone": contact.phone,
                "Mobile": contact.mobile,
                "Title": contact.title
            }]
        }

        zoho_data["data"][0] = {k: v for k, v in zoho_data["data"][0].items() if v is not None}

        success, _ = await self._api_request("PUT", "/Contacts", zoho_data)
        return success

    # ==========================================================================
    # Deal Operations
    # ==========================================================================

    async def get_deals(
        self,
        modified_since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch deals from Zoho CRM"""
        params = {"per_page": limit}

        success, response = await self._api_request("GET", "/Deals", params=params)

        if success and response:
            return response.get("data", [])
        return []

    async def create_deal(self, deal: CRMDeal) -> Optional[str]:
        """Create deal in Zoho CRM"""
        stage_map = {
            DealStage.QUALIFICATION: "Qualification",
            DealStage.NEEDS_ANALYSIS: "Needs Analysis",
            DealStage.PROPOSAL: "Proposal/Price Quote",
            DealStage.NEGOTIATION: "Negotiation/Review",
            DealStage.CLOSED_WON: "Closed Won",
            DealStage.CLOSED_LOST: "Closed Lost"
        }

        zoho_data = {
            "data": [{
                "Deal_Name": deal.name,
                "Description": deal.description,
                "Amount": float(deal.amount) if deal.amount else None,
                "Stage": stage_map.get(deal.stage, "Qualification"),
                "Probability": deal.probability,
                "Closing_Date": deal.expected_close_date.isoformat() if deal.expected_close_date else None
            }]
        }

        zoho_data["data"][0] = {k: v for k, v in zoho_data["data"][0].items() if v is not None}

        success, response = await self._api_request("POST", "/Deals", zoho_data)

        if success and response:
            data = response.get("data", [])
            if data:
                return data[0].get("details", {}).get("id")
        return None

    async def update_deal(self, external_id: str, deal: CRMDeal) -> bool:
        """Update deal in Zoho CRM"""
        stage_map = {
            DealStage.QUALIFICATION: "Qualification",
            DealStage.NEEDS_ANALYSIS: "Needs Analysis",
            DealStage.PROPOSAL: "Proposal/Price Quote",
            DealStage.NEGOTIATION: "Negotiation/Review",
            DealStage.CLOSED_WON: "Closed Won",
            DealStage.CLOSED_LOST: "Closed Lost"
        }

        zoho_data = {
            "data": [{
                "id": external_id,
                "Deal_Name": deal.name,
                "Description": deal.description,
                "Amount": float(deal.amount) if deal.amount else None,
                "Stage": stage_map.get(deal.stage, "Qualification"),
                "Probability": deal.probability
            }]
        }

        zoho_data["data"][0] = {k: v for k, v in zoho_data["data"][0].items() if v is not None}

        success, _ = await self._api_request("PUT", "/Deals", zoho_data)
        return success


# =============================================================================
# CUSTOM WEBHOOK CONNECTOR
# =============================================================================

class CustomWebhookConnector(BaseCRMConnector):
    """
    Custom webhook connector for any CRM system.
    Sends signed payloads to configured webhook URLs.
    """

    def __init__(self, integration: ExternalCRMIntegration, session: AsyncSession):
        super().__init__(integration, session)
        self.webhook_url = integration.webhook_url
        self.webhook_secret = integration.webhook_secret

    async def authenticate(self) -> bool:
        """Webhook connector doesn't need authentication"""
        return True

    async def refresh_access_token(self) -> bool:
        """Webhook connector doesn't use tokens"""
        return True

    def _generate_signature(self, payload: str, timestamp: str) -> str:
        """Generate HMAC signature for webhook payload"""
        if not self.webhook_secret:
            return ""

        message = f"{timestamp}.{payload}"
        signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return signature

    async def _send_webhook(
        self,
        event_type: str,
        entity_type: str,
        entity_id: str,
        data: Dict[str, Any]
    ) -> bool:
        """Send webhook with signed payload"""
        if not self.webhook_url:
            return False

        timestamp = str(int(time.time()))
        payload = {
            "event": event_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "data": data,
            "timestamp": timestamp,
            "integration_id": str(self.integration.id)
        }

        payload_str = json.dumps(payload, sort_keys=True)
        signature = self._generate_signature(payload_str, timestamp)

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Timestamp": timestamp,
            "X-Integration-ID": str(self.integration.id)
        }

        try:
            response = await self.http_client.post(
                self.webhook_url,
                headers=headers,
                content=payload_str,
                timeout=30.0
            )

            success = response.status_code in [200, 201, 202, 204]

            logger.info(
                "webhook_sent",
                integration_id=str(self.integration.id),
                event_type=event_type,
                entity_type=entity_type,
                status_code=response.status_code,
                success=success
            )

            return success

        except Exception as e:
            logger.error(
                "webhook_send_error",
                integration_id=str(self.integration.id),
                error=str(e)
            )
            return False

    # ==========================================================================
    # Lead Operations
    # ==========================================================================

    async def get_leads(
        self,
        modified_since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Webhook connector is push-only, no inbound sync"""
        return []

    async def create_lead(self, lead: CRMLead) -> Optional[str]:
        """Send lead creation webhook"""
        data = {
            "id": str(lead.id),
            "organization_name": lead.organization_name,
            "contact_first_name": lead.contact_first_name,
            "contact_last_name": lead.contact_last_name,
            "contact_email": lead.contact_email,
            "contact_phone": lead.contact_phone,
            "source": lead.source.value if lead.source else None,
            "status": lead.status.value if lead.status else None,
            "lead_score": lead.lead_score,
            "created_at": lead.created_at.isoformat() if lead.created_at else None
        }

        # Apply custom field mappings
        custom_mappings = self.map_fields_outbound(lead, "leads")
        data.update(custom_mappings)

        success = await self._send_webhook("lead.created", "lead", str(lead.id), data)

        # Return internal ID as external ID for tracking
        return str(lead.id) if success else None

    async def update_lead(self, external_id: str, lead: CRMLead) -> bool:
        """Send lead update webhook"""
        data = {
            "id": str(lead.id),
            "organization_name": lead.organization_name,
            "contact_first_name": lead.contact_first_name,
            "contact_last_name": lead.contact_last_name,
            "contact_email": lead.contact_email,
            "status": lead.status.value if lead.status else None,
            "lead_score": lead.lead_score,
            "updated_at": lead.updated_at.isoformat() if lead.updated_at else None
        }

        custom_mappings = self.map_fields_outbound(lead, "leads")
        data.update(custom_mappings)

        return await self._send_webhook("lead.updated", "lead", str(lead.id), data)

    async def delete_lead(self, external_id: str) -> bool:
        """Send lead deletion webhook"""
        return await self._send_webhook("lead.deleted", "lead", external_id, {"id": external_id})

    # ==========================================================================
    # Contact Operations
    # ==========================================================================

    async def get_contacts(
        self,
        modified_since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Webhook connector is push-only"""
        return []

    async def create_contact(self, contact: CRMContact) -> Optional[str]:
        """Send contact creation webhook"""
        data = {
            "id": str(contact.id),
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "email": contact.email,
            "phone": contact.phone,
            "title": contact.title,
            "created_at": contact.created_at.isoformat() if contact.created_at else None
        }

        custom_mappings = self.map_fields_outbound(contact, "contacts")
        data.update(custom_mappings)

        success = await self._send_webhook("contact.created", "contact", str(contact.id), data)
        return str(contact.id) if success else None

    async def update_contact(self, external_id: str, contact: CRMContact) -> bool:
        """Send contact update webhook"""
        data = {
            "id": str(contact.id),
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "email": contact.email,
            "phone": contact.phone,
            "updated_at": contact.updated_at.isoformat() if contact.updated_at else None
        }

        custom_mappings = self.map_fields_outbound(contact, "contacts")
        data.update(custom_mappings)

        return await self._send_webhook("contact.updated", "contact", str(contact.id), data)

    # ==========================================================================
    # Deal Operations
    # ==========================================================================

    async def get_deals(
        self,
        modified_since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Webhook connector is push-only"""
        return []

    async def create_deal(self, deal: CRMDeal) -> Optional[str]:
        """Send deal creation webhook"""
        data = {
            "id": str(deal.id),
            "name": deal.name,
            "amount": float(deal.amount) if deal.amount else None,
            "stage": deal.stage.value if deal.stage else None,
            "probability": deal.probability,
            "expected_close_date": deal.expected_close_date.isoformat() if deal.expected_close_date else None,
            "created_at": deal.created_at.isoformat() if deal.created_at else None
        }

        custom_mappings = self.map_fields_outbound(deal, "deals")
        data.update(custom_mappings)

        success = await self._send_webhook("deal.created", "deal", str(deal.id), data)
        return str(deal.id) if success else None

    async def update_deal(self, external_id: str, deal: CRMDeal) -> bool:
        """Send deal update webhook"""
        data = {
            "id": str(deal.id),
            "name": deal.name,
            "amount": float(deal.amount) if deal.amount else None,
            "stage": deal.stage.value if deal.stage else None,
            "probability": deal.probability,
            "updated_at": deal.updated_at.isoformat() if deal.updated_at else None
        }

        custom_mappings = self.map_fields_outbound(deal, "deals")
        data.update(custom_mappings)

        return await self._send_webhook("deal.updated", "deal", str(deal.id), data)


# =============================================================================
# CONNECTOR FACTORY
# =============================================================================

class CRMConnectorFactory:
    """
    Factory for creating CRM connectors based on integration type.
    """

    _connectors: Dict[ExternalCRMType, Type[BaseCRMConnector]] = {
        ExternalCRMType.SALESFORCE: SalesforceConnector,
        ExternalCRMType.HUBSPOT: HubSpotConnector,
        ExternalCRMType.ZOHO: ZohoCRMConnector,
        ExternalCRMType.CUSTOM_WEBHOOK: CustomWebhookConnector
    }

    @classmethod
    def create(
        cls,
        integration: ExternalCRMIntegration,
        session: AsyncSession
    ) -> BaseCRMConnector:
        """
        Create a CRM connector instance.

        Args:
            integration: Integration configuration
            session: Database session

        Returns:
            CRM connector instance

        Raises:
            ValueError: If CRM type is not supported
        """
        connector_class = cls._connectors.get(integration.crm_type)

        if not connector_class:
            raise ValueError(f"Unsupported CRM type: {integration.crm_type}")

        return connector_class(integration, session)

    @classmethod
    def register_connector(
        cls,
        crm_type: ExternalCRMType,
        connector_class: Type[BaseCRMConnector]
    ):
        """Register a custom connector"""
        cls._connectors[crm_type] = connector_class


# =============================================================================
# SYNC SCHEDULER
# =============================================================================

class CRMSyncScheduler:
    """
    Scheduler for running CRM sync operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self._running = False

    async def run_due_syncs(self) -> List[CRMSyncLog]:
        """Run all integrations that are due for sync"""
        # Find integrations that need syncing
        result = await self.session.execute(
            select(ExternalCRMIntegration).where(
                ExternalCRMIntegration.is_active == True,
                ExternalCRMIntegration.is_deleted == False
            )
        )
        integrations = result.scalars().all()

        logs = []
        for integration in integrations:
            if integration.should_sync():
                try:
                    connector = CRMConnectorFactory.create(integration, self.session)
                    sync_logs = await connector.full_sync()
                    logs.extend(sync_logs)
                    await connector.close()
                except Exception as e:
                    logger.error(
                        "sync_scheduler_error",
                        integration_id=str(integration.id),
                        error=str(e)
                    )

        return logs

    async def start(self, interval_seconds: int = 300):
        """Start the sync scheduler"""
        self._running = True

        while self._running:
            try:
                await self.run_due_syncs()
            except Exception as e:
                logger.error("sync_scheduler_loop_error", error=str(e))

            await asyncio.sleep(interval_seconds)

    def stop(self):
        """Stop the sync scheduler"""
        self._running = False


# =============================================================================
# WEBHOOK RECEIVER
# =============================================================================

class WebhookReceiver:
    """
    Receiver for incoming webhooks from external CRMs.
    Handles webhook verification and processing.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def verify_webhook(
        self,
        integration_id: UUID,
        signature: str,
        timestamp: str,
        payload: str
    ) -> bool:
        """Verify incoming webhook signature"""
        result = await self.session.execute(
            select(ExternalCRMIntegration).where(
                ExternalCRMIntegration.id == integration_id,
                ExternalCRMIntegration.is_active == True
            )
        )
        integration = result.scalar_one_or_none()

        if not integration or not integration.webhook_secret:
            return False

        # Verify timestamp is recent (within 5 minutes)
        try:
            ts = int(timestamp)
            if abs(time.time() - ts) > 300:
                return False
        except ValueError:
            return False

        # Verify signature
        message = f"{timestamp}.{payload}"
        expected_signature = hmac.new(
            integration.webhook_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    async def process_webhook(
        self,
        integration_id: UUID,
        event_type: str,
        entity_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """Process incoming webhook"""
        result = await self.session.execute(
            select(ExternalCRMIntegration).where(
                ExternalCRMIntegration.id == integration_id
            )
        )
        integration = result.scalar_one_or_none()

        if not integration:
            return False

        try:
            # Handle different event types
            if entity_type == "lead":
                await self._process_lead_webhook(integration, event_type, data)
            elif entity_type == "contact":
                await self._process_contact_webhook(integration, event_type, data)
            elif entity_type == "deal":
                await self._process_deal_webhook(integration, event_type, data)

            await self.session.commit()
            return True

        except Exception as e:
            logger.error(
                "webhook_processing_error",
                integration_id=str(integration_id),
                event_type=event_type,
                error=str(e)
            )
            return False

    async def _process_lead_webhook(
        self,
        integration: ExternalCRMIntegration,
        event_type: str,
        data: Dict[str, Any]
    ):
        """Process lead webhook"""
        external_id = data.get("id")

        if event_type in ["lead.created", "lead.updated"]:
            # Check if lead exists
            result = await self.session.execute(
                select(CRMLead).where(
                    CRMLead.external_crm_id == external_id,
                    CRMLead.external_crm_type == integration.crm_type
                )
            )
            lead = result.scalar_one_or_none()

            # Map fields
            connector = CRMConnectorFactory.create(integration, self.session)
            mapped_data = connector.map_fields_inbound(data, "leads")
            await connector.close()

            if lead:
                # Update existing
                for field, value in mapped_data.items():
                    if hasattr(lead, field):
                        setattr(lead, field, value)
                lead.last_synced_at = datetime.utcnow()
            elif event_type == "lead.created":
                # Create new
                lead = CRMLead(
                    external_crm_id=external_id,
                    external_crm_type=integration.crm_type,
                    last_synced_at=datetime.utcnow(),
                    **mapped_data
                )
                self.session.add(lead)

        elif event_type == "lead.deleted":
            # Soft delete
            await self.session.execute(
                update(CRMLead).where(
                    CRMLead.external_crm_id == external_id,
                    CRMLead.external_crm_type == integration.crm_type
                ).values(is_deleted=True, deleted_at=datetime.utcnow())
            )

    async def _process_contact_webhook(
        self,
        integration: ExternalCRMIntegration,
        event_type: str,
        data: Dict[str, Any]
    ):
        """Process contact webhook"""
        # Similar implementation to lead webhook
        pass

    async def _process_deal_webhook(
        self,
        integration: ExternalCRMIntegration,
        event_type: str,
        data: Dict[str, Any]
    ):
        """Process deal webhook"""
        # Similar implementation to lead webhook
        pass


# =============================================================================
# INTEGRATION SERVICE
# =============================================================================

class ExternalCRMService:
    """
    High-level service for managing external CRM integrations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.webhook_receiver = WebhookReceiver(session)

    async def create_integration(
        self,
        academy_id: UUID,
        crm_type: ExternalCRMType,
        integration_name: str,
        **kwargs
    ) -> ExternalCRMIntegration:
        """Create a new CRM integration"""
        integration = ExternalCRMIntegration(
            academy_id=academy_id,
            crm_type=crm_type,
            integration_name=integration_name,
            **kwargs
        )

        self.session.add(integration)
        await self.session.commit()
        await self.session.refresh(integration)

        logger.info(
            "integration_created",
            integration_id=str(integration.id),
            crm_type=crm_type.value
        )

        return integration

    async def get_oauth_url(
        self,
        integration_id: UUID
    ) -> Optional[str]:
        """Get OAuth authorization URL for an integration"""
        result = await self.session.execute(
            select(ExternalCRMIntegration).where(
                ExternalCRMIntegration.id == integration_id
            )
        )
        integration = result.scalar_one_or_none()

        if not integration:
            return None

        base_urls = {
            ExternalCRMType.SALESFORCE: "https://login.salesforce.com/services/oauth2/authorize",
            ExternalCRMType.HUBSPOT: "https://app.hubspot.com/oauth/authorize",
            ExternalCRMType.ZOHO: "https://accounts.zoho.com/oauth/v2/auth"
        }

        base_url = base_urls.get(integration.crm_type)
        if not base_url:
            return None

        params = {
            "client_id": integration.api_key,
            "redirect_uri": f"https://app.proficienthub.com/integrations/{integration.crm_type.value}/callback",
            "response_type": "code",
            "state": str(integration.id)
        }

        # Add CRM-specific params
        if integration.crm_type == ExternalCRMType.SALESFORCE:
            params["scope"] = "api refresh_token"
        elif integration.crm_type == ExternalCRMType.HUBSPOT:
            params["scope"] = "crm.objects.contacts.read crm.objects.contacts.write crm.objects.deals.read crm.objects.deals.write"
        elif integration.crm_type == ExternalCRMType.ZOHO:
            params["scope"] = "ZohoCRM.modules.ALL ZohoCRM.settings.ALL"
            params["access_type"] = "offline"

        return f"{base_url}?{urlencode(params)}"

    async def complete_oauth(
        self,
        integration_id: UUID,
        auth_code: str
    ) -> bool:
        """Complete OAuth flow with authorization code"""
        result = await self.session.execute(
            select(ExternalCRMIntegration).where(
                ExternalCRMIntegration.id == integration_id
            )
        )
        integration = result.scalar_one_or_none()

        if not integration:
            return False

        # Store auth code temporarily
        integration.access_token = auth_code

        connector = CRMConnectorFactory.create(integration, self.session)
        success = await connector.authenticate()
        await connector.close()

        return success

    async def trigger_sync(
        self,
        integration_id: UUID,
        full_sync: bool = False
    ) -> List[CRMSyncLog]:
        """Trigger sync for an integration"""
        result = await self.session.execute(
            select(ExternalCRMIntegration).where(
                ExternalCRMIntegration.id == integration_id,
                ExternalCRMIntegration.is_active == True
            )
        )
        integration = result.scalar_one_or_none()

        if not integration:
            raise ValueError(f"Integration {integration_id} not found or inactive")

        connector = CRMConnectorFactory.create(integration, self.session)
        logs = await connector.full_sync()
        await connector.close()

        return logs

    async def test_connection(
        self,
        integration_id: UUID
    ) -> Dict[str, Any]:
        """Test connection to external CRM"""
        result = await self.session.execute(
            select(ExternalCRMIntegration).where(
                ExternalCRMIntegration.id == integration_id
            )
        )
        integration = result.scalar_one_or_none()

        if not integration:
            return {"success": False, "error": "Integration not found"}

        try:
            connector = CRMConnectorFactory.create(integration, self.session)

            if not await connector.ensure_authenticated():
                return {"success": False, "error": "Authentication failed"}

            # Try to fetch a small amount of data
            leads = await connector.get_leads(limit=1)
            await connector.close()

            return {
                "success": True,
                "message": "Connection successful",
                "sample_record_count": len(leads)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
