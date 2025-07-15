"""
Enrichment Agent - Enriches property listings with owner contact information
"""

import asyncio
import random
import string
from typing import Dict, List, Any, Optional
from utils.models import AgentState, Lead
from datetime import datetime
import re

class EnrichmentAgent:
    """Agent responsible for enriching property data with owner contact information"""
    
    def __init__(self):
        self.enrichment_sources = {
            "property_records": self._enrich_from_property_records,
            "skiptracing": self._enrich_from_skiptracing,
            "social_media": self._enrich_from_social_media,
            "public_records": self._enrich_from_public_records
        }
    
    async def process(self, state: AgentState) -> AgentState:
        """Enrich filtered listings with contact information"""
        try:
            if not state.filtered_listings:
                raise ValueError("No filtered listings to enrich")
            
            print(f"📞 Enriching {len(state.filtered_listings)} listings with contact data...")
            
            enriched_leads = []
            
            # Process each listing
            for i, listing in enumerate(state.filtered_listings):
                print(f"   🔍 Enriching listing {i+1}/{len(state.filtered_listings)}")
                
                # Convert listing to Lead object
                lead = self._convert_listing_to_lead(listing)
                
                # Enrich with contact information
                enriched_lead = await self._enrich_lead(lead)
                
                enriched_leads.append(enriched_lead)
                
                # Small delay to simulate real enrichment
                await asyncio.sleep(0.1)
            
            state.enriched_leads = enriched_leads
            state.current_step = "scoring"
            
            # Count successful enrichments
            enriched_count = sum(1 for lead in enriched_leads if lead.owner_phone or lead.owner_email)
            print(f"✅ Enrichment Complete: {enriched_count}/{len(enriched_leads)} leads have contact info")
            
            return state
            
        except Exception as e:
            error_msg = f"Enrichment Agent error: {str(e)}"
            state.errors.append(error_msg)
            print(f"❌ {error_msg}")
            return state
    
    def _convert_listing_to_lead(self, listing: Dict[str, Any]) -> Lead:
        """Convert raw listing data to Lead object"""
        return Lead(
            id=f"lead_{random.randint(100000, 999999)}",
            address=listing.get('address', ''),
            city=listing.get('city', ''),
            state=listing.get('state', ''),
            zip_code=listing.get('zip_code', ''),
            property_type=listing.get('property_type', ''),
            price=listing.get('price'),
            bedrooms=listing.get('bedrooms'),
            bathrooms=listing.get('bathrooms'),
            square_feet=listing.get('square_feet'),
            lot_size=listing.get('lot_size'),
            year_built=listing.get('year_built'),
            source=listing.get('source', ''),
            motivation_indicators=listing.get('motivation_signals', []),
            found_date=datetime.now()
        )
    
    async def _enrich_lead(self, lead: Lead) -> Lead:
        """Enrich a single lead with contact information"""
        # Try each enrichment source
        for source_name, enrich_func in self.enrichment_sources.items():
            try:
                enriched_data = await enrich_func(lead)
                
                # Update lead with enriched data
                if enriched_data.get('owner_name'):
                    lead.owner_name = enriched_data['owner_name']
                if enriched_data.get('owner_phone'):
                    lead.owner_phone = enriched_data['owner_phone']
                if enriched_data.get('owner_email'):
                    lead.owner_email = enriched_data['owner_email']
                if enriched_data.get('mailing_address'):
                    lead.mailing_address = enriched_data['mailing_address']
                if enriched_data.get('equity_estimate'):
                    lead.equity_estimate = enriched_data['equity_estimate']
                
                # If we found contact info, we can stop enriching
                if lead.owner_phone or lead.owner_email:
                    break
                    
            except Exception as e:
                print(f"     ⚠️ {source_name} enrichment failed: {str(e)}")
                continue
        
        return lead
    
    async def _enrich_from_property_records(self, lead: Lead) -> Dict[str, Any]:
        """Enrich from public property records (mock implementation)"""
        await asyncio.sleep(0.2)  # Simulate API call
        
        # Mock enrichment - 70% success rate
        if random.random() < 0.7:
            return {
                "owner_name": self._generate_owner_name(),
                "mailing_address": f"{lead.address}, {lead.city}, {lead.state} {lead.zip_code}",
                "equity_estimate": self._estimate_equity(lead.price)
            }
        
        return {}
    
    async def _enrich_from_skiptracing(self, lead: Lead) -> Dict[str, Any]:
        """Enrich from skiptracing services (mock implementation)"""
        await asyncio.sleep(0.3)  # Simulate API call
        
        # Mock enrichment - 60% success rate for phone
        enriched_data = {}
        
        if random.random() < 0.6:
            enriched_data["owner_phone"] = self._generate_phone_number()
        
        if random.random() < 0.4:
            enriched_data["owner_email"] = self._generate_email(lead.owner_name)
        
        return enriched_data
    
    async def _enrich_from_social_media(self, lead: Lead) -> Dict[str, Any]:
        """Enrich from social media profiles (mock implementation)"""
        await asyncio.sleep(0.15)  # Simulate API call
        
        # Mock enrichment - lower success rate but additional context
        if random.random() < 0.3:
            return {
                "owner_email": self._generate_email(lead.owner_name),
                "social_profile": "facebook_verified"
            }
        
        return {}
    
    async def _enrich_from_public_records(self, lead: Lead) -> Dict[str, Any]:
        """Enrich from additional public records (mock implementation)"""
        await asyncio.sleep(0.25)  # Simulate API call
        
        # Mock enrichment - 50% success rate
        if random.random() < 0.5:
            return {
                "owner_name": self._generate_owner_name(),
                "mailing_address": self._generate_mailing_address(lead)
            }
        
        return {}
    
    def _generate_owner_name(self) -> str:
        """Generate realistic owner name"""
        first_names = [
            "James", "Mary", "John", "Patricia", "Robert", "Jennifer", 
            "Michael", "Linda", "William", "Elizabeth", "David", "Barbara",
            "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah",
            "Christopher", "Karen", "Charles", "Nancy", "Daniel", "Lisa"
        ]
        
        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
            "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez",
            "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore",
            "Jackson", "Martin", "Lee", "Perez", "Thompson", "White"
        ]
        
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def _generate_phone_number(self) -> str:
        """Generate realistic phone number"""
        area_codes = ["602", "623", "480", "928", "520"]  # Arizona area codes
        return f"({random.choice(area_codes)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
    
    def _generate_email(self, owner_name: Optional[str]) -> str:
        """Generate realistic email address"""
        if owner_name:
            # Create email from name
            name_parts = owner_name.lower().split()
            if len(name_parts) >= 2:
                email_base = f"{name_parts[0]}.{name_parts[1]}"
            else:
                email_base = name_parts[0] if name_parts else "owner"
        else:
            email_base = "owner"
        
        # Add random numbers sometimes
        if random.random() < 0.3:
            email_base += str(random.randint(1, 99))
        
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com"]
        return f"{email_base}@{random.choice(domains)}"
    
    def _generate_mailing_address(self, lead: Lead) -> str:
        """Generate mailing address (often different from property address)"""
        if random.random() < 0.7:
            # Same as property address
            return f"{lead.address}, {lead.city}, {lead.state} {lead.zip_code}"
        else:
            # Different mailing address
            po_box = f"PO Box {random.randint(100, 9999)}"
            return f"{po_box}, {lead.city}, {lead.state} {lead.zip_code}"
    
    def _estimate_equity(self, current_price: Optional[float]) -> Optional[float]:
        """Estimate property equity based on price and market factors"""
        if not current_price:
            return None
        
        # Mock equity calculation
        # Assume 10-40% equity based on various factors
        equity_percentage = random.uniform(0.1, 0.4)
        return round(current_price * equity_percentage, 2)
