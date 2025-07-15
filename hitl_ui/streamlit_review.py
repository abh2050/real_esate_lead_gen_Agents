"""
Streamlit Human-in-the-Loop Interface for Real Estate Lead Review
"""

import streamlit as st
import pandas as pd
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.leadgen_graph import RealEstateLeadGenGraph
from utils.models import Lead, AgentState

# Configure Streamlit page
st.set_page_config(
    page_title="🏡 RealEstateGenAI",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

class StreamlitHITLInterface:
    """Streamlit interface for human-in-the-loop lead review"""
    
    def __init__(self):
        self.graph = RealEstateLeadGenGraph()
        
        # Initialize session state
        if 'leads_data' not in st.session_state:
            st.session_state.leads_data = []
        if 'workflow_state' not in st.session_state:
            st.session_state.workflow_state = None
        if 'current_step' not in st.session_state:
            st.session_state.current_step = "input"
    
    def render(self):
        """Render the main Streamlit interface"""
        
        # Header
        st.title("🏡 RealEstateGenAI")
        st.markdown("**AI-Powered Real Estate Lead Generation with Human-in-the-Loop Review**")
        
        # Sidebar
        with st.sidebar:
            st.header("🎯 Workflow Status")
            self._render_workflow_status()
            
            st.header("📊 Quick Stats")
            if st.session_state.leads_data:
                self._render_quick_stats()
        
        # Main content based on current step
        if st.session_state.current_step == "input":
            self._render_input_interface()
        elif st.session_state.current_step == "processing":
            self._render_processing_interface()
        elif st.session_state.current_step == "review":
            self._render_review_interface()
        elif st.session_state.current_step == "complete":
            self._render_completion_interface()
    
    def _render_workflow_status(self):
        """Render workflow status in sidebar"""
        steps = [
            ("🎯 Intent Analysis", "intent"),
            ("🔍 Property Search", "search"),
            ("🎯 Filtering", "filter"),
            ("📞 Enrichment", "enrichment"),
            ("📊 Scoring", "scoring"),
            ("👤 Human Review", "review"),
            ("📁 Export", "complete")
        ]
        
        current = st.session_state.current_step
        
        for i, (step_name, step_key) in enumerate(steps):
            if step_key == current:
                st.markdown(f"🔄 **{step_name}**")
            elif any(step[1] == current for j, step in enumerate(steps) if j > i):
                st.markdown(f"✅ {step_name}")
            else:
                st.markdown(f"⏳ {step_name}")
    
    def _render_quick_stats(self):
        """Render quick statistics"""
        leads = st.session_state.leads_data
        
        total_leads = len(leads)
        high_quality = len([l for l in leads if l.get('score', 0) >= 70])
        with_contact = len([l for l in leads if l.get('owner_phone') or l.get('owner_email')])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Leads", total_leads)
            st.metric("High Quality", high_quality)
        with col2:
            st.metric("With Contact", with_contact)
            approval_rate = f"{len([l for l in leads if l.get('human_approved', False)]) / max(total_leads, 1) * 100:.1f}%"
            st.metric("Approval Rate", approval_rate)
    
    def _render_input_interface(self):
        """Render the input interface for starting lead generation"""
        
        st.header("🎯 Start Lead Generation")
        
        # Input form
        with st.form("lead_generation_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Search Criteria")
                query = st.text_area(
                    "Describe what you're looking for:",
                    placeholder="Find property owners selling duplexes in Phoenix, AZ under $500K with equity or distress signs",
                    height=100
                )
                
                location = st.text_input("Location", placeholder="Phoenix, AZ")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    min_price = st.number_input("Min Price ($)", min_value=0, value=0, step=10000)
                with col_b:
                    max_price = st.number_input("Max Price ($)", min_value=0, value=500000, step=10000)
            
            with col2:
                st.subheader("Lead Preferences")
                
                lead_type = st.selectbox(
                    "Lead Type",
                    ["seller", "buyer", "investor"],
                    index=0
                )
                
                property_types = st.multiselect(
                    "Property Types",
                    ["single-family", "duplex", "triplex", "apartment", "townhouse", "condo"],
                    default=["single-family", "duplex"]
                )
                
                motivation_signals = st.multiselect(
                    "Desired Motivation Signals",
                    ["motivated_seller", "price_reduction", "estate_sale", "financial_distress", 
                     "quick_sale_needed", "high_equity", "vacant_property"],
                    default=["motivated_seller", "high_equity"]
                )
            
            # Submit button
            submitted = st.form_submit_button("🚀 Start Lead Generation", type="primary", use_container_width=True)
            
            if submitted and query:
                # Start the workflow
                self._start_workflow(query, {
                    "location": location,
                    "min_price": min_price if min_price > 0 else None,
                    "max_price": max_price if max_price > 0 else None,
                    "lead_type": lead_type,
                    "property_types": property_types,
                    "motivation_signals": motivation_signals
                })
        
        # Sample queries
        st.header("💡 Sample Queries")
        sample_queries = [
            "Find motivated sellers in Austin, TX with properties under $400K",
            "Look for duplex owners in Denver, CO who might be interested in selling",
            "Find distressed properties in Miami, FL between $200K-$600K",
            "Search for estate sales and divorce situations in Seattle, WA"
        ]
        
        for query in sample_queries:
            if st.button(f"📝 {query}", key=f"sample_{hash(query)}"):
                st.text_area("Query", value=query, key="sample_query_display")
    
    def _render_processing_interface(self):
        """Render processing status during workflow execution"""
        
        st.header("🔄 Processing Your Request")
        
        # Progress bar (placeholder - in real implementation, this would be dynamic)
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulate progress updates
        steps = [
            "🎯 Analyzing your requirements...",
            "🔍 Searching property databases...",
            "🎯 Filtering results by criteria...",
            "📞 Enriching contact information...",
            "📊 Scoring lead quality...",
            "✅ Ready for human review!"
        ]
        
        for i, step in enumerate(steps):
            status_text.text(step)
            progress_bar.progress((i + 1) / len(steps))
            
            # In real implementation, this would wait for actual workflow steps
            import time
            time.sleep(1)
        
        # Transition to review
        st.session_state.current_step = "review"
        st.rerun()
    
    def _render_review_interface(self):
        """Render the human review interface"""
        
        st.header("👤 Human Review & Approval")
        
        if not st.session_state.leads_data:
            st.warning("No leads to review. Please start a new search.")
            if st.button("🔄 Start New Search"):
                st.session_state.current_step = "input"
                st.rerun()
            return
        
        # Review controls
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown("**Review and approve/reject leads below:**")
        with col2:
            if st.button("✅ Approve All High Quality (70+)", type="secondary"):
                self._approve_high_quality_leads()
                st.rerun()
        with col3:
            if st.button("📁 Export Approved Leads", type="primary"):
                self._export_approved_leads()
        
        # Filters
        st.subheader("🔍 Filters")
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            score_filter = st.slider("Minimum Score", 0, 100, 0)
        with filter_col2:
            contact_filter = st.selectbox("Contact Info", ["All", "Phone Available", "Email Available", "No Contact"])
        with filter_col3:
            status_filter = st.selectbox("Status", ["All", "New", "Approved", "Rejected"])
        
        # Filter leads
        filtered_leads = self._filter_leads(score_filter, contact_filter, status_filter)
        
        # Lead review cards
        st.subheader(f"📋 Leads for Review ({len(filtered_leads)} shown)")
        
        for i, lead in enumerate(filtered_leads):
            self._render_lead_card(lead, i)
        
        # Summary stats
        self._render_review_summary()
    
    def _render_lead_card(self, lead: Dict[str, Any], index: int):
        """Render individual lead review card"""
        
        # Determine card styling based on score
        score = lead.get('score', 0)
        if score >= 70:
            card_color = "🟢"
        elif score >= 50:
            card_color = "🟡"
        else:
            card_color = "🔴"
        
        with st.expander(f"{card_color} {lead.get('address', 'Unknown Address')} - Score: {score:.1f}", expanded=False):
            
            # Lead information columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Property Info**")
                st.write(f"📍 {lead.get('address', 'N/A')}")
                st.write(f"🏠 {lead.get('property_type', 'N/A')}")
                st.write(f"💰 ${lead.get('price', 0):,}")
                st.write(f"🛏️ {lead.get('bedrooms', 'N/A')} bed / {lead.get('bathrooms', 'N/A')} bath")
                st.write(f"📐 {lead.get('square_feet', 'N/A')} sq ft")
            
            with col2:
                st.markdown("**Contact Info**")
                st.write(f"👤 {lead.get('owner_name', 'Unknown')}")
                st.write(f"📞 {lead.get('owner_phone', 'No phone')}")
                st.write(f"📧 {lead.get('owner_email', 'No email')}")
                st.write(f"📮 {lead.get('mailing_address', 'N/A')}")
                
                if lead.get('equity_estimate'):
                    st.write(f"💵 Est. Equity: ${lead.get('equity_estimate', 0):,}")
            
            with col3:
                st.markdown("**Lead Quality**")
                st.write(f"⭐ Score: {score:.1f}/100")
                st.write(f"📊 Source: {lead.get('source', 'N/A')}")
                
                motivation = lead.get('motivation_indicators', [])
                if motivation:
                    st.write("🎯 Motivation:")
                    for indicator in motivation:
                        st.write(f"  • {indicator.replace('_', ' ').title()}")
            
            # Action buttons and notes
            action_col1, action_col2, action_col3 = st.columns([1, 1, 2])
            
            lead_key = f"lead_{index}"
            
            with action_col1:
                if st.button("✅ Approve", key=f"approve_{lead_key}"):
                    lead['human_approved'] = True
                    lead['human_reviewed'] = True
                    lead['status'] = 'approved'
                    st.success("Lead approved!")
                    st.rerun()
            
            with action_col2:
                if st.button("❌ Reject", key=f"reject_{lead_key}"):
                    lead['human_approved'] = False
                    lead['human_reviewed'] = True
                    lead['status'] = 'rejected'
                    st.error("Lead rejected!")
                    st.rerun()
            
            with action_col3:
                notes = st.text_input("Notes:", key=f"notes_{lead_key}", placeholder="Add notes about this lead...")
                if notes:
                    lead['notes'] = notes
    
    def _render_review_summary(self):
        """Render review summary and analytics"""
        
        st.header("📊 Review Analytics")
        
        leads = st.session_state.leads_data
        
        # Score distribution
        scores = [lead.get('score', 0) for lead in leads]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Score distribution histogram
            fig_hist = px.histogram(
                x=scores,
                nbins=20,
                title="Lead Score Distribution",
                labels={'x': 'Lead Score', 'y': 'Count'}
            )
            fig_hist.update_layout(showlegend=False)
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Approval status pie chart
            approved = len([l for l in leads if l.get('human_approved', False)])
            rejected = len([l for l in leads if l.get('human_reviewed', False) and not l.get('human_approved', False)])
            pending = len(leads) - approved - rejected
            
            fig_pie = px.pie(
                values=[approved, rejected, pending],
                names=['Approved', 'Rejected', 'Pending'],
                title="Review Status",
                color_discrete_map={'Approved': 'green', 'Rejected': 'red', 'Pending': 'orange'}
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    def _render_completion_interface(self):
        """Render completion interface after export"""
        
        st.header("🎉 Lead Generation Complete!")
        
        st.success("Your leads have been successfully processed and exported!")
        
        # Summary metrics
        leads = st.session_state.leads_data
        approved_leads = [l for l in leads if l.get('human_approved', False)]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Leads Found", len(leads))
        with col2:
            st.metric("Leads Approved", len(approved_leads))
        with col3:
            high_quality = len([l for l in approved_leads if l.get('score', 0) >= 70])
            st.metric("High Quality", high_quality)
        with col4:
            with_contact = len([l for l in approved_leads if l.get('owner_phone') or l.get('owner_email')])
            st.metric("With Contact Info", with_contact)
        
        # Download buttons (placeholder)
        st.subheader("📁 Download Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                "📄 Download CSV",
                data="CSV content here",  # In real implementation, generate actual CSV
                file_name=f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            st.download_button(
                "📊 Download Excel",
                data="Excel content here",  # In real implementation, generate actual Excel
                file_name=f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col3:
            st.download_button(
                "📋 Download Report",
                data="Report content here",  # In real implementation, generate actual report
                file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        
        # Start new search
        if st.button("🔄 Start New Search", type="primary"):
            # Reset session state
            st.session_state.leads_data = []
            st.session_state.workflow_state = None
            st.session_state.current_step = "input"
            st.rerun()
    
    def _start_workflow(self, query: str, criteria: Dict[str, Any]):
        """Start the lead generation workflow"""
        st.session_state.current_step = "processing"
        st.session_state.user_query = query
        st.session_state.search_criteria = criteria
        
        # For demo purposes, generate mock leads
        # In real implementation, this would call the actual workflow
        mock_leads = self._generate_mock_leads(criteria)
        st.session_state.leads_data = mock_leads
        
        st.rerun()
    
    def _generate_mock_leads(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate mock leads for demonstration"""
        import random
        
        mock_leads = []
        
        for i in range(random.randint(15, 30)):
            lead = {
                "id": f"lead_{i+1:03d}",
                "address": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm'])} {random.choice(['St', 'Ave', 'Dr'])}",
                "city": criteria.get("location", "Phoenix").split(",")[0],
                "state": "AZ",
                "zip_code": f"{random.randint(85000, 85999)}",
                "property_type": random.choice(criteria.get("property_types", ["single-family"])),
                "price": random.randint(200000, 800000),
                "bedrooms": random.randint(2, 5),
                "bathrooms": random.choice([1.0, 1.5, 2.0, 2.5, 3.0]),
                "square_feet": random.randint(1200, 3500),
                "year_built": random.randint(1980, 2020),
                "owner_name": f"Owner {i+1}",
                "owner_phone": f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}" if random.random() > 0.3 else None,
                "owner_email": f"owner{i+1}@email.com" if random.random() > 0.5 else None,
                "score": random.uniform(20, 95),
                "motivation_indicators": random.sample(criteria.get("motivation_signals", []), k=random.randint(0, 2)),
                "source": random.choice(["zillow", "mls", "fsbo"]),
                "human_reviewed": False,
                "human_approved": False,
                "status": "new"
            }
            mock_leads.append(lead)
        
        return mock_leads
    
    def _filter_leads(self, score_filter: int, contact_filter: str, status_filter: str) -> List[Dict[str, Any]]:
        """Filter leads based on criteria"""
        leads = st.session_state.leads_data
        filtered = []
        
        for lead in leads:
            # Score filter
            if lead.get('score', 0) < score_filter:
                continue
            
            # Contact filter
            if contact_filter == "Phone Available" and not lead.get('owner_phone'):
                continue
            elif contact_filter == "Email Available" and not lead.get('owner_email'):
                continue
            elif contact_filter == "No Contact" and (lead.get('owner_phone') or lead.get('owner_email')):
                continue
            
            # Status filter
            if status_filter != "All":
                lead_status = lead.get('status', 'new')
                if status_filter.lower() != lead_status:
                    continue
            
            filtered.append(lead)
        
        return filtered
    
    def _approve_high_quality_leads(self):
        """Auto-approve all leads with score >= 70"""
        count = 0
        for lead in st.session_state.leads_data:
            if lead.get('score', 0) >= 70:
                lead['human_approved'] = True
                lead['human_reviewed'] = True
                lead['status'] = 'approved'
                count += 1
        
        st.success(f"Approved {count} high-quality leads!")
    
    def _export_approved_leads(self):
        """Export approved leads"""
        approved_leads = [l for l in st.session_state.leads_data if l.get('human_approved', False)]
        
        if not approved_leads:
            st.warning("No approved leads to export!")
            return
        
        # In real implementation, this would call the formatter agent
        st.session_state.current_step = "complete"
        st.success(f"Exporting {len(approved_leads)} approved leads...")

def launch_hitl_ui():
    """Launch the Streamlit HITL interface"""
    interface = StreamlitHITLInterface()
    interface.render()

if __name__ == "__main__":
    launch_hitl_ui()
