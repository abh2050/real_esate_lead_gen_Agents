"""
Scoring Agent - Scores and prioritizes leads using LLM-based analysis
"""

import asyncio
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from utils.models import AgentState, Lead
import os
import json

class ScoringAgent:
    """Agent responsible for scoring lead quality using LLM analysis"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.2,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Lead scoring prompt
        self.scoring_prompt = ChatPromptTemplate.from_template("""
You are a real estate lead scoring expert. Analyze the following property and owner information to determine lead quality.

Property Information:
- Address: {address}
- Price: ${price:,}
- Property Type: {property_type}
- Bedrooms: {bedrooms}
- Bathrooms: {bathrooms}
- Square Feet: {square_feet}
- Year Built: {year_built}
- Source: {source}

Owner Information:
- Owner Name: {owner_name}
- Phone Available: {has_phone}
- Email Available: {has_email}
- Mailing Address: {mailing_address}

Motivation Indicators:
{motivation_indicators}

Market Context:
- Days on Market: {days_on_market}
- Estimated Equity: ${equity_estimate}

Lead Type Target: {lead_type}

Please score this lead from 0-100 based on:

1. **Contact Availability (25 points)**: Phone/email accessibility
2. **Motivation Level (30 points)**: Signs of seller motivation
3. **Deal Potential (25 points)**: Price, equity, property condition indicators  
4. **Lead Type Match (20 points)**: How well this matches the target lead type

Return your analysis in this JSON format:
{{
    "overall_score": 85,
    "contact_score": 20,
    "motivation_score": 25,
    "deal_potential_score": 22,
    "lead_type_match_score": 18,
    "key_strengths": ["High equity", "Phone available", "Price reduction"],
    "key_concerns": ["Needs repairs", "Competitive market"],
    "recommended_approach": "Call owner directly about cash offer",
    "priority_level": "high"
}}

