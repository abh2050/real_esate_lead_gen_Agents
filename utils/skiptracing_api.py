"""
Skiptracing API Integration Utilities
Mock implementation for demonstration - replace with actual skiptracing services
"""

import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
import random
import json

class SkiptracingAPI:
    """Skiptracing service integration for finding property owner contact information"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.services = {
            "truepeoplesearch": self._search_truepeoplesearch,
            "spokeo": self._search_spokeo,
            "whitepages": self._search_whitepages,
            "beenverified": self._search_beenverified
        }
    
    async def find_owner_contact(self, 
                                address: str,
                                city: str,
                                state: str,
                                zip_code: str,
                                owner_name: Optional[str] = None) -> Dict[str, Any]:
        """Find property owner contact information"""
        
        contact_info = {
            "address": f"{address}, {city}, {state} {zip_code}",
            "owner_name": owner_name,
            "phones": [],
            "emails": [],
            "relatives": [],
            "previous_addresses": [],
            "confidence_score": 0
        }
        
        # Try each skiptracing service
        for service_name, search_func in self.services.items():
            try:
                result = await search_func(address, city, state, zip_code, owner_name)
                
                # Merge results
                if result.get("phones"):
                    contact_info["phones"].extend(result["phones"])
                if result.get("emails"):
                    contact_info["emails"].extend(result["emails"])
                if result.get("relatives"):
                    contact_info["relatives"].extend(result["relatives"])
                if result.get("previous_addresses"):
                    contact_info["previous_addresses"].extend(result["previous_addresses"])
                
                # Update confidence score
                contact_info["confidence_score"] = max(
                    contact_info["confidence_score"],
                    result.get("confidence_score", 0)
                )
                
                # If we found good contact info, we might not need to check other services
                if result.get("confidence_score", 0) > 80:
                    break
                    
            except Exception as e:
                print(f"Skiptracing service {service_name} failed: {str(e)}")
                continue
        
        # Deduplicate results
        contact_info["phones"] = list(set(contact_info["phones"]))
        contact_info["emails"] = list(set(contact_info["emails"]))
        contact_info["relatives"] = list(set(contact_info["relatives"]))
        
        return contact_info
    
    async def _search_truepeoplesearch(self, address: str, city: str, state: str, zip_code: str, owner_name: Optional[str]) -> Dict[str, Any]:
        """Search TruePeopleSearch (mock implementation)"""
        await asyncio.sleep(0.3)  # Simulate API delay
        
        # Mock successful search (70% success rate)
        if random.random() < 0.7:
            return {
                "phones": [self._generate_phone_number()],
                "emails": [self._generate_email(owner_name)] if owner_name else [],
                "relatives": [f"Relative {i}" for i in range(random.randint(0, 3))],
                "confidence_score": random.randint(60, 95)
            }
        
        return {"confidence_score": 0}
    
    async def _search_spokeo(self, address: str, city: str, state: str, zip_code: str, owner_name: Optional[str]) -> Dict[str, Any]:
        """Search Spokeo (mock implementation)"""
        await asyncio.sleep(0.4)  # Simulate API delay
        
        # Mock successful search (60% success rate)
        if random.random() < 0.6:
            return {
                "phones": [self._generate_phone_number() for _ in range(random.randint(1, 2))],
                "emails": [self._generate_email(owner_name)] if owner_name and random.random() < 0.5 else [],
                "previous_addresses": [self._generate_previous_address(city, state)],
                "confidence_score": random.randint(70, 90)
            }
        
        return {"confidence_score": 0}
    
    async def _search_whitepages(self, address: str, city: str, state: str, zip_code: str, owner_name: Optional[str]) -> Dict[str, Any]:
        """Search Whitepages (mock implementation)"""
        await asyncio.sleep(0.2)  # Simulate API delay
        
        # Mock successful search (80% success rate for phones, lower for emails)
        if random.random() < 0.8:
            return {
                "phones": [self._generate_phone_number()],
                "emails": [self._generate_email(owner_name)] if owner_name and random.random() < 0.3 else [],
                "confidence_score": random.randint(75, 95)
            }
        
        return {"confidence_score": 0}
    
    async def _search_beenverified(self, address: str, city: str, state: str, zip_code: str, owner_name: Optional[str]) -> Dict[str, Any]:
        """Search BeenVerified (mock implementation)"""
        await asyncio.sleep(0.5)  # Simulate API delay
        
        # Mock successful search (50% success rate)
        if random.random() < 0.5:
            return {
                "phones": [self._generate_phone_number()],
                "emails": [self._generate_email(owner_name)] if owner_name else [],
                "relatives": [f"{random.choice(['John', 'Jane', 'Bob', 'Alice'])} {random.choice(['Smith', 'Johnson', 'Williams'])}" for _ in range(random.randint(1, 2))],
                "previous_addresses": [self._generate_previous_address(city, state) for _ in range(random.randint(0, 2))],
                "confidence_score": random.randint(65, 85)
            }
        
        return {"confidence_score": 0}
    
    def _generate_phone_number(self) -> str:
        """Generate realistic phone number"""
        area_codes = ["602", "623", "480", "928", "520", "480", "602"]  # Arizona area codes + some repeats
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
        
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com"]
        return f"{email_base}@{random.choice(domains)}"
    
    def _generate_previous_address(self, current_city: str, current_state: str) -> str:
        """Generate previous address"""
        if random.random() < 0.7:
            # Same city, different address
            return f"{random.randint(100, 9999)} {random.choice(['Old', 'Former', 'Previous'])} {random.choice(['St', 'Ave', 'Dr'])}, {current_city}, {current_state}"
        else:
            # Different city
            cities = ["Phoenix", "Tucson", "Mesa", "Chandler", "Glendale", "Scottsdale"]
            other_city = random.choice([c for c in cities if c != current_city])
            return f"{random.randint(100, 9999)} {random.choice(['Main', 'First', 'Second'])} {random.choice(['St', 'Ave', 'Dr'])}, {other_city}, {current_state}"

class PropertyRecordsAPI:
    """Property records API for getting owner information from public records"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    async def get_property_owner(self, address: str, city: str, state: str, zip_code: str) -> Dict[str, Any]:
        """Get property owner information from public records"""
        
        await asyncio.sleep(0.3)  # Simulate API delay
        
        # Mock property records lookup (90% success rate)
        if random.random() < 0.9:
            owner_names = [
                "John Smith", "Mary Johnson", "Robert Williams", "Jennifer Brown",
                "Michael Jones", "Linda Garcia", "William Miller", "Elizabeth Davis",
                "David Rodriguez", "Barbara Martinez", "Richard Hernandez", "Susan Lopez"
            ]
            
            return {
                "owner_name": random.choice(owner_names),
                "mailing_address": self._generate_mailing_address(address, city, state, zip_code),
                "property_value": random.randint(200000, 800000),
                "property_tax": random.randint(2000, 12000),
                "ownership_type": random.choice(["Individual", "Trust", "LLC", "Corporation"]),
                "deed_date": f"2{random.randint(0, 2)}{random.randint(10, 23)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "parcel_number": f"APN{random.randint(100000, 999999)}",
                "confidence_score": random.randint(85, 98)
            }
        
        return {"confidence_score": 0}
    
    def _generate_mailing_address(self, property_address: str, city: str, state: str, zip_code: str) -> str:
        """Generate mailing address (often same as property, sometimes different)"""
        if random.random() < 0.8:
            # Same as property address
            return f"{property_address}, {city}, {state} {zip_code}"
        else:
            # Different mailing address (PO Box or different address)
            if random.random() < 0.5:
                return f"PO Box {random.randint(100, 9999)}, {city}, {state} {zip_code}"
            else:
                return f"{random.randint(100, 9999)} {random.choice(['Mailing', 'Billing', 'Contact'])} {random.choice(['St', 'Ave', 'Dr'])}, {city}, {state} {zip_code}"

