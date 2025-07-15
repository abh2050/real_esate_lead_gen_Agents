"""
Shared state models and types for the Real Estate Lead Generation system
"""

from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class Lead(BaseModel):
    """Individual lead data structure"""
    id: str = Field(description="Unique lead identifier")
    
    # Property Information
    address: str = Field(description="Property address")
    city: str = Field(description="City")
    state: str = Field(description="State")
    zip_code: str = Field(description="ZIP code")
    property_type: str = Field(description="Type of property (single-family, duplex, etc.)")
    price: Optional[float] = Field(None, description="Listed price")
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms")
    bathrooms: Optional[float] = Field(None, description="Number of bathrooms")
    square_feet: Optional[int] = Field(None, description="Square footage")
    lot_size: Optional[float] = Field(None, description="Lot size in acres")
    year_built: Optional[int] = Field(None, description="Year built")
    
    # Owner Information
    owner_name: Optional[str] = Field(None, description="Property owner name")
    owner_phone: Optional[str] = Field(None, description="Owner phone number")
    owner_email: Optional[str] = Field(None, description="Owner email")
    mailing_address: Optional[str] = Field(None, description="Owner mailing address")
    
    # Lead Scoring
    score: Optional[float] = Field(None, description="Lead quality score (0-100)")
    motivation_indicators: List[str] = Field(default_factory=list, description="Signs of seller motivation")
    equity_estimate: Optional[float] = Field(None, description="Estimated equity amount")
    
    # Metadata
    source: str = Field(description="Data source (Zillow, MLS, etc.)")
    found_date: datetime = Field(default_factory=datetime.now, description="When lead was found")
    status: Literal["new", "reviewed", "approved", "rejected", "contacted"] = Field(default="new")
    notes: Optional[str] = Field(None, description="Human reviewer notes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional lead metadata")
    
    # Human-in-the-Loop
    human_reviewed: bool = Field(default=False, description="Has been reviewed by human")
    human_approved: bool = Field(default=False, description="Approved by human reviewer")

class SearchCriteria(BaseModel):
    """Search criteria for lead generation"""
    location: str = Field(description="Target location (city, state, or ZIP)")
    property_types: List[str] = Field(default=["single-family", "duplex", "townhouse"])
    price_min: Optional[float] = Field(None, description="Minimum price")
    price_max: Optional[float] = Field(None, description="Maximum price")
    lead_type: Literal["buyer", "seller", "investor"] = Field(default="seller")
    motivation_signals: List[str] = Field(default_factory=list, description="Specific motivation indicators to look for")

class AgentState(BaseModel):
    """Shared state passed between agents in the workflow"""
    
    # Input
    user_query: str = Field(description="Original user query")
    search_criteria: Optional[SearchCriteria] = Field(None, description="Parsed search criteria")
    
    # Agent Results
    raw_listings: List[Dict[str, Any]] = Field(default_factory=list, description="Raw property listings")
    filtered_listings: List[Dict[str, Any]] = Field(default_factory=list, description="Filtered listings")
    enriched_leads: List[Lead] = Field(default_factory=list, description="Enriched lead data")
    scored_leads: List[Lead] = Field(default_factory=list, description="Scored leads")
    
    # Human-in-the-Loop
    human_reviewed_leads: List[Lead] = Field(default_factory=list, description="Human-approved leads")
    
    # Output
    final_leads: List[Lead] = Field(default_factory=list, description="Final processed leads")
    output_file: Optional[str] = Field(None, description="Path to output file")
    
    # Workflow metadata
    current_step: str = Field(default="intent", description="Current workflow step")
    errors: List[str] = Field(default_factory=list, description="Workflow errors")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class WorkflowConfig(BaseModel):
    """Configuration for the lead generation workflow"""
    
    # API Keys and Settings
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    google_api_key: Optional[str] = Field(None, description="Google API key")
    zillow_api_key: Optional[str] = Field(None, description="Zillow API key")
    
    # Workflow Settings
    max_leads_per_search: int = Field(default=50, description="Maximum leads to process per search")
    require_human_review: bool = Field(default=True, description="Require human review before output")
    auto_export: bool = Field(default=False, description="Automatically export after human review")
    
    # Output Settings
    output_format: Literal["csv", "json", "google_sheets", "airtable"] = Field(default="csv")
    output_directory: str = Field(default="./outputs", description="Directory for output files")
    
    # Scoring Settings
    min_lead_score: float = Field(default=30.0, description="Minimum score for lead inclusion")
    prioritize_motivation: bool = Field(default=True, description="Prioritize motivated sellers")