Be realistic and conservative in scoring. Only give high scores (80+) to truly exceptional leads.
""")
    
    async def process(self, state: AgentState) -> AgentState:
        """Score all enriched leads"""
        try:
            if not state.enriched_leads:
                raise ValueError("No enriched leads to score")
            
            print(f"📊 Scoring {len(state.enriched_leads)} enriched leads...")
            
            scored_leads = []
            
            # Score each lead
            for i, lead in enumerate(state.enriched_leads):
                print(f"   🎯 Scoring lead {i+1}/{len(state.enriched_leads)}: {lead.address}")
                
                try:
                    # Get LLM scoring
                    score_data = await self._score_lead(lead, state.search_criteria.lead_type)
                    
                    # Update lead with scoring data
                    lead.score = score_data.get("overall_score", 0)
                    
                    # Add scoring metadata
                    lead.metadata = {
                        "scoring": score_data,
                        "scored_at": str(asyncio.get_event_loop().time())
                    }
                    
                    scored_leads.append(lead)
                    
                except Exception as e:
                    print(f"     ⚠️ Scoring failed for {lead.address}: {str(e)}")
                    # Add lead with default score
                    lead.score = self._calculate_fallback_score(lead)
                    scored_leads.append(lead)
                
                # Small delay between API calls
                await asyncio.sleep(0.2)
            
            # Sort by score (highest first)
            scored_leads.sort(key=lambda x: x.score or 0, reverse=True)
            
            state.scored_leads = scored_leads
            state.current_step = "human_review"
            
            # Print scoring summary
            high_score_leads = [lead for lead in scored_leads if (lead.score or 0) >= 70]
            medium_score_leads = [lead for lead in scored_leads if 50 <= (lead.score or 0) < 70]
            
            print(f"✅ Scoring Complete:")
            print(f"   🟢 High Quality (70+): {len(high_score_leads)} leads")
            print(f"   🟡 Medium Quality (50-69): {len(medium_score_leads)} leads")
            print(f"   🔴 Lower Quality (<50): {len(scored_leads) - len(high_score_leads) - len(medium_score_leads)} leads")
            
            return state
            
        except Exception as e:
            error_msg = f"Scoring Agent error: {str(e)}"
            state.errors.append(error_msg)
            print(f"❌ {error_msg}")
            return state
    
    async def _score_lead(self, lead: Lead, lead_type: str) -> Dict[str, Any]:
        """Score a single lead using LLM analysis"""
        try:
            # Prepare the prompt data
            prompt_data = {
                "address": lead.address,
                "price": lead.price or 0,
                "property_type": lead.property_type,
                "bedrooms": lead.bedrooms or "Unknown",
                "bathrooms": lead.bathrooms or "Unknown", 
                "square_feet": lead.square_feet or "Unknown",
                "year_built": lead.year_built or "Unknown",
                "source": lead.source,
                "owner_name": lead.owner_name or "Unknown",
                "has_phone": "Yes" if lead.owner_phone else "No",
                "has_email": "Yes" if lead.owner_email else "No",
                "mailing_address": lead.mailing_address or "Same as property",
                "motivation_indicators": ", ".join(lead.motivation_indicators) if lead.motivation_indicators else "None identified",
                "days_on_market": getattr(lead, 'days_on_market', 'Unknown'),
                "equity_estimate": lead.equity_estimate or 0,
                "lead_type": lead_type
            }
            
            # Format the prompt
            formatted_prompt = self.scoring_prompt.format(**prompt_data)
            
            # Get LLM response
            response = await self.llm.ainvoke(formatted_prompt)
            
            # Parse JSON response
            try:
                score_data = json.loads(response.content)
                
                # Validate score data
                if not isinstance(score_data.get("overall_score"), (int, float)):
                    raise ValueError("Invalid overall_score in response")
                
                return score_data
                
            except json.JSONDecodeError:
                print(f"     ⚠️ Failed to parse LLM response as JSON, using fallback scoring")
                return self._extract_score_from_text(response.content, lead)
                
        except Exception as e:
            print(f"     ⚠️ LLM scoring failed: {str(e)}")
            raise
    
    def _extract_score_from_text(self, response_text: str, lead: Lead) -> Dict[str, Any]:
        """Extract score from non-JSON LLM response"""
        # Try to find a score in the text
        import re
        
        score_match = re.search(r'(?:score|rating).*?(\d+)', response_text.lower())
        if score_match:
            overall_score = int(score_match.group(1))
        else:
            overall_score = self._calculate_fallback_score(lead)
        
        return {
            "overall_score": overall_score,
            "contact_score": 15 if lead.owner_phone or lead.owner_email else 5,
            "motivation_score": len(lead.motivation_indicators) * 5,
            "deal_potential_score": 15,
            "lead_type_match_score": 15,
            "key_strengths": ["Contact available"] if lead.owner_phone or lead.owner_email else [],
            "key_concerns": [],
            "recommended_approach": "Standard follow-up",
            "priority_level": "medium" if overall_score >= 50 else "low"
        }
    
    def _calculate_fallback_score(self, lead: Lead) -> float:
        """Calculate a basic score when LLM scoring fails"""
        score = 0
        
        # Contact information (30 points)
        if lead.owner_phone:
            score += 20
        if lead.owner_email:
            score += 10
        
        # Motivation indicators (30 points)
        high_value_indicators = [
            "motivated_seller", "price_reduction", "estate_sale",
            "financial_distress", "quick_sale_needed", "high_equity"
        ]
        
        for indicator in lead.motivation_indicators:
            if indicator in high_value_indicators:
                score += 8
            else:
                score += 3
        
        # Property completeness (20 points)
        if lead.price:
            score += 5
        if lead.bedrooms:
            score += 3
        if lead.bathrooms:
            score += 3
        if lead.square_feet:
            score += 5
        if lead.year_built:
            score += 4
        
        # Source quality (20 points)
        source_scores = {
            "mls": 20,
            "fsbo": 15,
            "zillow": 12,
            "realtor": 10
        }
        score += source_scores.get(lead.source, 5)
        
        return min(score, 100)  # Cap at 100