class EnrichmentService:
    """Comprehensive enrichment service combining multiple data sources"""
    
    def __init__(self):
        self.skiptracing = SkiptracingAPI()
        self.property_records = PropertyRecordsAPI()
    
    async def enrich_property_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich a property lead with all available contact information"""
        
        address = lead_data.get("address", "")
        city = lead_data.get("city", "")
        state = lead_data.get("state", "")
        zip_code = lead_data.get("zip_code", "")
        
        enriched_data = lead_data.copy()
        
        try:
            # Get property owner from public records
            print(f"   🔍 Searching property records for {address}")
            property_info = await self.property_records.get_property_owner(address, city, state, zip_code)
            
            if property_info.get("owner_name"):
                enriched_data["owner_name"] = property_info["owner_name"]
                enriched_data["mailing_address"] = property_info.get("mailing_address")
                enriched_data["property_value_estimate"] = property_info.get("property_value")
                
                # Now search for contact info using the owner name
                print(f"   📞 Skiptracing contact info for {property_info['owner_name']}")
                contact_info = await self.skiptracing.find_owner_contact(
                    address, city, state, zip_code, property_info["owner_name"]
                )
                
                # Add contact information
                if contact_info.get("phones"):
                    enriched_data["owner_phone"] = contact_info["phones"][0]  # Use first phone
                    enriched_data["all_phones"] = contact_info["phones"]
                
                if contact_info.get("emails"):
                    enriched_data["owner_email"] = contact_info["emails"][0]  # Use first email
                    enriched_data["all_emails"] = contact_info["emails"]
                
                if contact_info.get("relatives"):
                    enriched_data["relatives"] = contact_info["relatives"]
                
                if contact_info.get("previous_addresses"):
                    enriched_data["previous_addresses"] = contact_info["previous_addresses"]
                
                # Calculate enrichment confidence
                enrichment_score = (
                    property_info.get("confidence_score", 0) * 0.6 +
                    contact_info.get("confidence_score", 0) * 0.4
                )
                enriched_data["enrichment_confidence"] = enrichment_score
                
                print(f"   ✅ Enrichment complete (confidence: {enrichment_score:.1f}%)")
            else:
                print(f"   ⚠️ No owner information found in property records")
                enriched_data["enrichment_confidence"] = 0
        
        except Exception as e:
            print(f"   ❌ Enrichment failed: {str(e)}")
            enriched_data["enrichment_error"] = str(e)
            enriched_data["enrichment_confidence"] = 0
        
        return enriched_data

# Batch enrichment utility
async def batch_enrich_leads(leads: List[Dict[str, Any]], max_concurrent: int = 5) -> List[Dict[str, Any]]:
    """Enrich multiple leads concurrently with rate limiting"""
    
    enrichment_service = EnrichmentService()
    enriched_leads = []
    
    # Process in batches to avoid rate limiting
    for i in range(0, len(leads), max_concurrent):
        batch = leads[i:i + max_concurrent]
        
        # Process batch concurrently
        tasks = [enrichment_service.enrich_property_lead(lead) for lead in batch]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle results and exceptions
        for j, result in enumerate(batch_results):
            if isinstance(result, Exception):
                print(f"Lead {i+j+1} enrichment failed: {str(result)}")
                # Add original lead with error marker
                error_lead = batch[j].copy()
                error_lead["enrichment_error"] = str(result)
                enriched_leads.append(error_lead)
            else:
                enriched_leads.append(result)
        
        # Small delay between batches
        if i + max_concurrent < len(leads):
            await asyncio.sleep(1)
    
    return enriched_leads
