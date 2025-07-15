"""
Search Agent - Queries various real estate data sources for property listings
"""

import asyncio
import aiohttp
from typing import Dict, List, Any
from utils.models import AgentState, SearchCriteria
import json
import random
from datetime import datetime, timedelta

class SearchAgent:
    """Agent responsible for searching property listings from various sources"""
    
    def __init__(self):
        self.sources = {
            "zillow": self._search_zillow,
            "realtor": self._search_realtor,
            "mls": self._search_mls,
            "fsbo": self._search_fsbo
        }
    
    async def process(self, state: AgentState) -> AgentState:
        """Search for properties based on criteria"""
        try:
            if not state.search_criteria:
                raise ValueError("No search criteria provided")
            
            print(f"🔍 Starting property search for: {state.search_criteria.location}")
            
            # Search all available sources
            all_listings = []
            
            for source_name, search_func in self.sources.items():
                try:
                    print(f"   📡 Searching {source_name}...")
                    listings = await search_func(state.search_criteria)
                    all_listings.extend(listings)
                    print(f"   ✅ Found {len(listings)} listings from {source_name}")
                except Exception as e:
                    print(f"   ⚠️  {source_name} search failed: {str(e)}")
                    continue
            
            # Remove duplicates based on address
            unique_listings = self._deduplicate_listings(all_listings)
            
            state.raw_listings = unique_listings
            state.current_step = "filter"
            
            print(f"🎯 Search Complete: {len(unique_listings)} unique listings found")
            
            return state
            
        except Exception as e:
            error_msg = f"Search Agent error: {str(e)}"
            state.errors.append(error_msg)
            print(f"❌ {error_msg}")
            return state
    
    async def _search_zillow(self, criteria: SearchCriteria) -> List[Dict[str, Any]]:
        """Search Zillow (mock implementation - replace with real API)"""
        # Mock data for demonstration
        await asyncio.sleep(1)  # Simulate API call
        
        mock_listings = []
        for i in range(random.randint(10, 25)):
            listing = {
                "source": "zillow",
                "address": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm', 'Cedar'])} {random.choice(['St', 'Ave', 'Dr', 'Ln'])}",
                "city": criteria.location.split(',')[0].strip() if ',' in criteria.location else criteria.location,
                "state": criteria.location.split(',')[1].strip() if ',' in criteria.location else "AZ",
                "zip_code": f"{random.randint(10000, 99999)}",
                "property_type": random.choice(criteria.property_types),
                "price": random.randint(200000, 800000),
                "bedrooms": random.randint(2, 5),
                "bathrooms": random.choice([1.0, 1.5, 2.0, 2.5, 3.0]),
                "square_feet": random.randint(1200, 3500),
                "year_built": random.randint(1980, 2020),
                "days_on_market": random.randint(1, 200),
                "listing_type": random.choice(["for_sale", "pending", "recently_sold"]),
                "mls_number": f"MLS{random.randint(100000, 999999)}",
                "listing_agent": f"Agent {random.randint(1, 100)}",
                "motivation_signals": self._generate_motivation_signals()
            }
            
            # Apply price filters
            if criteria.price_min and listing["price"] < criteria.price_min:
                continue
            if criteria.price_max and listing["price"] > criteria.price_max:
                continue
                
            mock_listings.append(listing)
        
        return mock_listings
    
    async def _search_realtor(self, criteria: SearchCriteria) -> List[Dict[str, Any]]:
        """Search Realtor.com (mock implementation)"""
        await asyncio.sleep(0.8)
        
        mock_listings = []
        for i in range(random.randint(5, 15)):
            listing = {
                "source": "realtor",
                "address": f"{random.randint(100, 9999)} {random.choice(['Broadway', 'First', 'Second', 'Third', 'Fourth'])} {random.choice(['St', 'Ave', 'Blvd'])}",
                "city": criteria.location.split(',')[0].strip() if ',' in criteria.location else criteria.location,
                "state": criteria.location.split(',')[1].strip() if ',' in criteria.location else "AZ",
                "zip_code": f"{random.randint(10000, 99999)}",
                "property_type": random.choice(criteria.property_types),
                "price": random.randint(150000, 700000),
                "bedrooms": random.randint(1, 4),
                "bathrooms": random.choice([1.0, 1.5, 2.0, 2.5, 3.0]),
                "square_feet": random.randint(800, 2800),
                "year_built": random.randint(1970, 2019),
                "days_on_market": random.randint(1, 150),
                "listing_type": "for_sale",
                "description": "Beautiful property with great potential",
                "motivation_signals": self._generate_motivation_signals()
            }
            
            # Apply price filters
            if criteria.price_min and listing["price"] < criteria.price_min:
                continue
            if criteria.price_max and listing["price"] > criteria.price_max:
                continue
                
            mock_listings.append(listing)
        
        return mock_listings
    
    async def _search_mls(self, criteria: SearchCriteria) -> List[Dict[str, Any]]:
        """Search MLS data (mock implementation)"""
        await asyncio.sleep(1.2)
        
        # Simulate fewer but higher quality MLS listings
        mock_listings = []
        for i in range(random.randint(3, 8)):
            listing = {
                "source": "mls",
                "address": f"{random.randint(1000, 9999)} {random.choice(['Professional', 'Executive', 'Corporate', 'Business'])} {random.choice(['Way', 'Circle', 'Court'])}",
                "city": criteria.location.split(',')[0].strip() if ',' in criteria.location else criteria.location,
                "state": criteria.location.split(',')[1].strip() if ',' in criteria.location else "AZ",
                "zip_code": f"{random.randint(10000, 99999)}",
                "property_type": random.choice(criteria.property_types),
                "price": random.randint(300000, 1200000),
                "bedrooms": random.randint(3, 6),
                "bathrooms": random.choice([2.0, 2.5, 3.0, 3.5, 4.0]),
                "square_feet": random.randint(2000, 5000),
                "year_built": random.randint(1990, 2023),
                "days_on_market": random.randint(1, 90),
                "listing_type": "active",
                "mls_exclusive": True,
                "motivation_signals": self._generate_motivation_signals(high_quality=True)
            }
            
            # Apply price filters
            if criteria.price_min and listing["price"] < criteria.price_min:
                continue
            if criteria.price_max and listing["price"] > criteria.price_max:
                continue
                
            mock_listings.append(listing)
        
        return mock_listings
    
    async def _search_fsbo(self, criteria: SearchCriteria) -> List[Dict[str, Any]]:
        """Search For Sale By Owner listings (mock implementation)"""
        await asyncio.sleep(0.6)
        
        mock_listings = []
        for i in range(random.randint(2, 6)):
            listing = {
                "source": "fsbo",
                "address": f"{random.randint(100, 9999)} {random.choice(['Residential', 'Homeowner', 'Private', 'Owner'])} {random.choice(['Dr', 'Ln', 'Ct'])}",
                "city": criteria.location.split(',')[0].strip() if ',' in criteria.location else criteria.location,
                "state": criteria.location.split(',')[1].strip() if ',' in criteria.location else "AZ",
                "zip_code": f"{random.randint(10000, 99999)}",
                "property_type": random.choice(criteria.property_types),
                "price": random.randint(180000, 600000),
                "bedrooms": random.randint(2, 4),
                "bathrooms": random.choice([1.0, 1.5, 2.0, 2.5]),
                "square_feet": random.randint(1000, 2500),
                "year_built": random.randint(1975, 2015),
                "days_on_market": random.randint(5, 300),
                "listing_type": "fsbo",
                "owner_contact": f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
                "motivation_signals": self._generate_motivation_signals(fsbo=True)
            }
            
            # Apply price filters
            if criteria.price_min and listing["price"] < criteria.price_min:
                continue
            if criteria.price_max and listing["price"] > criteria.price_max:
                continue
                
            mock_listings.append(listing)
        
        return mock_listings
    
    def _generate_motivation_signals(self, high_quality: bool = False, fsbo: bool = False) -> List[str]:
        """Generate realistic motivation signals"""
        all_signals = [
            "long_time_on_market",
            "price_reduction",
            "motivated_seller",
            "estate_sale",
            "divorce_sale",
            "job_relocation",
            "financial_distress",
            "vacant_property",
            "needs_repairs",
            "investor_owned",
            "high_equity",
            "below_market_value",
            "quick_sale_needed"
        ]
        
        # Higher quality signals for MLS
        if high_quality:
            quality_signals = [
                "price_reduction",
                "motivated_seller", 
                "job_relocation",
                "high_equity",
                "quick_sale_needed"
            ]
            return random.sample(quality_signals, k=random.randint(1, 2))
        
        # FSBO specific signals
        if fsbo:
            fsbo_signals = [
                "owner_motivated",
                "avoid_agent_fees",
                "quick_sale_needed",
                "financial_distress",
                "vacant_property"
            ]
            return random.sample(fsbo_signals, k=random.randint(1, 3))
        
        # General signals
        return random.sample(all_signals, k=random.randint(0, 2))
    
    def _deduplicate_listings(self, listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate listings based on address"""
        seen_addresses = set()
        unique_listings = []
        
        for listing in listings:
            address_key = f"{listing['address']}, {listing['city']}, {listing['state']}"
            if address_key not in seen_addresses:
                seen_addresses.add(address_key)
                unique_listings.append(listing)
        
        return unique_listings
