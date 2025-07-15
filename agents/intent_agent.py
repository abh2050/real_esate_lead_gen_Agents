"""
Intent Agent - Understands user requirements and converts to structured search criteria
"""

import re
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from utils.models import SearchCriteria, AgentState
import os

class IntentAgent:
    """Agent responsible for understanding user intent and extracting search criteria"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.output_parser = PydanticOutputParser(pydantic_object=SearchCriteria)
        
        # Intent analysis prompt
        self.prompt = ChatPromptTemplate.from_template("""
You are a real estate lead generation specialist. Analyze the user query and extract structured search criteria.

Key indicators to look for:
- Location: city, state, ZIP codes, neighborhoods
- Property types: single-family, duplex, triplex, apartment, commercial
- Price ranges: under $X, between $X-$Y, over $X  
- Lead type: buyer leads, seller leads, investor opportunities
- Motivation signals: distressed, foreclosure, divorce, estate sale, vacant, high equity

User Query: {user_query}

{format_instructions}

Extract the following information:
1. Primary location(s) to search
2. Property types of interest
3. Price range (if mentioned)
4. Whether they want buyer, seller, or investor leads
5. Any specific motivation signals mentioned

Be specific and detailed. If information is unclear, make reasonable assumptions based on real estate context.
""")
        
    async def process(self, state: AgentState) -> AgentState:
        """Process user query and extract search criteria"""
        try:
            # Format the prompt
            formatted_prompt = self.prompt.format(
                user_query=state.user_query,
                format_instructions=self.output_parser.get_format_instructions()
            )
            
            # Get LLM response
            response = await self.llm.ainvoke(formatted_prompt)
            
            # Parse the response
            search_criteria = self.output_parser.parse(response.content)
            
            # Update state
            state.search_criteria = search_criteria
            state.current_step = "search"
            
            # Add some metadata
            state.metadata["intent_analysis"] = {
                "original_query": state.user_query,
                "extracted_location": search_criteria.location,
                "lead_type": search_criteria.lead_type,
                "property_types": search_criteria.property_types
            }
            
            print(f"🎯 Intent Analysis Complete:")
            print(f"   📍 Location: {search_criteria.location}")
            print(f"   🏠 Property Types: {', '.join(search_criteria.property_types)}")
            print(f"   💰 Price Range: ${search_criteria.price_min or 'No min'} - ${search_criteria.price_max or 'No max'}")
            print(f"   🎯 Lead Type: {search_criteria.lead_type}")
            
            return state
            
        except Exception as e:
            error_msg = f"Intent Agent error: {str(e)}"
            state.errors.append(error_msg)
            print(f"❌ {error_msg}")
            return state
    
    def _extract_price_range(self, query: str) -> tuple[float, float]:
        """Extract price range from natural language"""
        price_patterns = [
            r'under\s+\$?([\d,]+)',
            r'below\s+\$?([\d,]+)',
            r'over\s+\$?([\d,]+)',
            r'above\s+\$?([\d,]+)',
            r'\$?([\d,]+)\s*-\s*\$?([\d,]+)',
            r'between\s+\$?([\d,]+)\s+and\s+\$?([\d,]+)',
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, query.lower())
            if match:
                if 'under' in pattern or 'below' in pattern:
                    return None, float(match.group(1).replace(',', ''))
                elif 'over' in pattern or 'above' in pattern:
                    return float(match.group(1).replace(',', '')), None
                else:
                    # Range pattern
                    return (
                        float(match.group(1).replace(',', '')),
                        float(match.group(2).replace(',', ''))
                    )
        
        return None, None
    
    def _extract_locations(self, query: str) -> list[str]:
        """Extract location mentions from query"""
        # Common location patterns
        location_patterns = [
            r'in\s+([A-Za-z\s]+,\s*[A-Z]{2})',  # City, ST
            r'([A-Za-z\s]+,\s*[A-Z]{2})',        # City, ST
            r'(\d{5})',                          # ZIP code
        ]
        
        locations = []
        for pattern in location_patterns:
            matches = re.findall(pattern, query)
            locations.extend(matches)
        
        return locations
