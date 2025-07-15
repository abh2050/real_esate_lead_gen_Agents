"""
Formatter Agent - Exports leads to various formats (CSV, Google Sheets, CRM)
"""

import asyncio
import csv
import json
import os
from datetime import datetime
from typing import Dict, List, Any
from utils.models import AgentState, Lead
import pandas as pd

class FormatterAgent:
    """Agent responsible for formatting and exporting final leads"""
    
    def __init__(self):
        self.output_formats = {
            "csv": self._export_to_csv,
            "json": self._export_to_json,
            "excel": self._export_to_excel,
            "google_sheets": self._export_to_google_sheets,
            "airtable": self._export_to_airtable
        }
        
        # Ensure output directory exists
        self.output_dir = "outputs"
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def process(self, state: AgentState) -> AgentState:
        """Format and export human-approved leads"""
        try:
            # Handle both AgentState and dict-like states from LangGraph
            if hasattr(state, 'human_reviewed_leads'):
                leads_to_export = state.human_reviewed_leads or state.scored_leads
            else:
                # Handle dict-like state from LangGraph
                leads_to_export = state.get('human_reviewed_leads', state.get('scored_leads', []))
            
            if not leads_to_export:
                raise ValueError("No leads to export")
            
            print(f"📁 Exporting {len(leads_to_export)} leads...")
            
            # Generate timestamp for file naming
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export to multiple formats
            output_files = []
            
            # Always export to CSV
            csv_file = await self._export_to_csv(leads_to_export, timestamp)
            output_files.append(csv_file)
            
            # Export to additional formats based on configuration
            json_file = await self._export_to_json(leads_to_export, timestamp)
            output_files.append(json_file)
            
            excel_file = await self._export_to_excel(leads_to_export, timestamp)
            output_files.append(excel_file)
            
            # Create summary report
            summary_file = await self._create_summary_report(state, leads_to_export, timestamp)
            output_files.append(summary_file)
            
            # Update state - handle both AgentState and dict-like states
            if hasattr(state, 'output_file'):
                state.output_file = csv_file  # Primary output file
                state.final_leads = leads_to_export
                state.current_step = "complete"
            else:
                # Handle dict-like state from LangGraph
                state['output_file'] = csv_file
                state['final_leads'] = leads_to_export
                state['current_step'] = "complete"
            
            print(f"✅ Export Complete:")
            for file_path in output_files:
                print(f"   📄 {file_path}")
            
            return state
            
        except Exception as e:
            error_msg = f"Formatter Agent error: {str(e)}"
            state.errors.append(error_msg)
            print(f"❌ {error_msg}")
            return state
    
    async def _export_to_csv(self, leads: List[Lead], timestamp: str) -> str:
        """Export leads to CSV format"""
        filename = f"{self.output_dir}/real_estate_leads_{timestamp}.csv"
        
        # Prepare CSV data
        csv_data = []
        for lead in leads:
            row = {
                "Lead ID": lead.id,
                "Score": lead.score or 0,
                "Address": lead.address,
                "City": lead.city,
                "State": lead.state,
                "ZIP Code": lead.zip_code,
                "Property Type": lead.property_type,
                "Price": lead.price or "",
                "Bedrooms": lead.bedrooms or "",
                "Bathrooms": lead.bathrooms or "",
                "Square Feet": lead.square_feet or "",
                "Year Built": lead.year_built or "",
                "Owner Name": lead.owner_name or "",
                "Owner Phone": lead.owner_phone or "",
                "Owner Email": lead.owner_email or "",
                "Mailing Address": lead.mailing_address or "",
                "Motivation Indicators": ", ".join(lead.motivation_indicators),
                "Estimated Equity": lead.equity_estimate or "",
                "Source": lead.source,
                "Status": lead.status,
                "Human Reviewed": lead.human_reviewed,
                "Human Approved": lead.human_approved,
                "Found Date": lead.found_date.strftime("%Y-%m-%d %H:%M:%S"),
                "Notes": lead.notes or ""
            }
            csv_data.append(row)
        
        # Write CSV file
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            if csv_data:
                fieldnames = csv_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
        
        return filename
    
    async def _export_to_json(self, leads: List[Lead], timestamp: str) -> str:
        """Export leads to JSON format"""
        filename = f"{self.output_dir}/real_estate_leads_{timestamp}.json"
        
        # Convert leads to JSON-serializable format
        json_data = []
        for lead in leads:
            lead_dict = lead.dict()
            # Convert datetime to string
            lead_dict["found_date"] = lead.found_date.isoformat()
            json_data.append(lead_dict)
        
        # Write JSON file
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump({
                "export_timestamp": datetime.now().isoformat(),
                "total_leads": len(leads),
                "leads": json_data
            }, jsonfile, indent=2, ensure_ascii=False)
        
        return filename
    
    async def _export_to_excel(self, leads: List[Lead], timestamp: str) -> str:
        """Export leads to Excel format"""
        filename = f"{self.output_dir}/real_estate_leads_{timestamp}.xlsx"
        
        # Prepare DataFrame
        excel_data = []
        for lead in leads:
            row = {
                "Lead ID": lead.id,
                "Score": lead.score or 0,
                "Address": lead.address,
                "City": lead.city,
                "State": lead.state,
                "ZIP Code": lead.zip_code,
                "Property Type": lead.property_type,
                "Price": lead.price,
                "Bedrooms": lead.bedrooms,
                "Bathrooms": lead.bathrooms,
                "Square Feet": lead.square_feet,
                "Year Built": lead.year_built,
                "Owner Name": lead.owner_name,
                "Owner Phone": lead.owner_phone,
                "Owner Email": lead.owner_email,
                "Mailing Address": lead.mailing_address,
                "Motivation Indicators": ", ".join(lead.motivation_indicators) if lead.motivation_indicators else "",
                "Estimated Equity": lead.equity_estimate,
                "Source": lead.source,
                "Status": lead.status,
                "Human Reviewed": lead.human_reviewed,
                "Human Approved": lead.human_approved,
                "Found Date": lead.found_date,
                "Notes": lead.notes
            }
            excel_data.append(row)
        
        # Create DataFrame and export
        df = pd.DataFrame(excel_data)
        
        # Create Excel file with multiple sheets
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Main leads sheet
            df.to_excel(writer, sheet_name='Leads', index=False)
            
            # Summary sheet
            summary_data = {
                "Metric": [
                    "Total Leads",
                    "High Quality (70+)",
                    "Medium Quality (50-69)",
                    "With Phone Contact",
                    "With Email Contact",
                    "Human Reviewed",
                    "Human Approved"
                ],
                "Count": [
                    len(leads),
                    len([l for l in leads if (l.score or 0) >= 70]),
                    len([l for l in leads if 50 <= (l.score or 0) < 70]),
                    len([l for l in leads if l.owner_phone]),
                    len([l for l in leads if l.owner_email]),
                    len([l for l in leads if l.human_reviewed]),
                    len([l for l in leads if l.human_approved])
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        return filename
    
    async def _export_to_google_sheets(self, leads: List[Lead], timestamp: str) -> str:
        """Export leads to Google Sheets (mock implementation)"""
        # This would integrate with Google Sheets API
        print("   📊 Google Sheets export not implemented (requires API setup)")
        return "google_sheets_export_pending"
    
    async def _export_to_airtable(self, leads: List[Lead], timestamp: str) -> str:
        """Export leads to Airtable (mock implementation)"""
        # This would integrate with Airtable API
        print("   📋 Airtable export not implemented (requires API setup)")
        return "airtable_export_pending"
    
    async def _create_summary_report(self, state: AgentState, leads: List[Lead], timestamp: str) -> str:
        """Create a summary report of the lead generation process"""
        filename = f"{self.output_dir}/lead_generation_report_{timestamp}.txt"
        
        # Calculate statistics
        total_leads = len(leads)
        high_quality = len([l for l in leads if (l.score or 0) >= 70])
        medium_quality = len([l for l in leads if 50 <= (l.score or 0) < 70])
        with_phone = len([l for l in leads if l.owner_phone])
        with_email = len([l for l in leads if l.owner_email])
        
        # Top motivation indicators
        all_indicators = []
        for lead in leads:
            all_indicators.extend(lead.motivation_indicators)
        
        indicator_counts = {}
        for indicator in all_indicators:
            indicator_counts[indicator] = indicator_counts.get(indicator, 0) + 1
        
        top_indicators = sorted(indicator_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Create report
        report = f"""
🏡 REAL ESTATE LEAD GENERATION REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SEARCH QUERY: {state.user_query}

SEARCH CRITERIA:
- Location: {state.search_criteria.location if state.search_criteria else 'N/A'}
- Property Types: {', '.join(state.search_criteria.property_types) if state.search_criteria else 'N/A'}
- Lead Type: {state.search_criteria.lead_type if state.search_criteria else 'N/A'}
- Price Range: ${state.search_criteria.price_min or 'No min'} - ${state.search_criteria.price_max or 'No max'}

RESULTS SUMMARY:
- Total Leads Found: {total_leads}
- High Quality (70+ score): {high_quality} ({high_quality/total_leads*100:.1f}%)
- Medium Quality (50-69 score): {medium_quality} ({medium_quality/total_leads*100:.1f}%)
- Leads with Phone: {with_phone} ({with_phone/total_leads*100:.1f}%)
- Leads with Email: {with_email} ({with_email/total_leads*100:.1f}%)

TOP MOTIVATION INDICATORS:
"""
        
        for indicator, count in top_indicators:
            percentage = count / total_leads * 100
            report += f"- {indicator.replace('_', ' ').title()}: {count} leads ({percentage:.1f}%)\n"
        
        report += f"""
WORKFLOW STEPS:
1. Intent Analysis: {state.metadata.get('intent_analysis', {}).get('extracted_location', 'Completed')}
2. Property Search: {len(state.raw_listings)} raw listings found
3. Filtering: {len(state.filtered_listings)} listings after filtering
4. Enrichment: {len(state.enriched_leads)} leads enriched
5. Scoring: {len(state.scored_leads)} leads scored
6. Human Review: {len(state.human_reviewed_leads)} leads reviewed
7. Export: {total_leads} leads exported

TOP 5 LEADS BY SCORE:
"""
        
        # Sort leads by score and show top 5
        sorted_leads = sorted(leads, key=lambda x: x.score or 0, reverse=True)[:5]
        for i, lead in enumerate(sorted_leads, 1):
            report += f"{i}. {lead.address}, {lead.city} - Score: {lead.score:.1f}\n"
            if lead.owner_phone:
                report += f"   Phone: {lead.owner_phone}\n"
            if lead.motivation_indicators:
                report += f"   Motivation: {', '.join(lead.motivation_indicators)}\n"
            report += "\n"
        
        if state.errors:
            report += "ERRORS ENCOUNTERED:\n"
            for error in state.errors:
                report += f"- {error}\n"
        
        # Write report
        with open(filename, 'w', encoding='utf-8') as report_file:
            report_file.write(report)
        
        return filename
