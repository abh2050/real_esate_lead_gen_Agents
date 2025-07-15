"""
Filter Agent - Filters and refines property listings based on criteria
"""

from typing import Dict, List, Any
from utils.models import AgentState, SearchCriteria
from datetime import datetime, timedelta

class FilterAgent:
    """Agent responsible for filtering raw listings based on detailed criteria"""
    
    def __init__(self):
        self.filters = {
            "location": self._filter_by_location,
            "price": self._filter_by_price,
            "property_type": self._filter_by_property_type,
            "size": self._filter_by_size,
            "age": self._filter_by_age,
            "motivation": self._filter_by_motivation,
            "quality": self._filter_by_quality
        }
    
    async def process(self, state: AgentState) -> AgentState:
        """Filter raw listings based on search criteria"""
        try:
            if not state.raw_listings:
                raise ValueError("No raw listings to filter")
            
            print(f"🔍 Filtering {len(state.raw_listings)} raw listings...")
            
            filtered_listings = state.raw_listings.copy()
            
            # Apply each filter
            for filter_name, filter_func in self.filters.items():
                initial_count = len(filtered_listings)
                
                # Skip motivation filter if no specific motivation signals are requested
                if filter_name == "motivation" and not state.search_criteria.motivation_signals:
                    print(f"   🎯 {filter_name} filter: skipped (no specific signals requested)")
                    continue
                    
                filtered_listings = filter_func(filtered_listings, state.search_criteria)
                removed = initial_count - len(filtered_listings)
                if removed > 0:
                    print(f"   🎯 {filter_name} filter: removed {removed} listings")
                else:
                    print(f"   ✅ {filter_name} filter: all listings passed")
            
            # Add quality scores
            filtered_listings = self._add_quality_scores(filtered_listings)
            
            # Sort by quality score
            filtered_listings.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
            
            state.filtered_listings = filtered_listings
            state.current_step = "enrichment"
            
            print(f"✅ Filtering Complete: {len(filtered_listings)} listings remain")
            
            return state
            
        except Exception as e:
            error_msg = f"Filter Agent error: {str(e)}"
            state.errors.append(error_msg)
            print(f"❌ {error_msg}")
            return state
    
    def _filter_by_location(self, listings: List[Dict[str, Any]], criteria: SearchCriteria) -> List[Dict[str, Any]]:
        """Filter by location criteria"""
        if not criteria.location:
            return listings
        
        # Extract target city and state
        location_parts = [part.strip().lower() for part in criteria.location.split(',')]
        target_city = location_parts[0] if location_parts else ""
        target_state = location_parts[1] if len(location_parts) > 1 else ""
        
        filtered = []
        for listing in listings:
            listing_city = listing.get('city', '').lower()
            listing_state = listing.get('state', '').lower()
            
            # Match city
            city_match = target_city in listing_city or listing_city in target_city
            
            # Match state if provided
            state_match = True
            if target_state:
                state_match = target_state in listing_state or listing_state in target_state
            
            if city_match and state_match:
                filtered.append(listing)
        
        return filtered
    
    def _filter_by_price(self, listings: List[Dict[str, Any]], criteria: SearchCriteria) -> List[Dict[str, Any]]:
        """Filter by price range"""
        filtered = []
        
        for listing in listings:
            price = listing.get('price', 0)
            
            # Check minimum price
            if criteria.price_min and price < criteria.price_min:
                continue
            
            # Check maximum price
            if criteria.price_max and price > criteria.price_max:
                continue
            
            filtered.append(listing)
        
        return filtered
    
    def _filter_by_property_type(self, listings: List[Dict[str, Any]], criteria: SearchCriteria) -> List[Dict[str, Any]]:
        """Filter by property type"""
        if not criteria.property_types:
            return listings
        
        filtered = []
        for listing in listings:
            listing_type = listing.get('property_type', '').lower()
            
            # Check if listing type matches any of the desired types
            for desired_type in criteria.property_types:
                if desired_type.lower() in listing_type or listing_type in desired_type.lower():
                    filtered.append(listing)
                    break
        
        return filtered
    
    def _filter_by_size(self, listings: List[Dict[str, Any]], criteria: SearchCriteria) -> List[Dict[str, Any]]:
        """Filter by property size (bedrooms, bathrooms, square feet)"""
        filtered = []
        
        for listing in listings:
            # Basic size filters - can be expanded based on criteria
            bedrooms = listing.get('bedrooms', 0)
            square_feet = listing.get('square_feet', 0)
            
            # Filter out very small properties for investors
            if criteria.lead_type == "investor":
                if bedrooms < 2 or square_feet < 800:
                    continue
            
            # Filter out very large properties for first-time buyers
            if criteria.lead_type == "buyer":
                if bedrooms > 5 or square_feet > 4000:
                    continue
            
            filtered.append(listing)
        
        return filtered
    
    def _filter_by_age(self, listings: List[Dict[str, Any]], criteria: SearchCriteria) -> List[Dict[str, Any]]:
        """Filter by property age"""
        filtered = []
        current_year = datetime.now().year
        
        for listing in listings:
            year_built = listing.get('year_built', current_year)
            property_age = current_year - year_built
            
            # Skip properties with missing or unrealistic year built
            if year_built < 1900 or year_built > current_year:
                continue
            
            # Age-based filtering based on lead type
            if criteria.lead_type == "investor":
                # Investors might prefer older properties with potential
                if property_age > 50:  # Built before 1974
                    listing['age_category'] = 'vintage'
                elif property_age > 20:  # Built before 2004
                    listing['age_category'] = 'mature'
                else:
                    listing['age_category'] = 'modern'
            
            filtered.append(listing)
        
        return filtered
    
    def _filter_by_motivation(self, listings: List[Dict[str, Any]], criteria: SearchCriteria) -> List[Dict[str, Any]]:
        """Filter by motivation signals"""
        # If no specific motivation signals are requested, return all listings
        if not criteria.motivation_signals:
            return listings
        
        filtered = []
        
        for listing in listings:
            listing_signals = listing.get('motivation_signals', [])
            
            # Check if any desired motivation signals are present
            has_desired_signal = any(
                desired_signal.lower() in [signal.lower() for signal in listing_signals]
                for desired_signal in criteria.motivation_signals
            )
            
            # If we have specific motivation criteria, use them
            # But be more lenient - if a listing has ANY motivation signals, include it
            if has_desired_signal:
                filtered.append(listing)
            elif listing_signals:  # Has some motivation signals, even if not exactly what we want
                filtered.append(listing)
        
        # If no listings match the strict criteria, return some with any motivation signals
        if not filtered:
            print(f"   ℹ️  No listings match specific motivation criteria, including any with motivation signals")
            for listing in listings:
                if listing.get('motivation_signals'):
                    filtered.append(listing)
        
        return filtered
    
    def _filter_by_quality(self, listings: List[Dict[str, Any]], criteria: SearchCriteria) -> List[Dict[str, Any]]:
        """Filter out low-quality listings"""
        filtered = []
        
        for listing in listings:
            # Quality indicators
            has_price = listing.get('price', 0) > 0
            has_address = bool(listing.get('address', '').strip())
            has_property_type = bool(listing.get('property_type', '').strip())
            
            # Require basic information
            if has_price and has_address and has_property_type:
                filtered.append(listing)
        
        return filtered
    
    def _add_quality_scores(self, listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add quality scores to listings"""
        for listing in listings:
            score = 0
            
            # Basic information completeness (30 points)
            if listing.get('price'): score += 10
            if listing.get('bedrooms'): score += 5
            if listing.get('bathrooms'): score += 5
            if listing.get('square_feet'): score += 10
            
            # Motivation signals (40 points)
            motivation_signals = listing.get('motivation_signals', [])
            high_value_signals = [
                'motivated_seller', 'price_reduction', 'estate_sale',
                'financial_distress', 'quick_sale_needed', 'high_equity'
            ]
            
            for signal in motivation_signals:
                if signal in high_value_signals:
                    score += 10
                else:
                    score += 5
            
            # Source quality (20 points)
            source = listing.get('source', '')
            if source == 'mls':
                score += 20
            elif source == 'fsbo':
                score += 15
            elif source == 'zillow':
                score += 10
            else:
                score += 5
            
            # Days on market (10 points - inverse scoring)
            days_on_market = listing.get('days_on_market', 0)
            if days_on_market > 90:
                score += 10  # Long time = more motivated
            elif days_on_market > 30:
                score += 7
            elif days_on_market > 7:
                score += 4
            else:
                score += 1
            
            listing['quality_score'] = min(score, 100)  # Cap at 100
        
        return listings
