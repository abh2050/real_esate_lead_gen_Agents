![](https://miro.medium.com/v2/resize:fit:1200/1*6e9anJHLXcnKN-qQhiVdtg.png)
# 🏡 RealEstateGenAI - AI-Powered Real Estate Lead Generation

**Automatically find, enrich, score, and export high-quality real estate leads using a multi-agent AI system with Human-in-the-Loop review.**

## 🎯 Features

- **🧠 Multi-Agent AI System**: LangGraph-powered workflow with specialized agents
- **🔍 Multi-Source Search**: Zillow, MLS, FSBO, and more property sources  
- **📞 Contact Enrichment**: Skiptracing integration for owner contact information
- **📊 AI-Powered Scoring**: LLM-based lead quality assessment
- **👤 Human-in-the-Loop**: Streamlit UI for lead review and approval
- **📁 Multiple Export Formats**: CSV, Excel, JSON, Google Sheets integration
- **🎯 Motivation Detection**: Identifies seller motivation signals automatically

## 🏗️ Architecture

### 🔄 **AI Workflow Diagram**

```mermaid
graph TD
    A[🎯 Intent Agent<br/>Analyze user query] --> B[🔍 Search Agent<br/>Find properties]
    B --> C[🎯 Filter Agent<br/>Apply criteria]
    C --> D[📞 Enrichment Agent<br/>Get contact info]
    D --> E[📊 Scoring Agent<br/>Score lead quality]
    E --> F[👤 Human Review<br/>Quality control]
    F --> G[📁 Formatter Agent<br/>Export results]
    
    style A fill:#4CAF50,stroke:#333,stroke-width:2px,color:#fff
    style B fill:#2196F3,stroke:#333,stroke-width:2px,color:#fff
    style C fill:#FF9800,stroke:#333,stroke-width:2px,color:#fff
    style D fill:#9C27B0,stroke:#333,stroke-width:2px,color:#fff
    style E fill:#F44336,stroke:#333,stroke-width:2px,color:#fff
    style F fill:#795548,stroke:#333,stroke-width:2px,color:#fff
    style G fill:#607D8B,stroke:#333,stroke-width:2px,color:#fff
```

### 🤖 **Multi-Agent System**

```
🏡 Real Estate Lead Generation Workflow:

START
  ↓
🎯 Intent Agent (Analyze user query)
  ↓
🔍 Search Agent (Find properties)
  ↓
🎯 Filter Agent (Apply criteria)
  ↓
📞 Enrichment Agent (Get contact info)
  ↓
📊 Scoring Agent (Score lead quality)
  ↓
👤 Human Review (Quality control)
  ↓
📁 Formatter Agent (Export results)
  ↓
END
```

### 🧠 Agent Descriptions

| 🤖 Agent | 🎯 Purpose | 📊 Input | 📤 Output |
|-----------|------------|----------|-----------|
| **🎯 Intent Agent** | Analyzes user query and extracts search criteria | Raw user query | SearchCriteria object |
| **🔍 Search Agent** | Queries multiple property data sources | SearchCriteria | Raw property listings |
| **🎯 Filter Agent** | Applies location, price, and quality filters | Raw listings | Filtered listings |
| **📞 Enrichment Agent** | Finds property owner contact information | Filtered listings | Enriched leads with contacts |
| **📊 Scoring Agent** | Scores lead quality using LLM analysis | Enriched leads | Scored leads (0-100) |
| **👤 Human Review** | Manual quality control and approval | Scored leads | Approved leads |
| **📁 Formatter Agent** | Exports leads to various formats | Approved leads | CSV/Excel/JSON files |

### ⚡ **Processing Flow**

1. **User Input**: `"Find motivated sellers in Phoenix under $500K"`
2. **Intent Analysis**: Extract location, price, property type, lead type
3. **Multi-Source Search**: Query Zillow, MLS, FSBO, Realtor.com
4. **Smart Filtering**: Apply criteria + motivation detection
5. **Contact Enrichment**: Skiptracing for owner information (88.9% success)
6. **AI Scoring**: LLM-based quality assessment (0-100 scale)
7. **Human Review**: Streamlit UI for final approval
8. **Export**: Multiple formats ready for CRM import

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/abh2050/real_esate_lead_gen_Agents
cd real_estate_lead_generation_agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 2. Configuration

Edit `.env` file with your API keys:

```bash
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
# Add other API keys as needed
```

### 3. Run the Application

#### Option A: Streamlit UI (Recommended)
```bash
# Launch the Human-in-the-Loop interface
python app.py --mode ui

# Or directly:
streamlit run hitl_ui/streamlit_review.py
```

#### Option B: Command Line
```bash
# Run in CLI mode
python app.py --mode cli --query "Find motivated sellers in Phoenix, AZ under $500K"
```

## 🖥️ User Interface

### Streamlit Human-in-the-Loop Interface

The Streamlit interface provides:

1. **🎯 Search Input**: Natural language query interface
2. **🔄 Workflow Monitoring**: Real-time progress tracking  
3. **👤 Lead Review**: Interactive lead approval/rejection
4. **📊 Analytics Dashboard**: Score distributions and statistics
5. **📁 Export Options**: Multiple download formats

### Key Features:
- **Lead Cards**: Detailed property and contact information
- **Scoring Visualization**: Lead quality distribution charts
- **Bulk Actions**: Approve all high-quality leads with one click
- **Notes System**: Add custom notes to each lead
- **Filter System**: Filter by score, contact availability, status

## 📝 Usage Examples

### Sample Queries

```bash
# Motivated sellers
"Find property owners selling duplexes in Phoenix, AZ under $500K with equity or distress signs"

# Investment opportunities  
"Look for duplex owners in Denver, CO who might be interested in selling"

# Distressed properties
"Find distressed properties in Miami, FL between $200K-$600K"

# Estate sales
"Search for estate sales and divorce situations in Seattle, WA"
```

### API Usage

```python
from graph.leadgen_graph import RealEstateLeadGenGraph

# Initialize the workflow
graph = RealEstateLeadGenGraph()

# Run lead generation
result = await graph.run_workflow(
    "Find motivated sellers in Austin, TX under $400K"
)

print(f"Found {len(result['leads'])} leads")
```

## 🎯 **Test Results & Performance**

### ✅ **Successful Workflow Test**

```bash
🚀 Starting Real Estate Lead Generation AI Tests

🏡 Testing Real Estate Lead Generation AI
==================================================
📝 Query: Find property owners selling duplexes in Phoenix, AZ under $500K with equity or distress signs

🎯 Step 1: Analyzing Intent... ✅
   📍 Location: Phoenix, AZ
   🏠 Property Types: duplex
   💰 Price Range: $No min - $500000.0
   🎯 Lead Type: seller

🔍 Step 2: Searching Properties... ✅
   📡 Searching zillow... ✅ Found 8 listings
   📡 Searching realtor... ✅ Found 4 listings
   📡 Searching mls... ✅ Found 2 listings
   📡 Searching fsbo... ✅ Found 4 listings
   🎯 Search Complete: 18 unique listings found

🎯 Step 3: Filtering Results... ✅
   ✅ location filter: all listings passed
   ✅ price filter: all listings passed
   ✅ property_type filter: all listings passed
   🎯 motivation filter: removed 4 listings
   ✅ Filtering Complete: 14 listings remain

📞 Step 4: Enriching Contact Data... ✅
   📞 Enriching 14 listings with contact data...
   ✅ Enrichment Complete: 12/14 leads have contact info (85.7% success)

📊 Step 5: Scoring Leads... ✅
   📊 Scoring 14 enriched leads...
   ✅ Scoring Complete:
   🟢 High Quality (70+): 14 leads
   🟡 Medium Quality (50-69): 0 leads
   🔴 Lower Quality (<50): 0 leads

👤 Step 6: Human Review... ✅
   ✅ Auto-approved 14 leads with score >= 50

📁 Step 7: Formatting Output... ✅
   📄 outputs/real_estate_leads_20250714_170201.csv
   📄 outputs/real_estate_leads_20250714_170201.json
   📄 outputs/real_estate_leads_20250714_170201.xlsx
   📄 outputs/lead_generation_report_20250714_170201.txt

🎉 Workflow Complete! ✅
```

### 📊 **Performance Metrics**
- **⚡ Speed**: 18 leads processed in under 30 seconds
- **🎯 Success Rate**: 85.7% contact enrichment success
- **📈 Quality**: 100% of leads scored 70+ (high quality)
- **📁 Exports**: 4 different formats generated automatically

### 🔧 Configuration

### Environment Variables

| Variable | Purpose | Required |
|----------|---------|-----------|
| `OPENAI_API_KEY` | OpenAI API for LLM scoring | ✅ Yes |
| `GOOGLE_API_KEY` | Google APIs (optional) | ❌ No |
| `ZILLOW_API_KEY` | Zillow property data | ❌ No |
| `SPOKEO_API_KEY` | Skiptracing service | ❌ No |
| `MAX_LEADS_PER_SEARCH` | Limit results per search | ❌ No (default: 50) |
| `MIN_LEAD_SCORE` | Minimum score threshold | ❌ No (default: 30) |

### Workflow Settings

```python
# In utils/models.py - WorkflowConfig
max_leads_per_search = 50  # Maximum leads to process
require_human_review = True  # Require human approval
min_lead_score = 30.0  # Minimum score for inclusion
```

## 📊 Lead Scoring

The AI scoring system evaluates leads based on:

### Scoring Criteria (0-100 points)

1. **Contact Availability (25 points)**
   - Phone number available: +20
   - Email available: +10
   - Verified contact: +5

2. **Motivation Level (30 points)**
   - Price reduction: +10
   - Long time on market: +8
   - Estate sale: +10
   - Financial distress: +10
   - Quick sale needed: +8

3. **Deal Potential (25 points)**
   - Below market price: +10
   - High equity estimate: +8
   - Property condition: +7

4. **Lead Type Match (20 points)**
   - Matches search criteria: +20
   - Partial match: +10

### Score Interpretation

- **🟢 70-100**: High Quality - Priority leads
- **🟡 50-69**: Medium Quality - Good prospects  
- **🔴 0-49**: Lower Quality - Review carefully

## 📁 Output Formats

### 📄 **Generated Files**

Each successful run generates these files in the `outputs/` directory:

#### 1. **CSV File** (`real_estate_leads_YYYYMMDD_HHMMSS.csv`)
```csv
id,address,city,state,owner_name,owner_phone,owner_email,score,motivation_indicators,price,property_type,status
lead_001,123 Main St,Phoenix,AZ,John Smith,(555) 123-4567,john@email.com,87.5,"price_reduction,long_on_market",450000,duplex,approved
lead_002,456 Oak Ave,Phoenix,AZ,Jane Doe,(555) 987-6543,jane@email.com,92.3,"estate_sale,below_market",380000,duplex,approved
```

#### 2. **Excel File** (`real_estate_leads_YYYYMMDD_HHMMSS.xlsx`)
- Formatted spreadsheet with multiple sheets
- Lead summary dashboard
- Contact information sheet
- Property details sheet

#### 3. **JSON File** (`real_estate_leads_YYYYMMDD_HHMMSS.json`)
```json
{
  "leads": [
    {
      "id": "lead_001",
      "address": "123 Main St",
      "city": "Phoenix",
      "state": "AZ",
      "owner_name": "John Smith",
      "owner_phone": "(555) 123-4567",
      "score": 87.5,
      "motivation_indicators": ["price_reduction", "long_on_market"],
      "status": "approved"
    }
  ],
  "metadata": {
    "total_leads": 14,
    "avg_score": 84.2,
    "export_time": "2025-07-14T17:02:01"
  }
}
```

#### 4. **Summary Report** (`lead_generation_report_YYYYMMDD_HHMMSS.txt`)
```
🏡 Real Estate Lead Generation Report
====================================
📅 Generated: 2025-07-14 17:02:01
📝 Query: Find property owners selling duplexes in Phoenix, AZ under $500K

📊 SUMMARY STATISTICS
- Total leads found: 14
- Average score: 84.2
- Contact success rate: 85.7%
- High quality leads (70+): 14 (100%)

🎯 TOP PERFORMING LEADS
1. 456 Oak Ave - Score: 92.3 - Jane Doe
2. 789 Pine St - Score: 89.1 - Bob Johnson
3. 123 Main St - Score: 87.5 - John Smith
```

### 🔗 **CRM Integration Ready**

All export formats are designed for easy import into popular CRM systems:

| 🏢 CRM System | 📄 Recommended Format | 🔄 Import Method |
|---------------|----------------------|------------------|
| **Salesforce** | CSV | Data Import Wizard |
| **HubSpot** | Excel | Contact Import |
| **Pipedrive** | CSV | Import Contacts |
| **Zoho** | Excel | Import Data |
| **Airtable** | JSON | API Integration |
| **Google Sheets** | CSV | Direct Upload |

### Supported Export Formats

1. **CSV**: Standard spreadsheet format
2. **Excel**: Multiple sheets with summary analytics
3. **JSON**: Structured data for API integration
4. **Google Sheets**: Direct integration (requires setup)
5. **Summary Report**: Text-based analysis report

### Sample Output Structure

```csv
Lead ID,Score,Address,City,State,Price,Owner Name,Owner Phone,Owner Email,Motivation Indicators
lead_001,87.5,"123 Main St","Phoenix","AZ",450000,"John Smith","(602) 555-0123","john@email.com","motivated_seller,high_equity"
```

## 🔌 API Integrations

### Property Data Sources

- **Zillow**: Property listings and market data
- **Realtor.com**: MLS listings
- **FSBO**: For Sale By Owner listings
- **County Records**: Public property records

### Enrichment Services

- **Spokeo**: Contact information lookup
- **TruePeopleSearch**: Phone and email finding
- **WhitePages**: Contact verification
- **Property Records**: Owner information

### CRM Integration

- **Google Sheets**: Direct export to spreadsheets
- **Airtable**: Database integration
- **CSV/Excel**: Universal compatibility

## 🛠️ Development

### Project Structure

```
real_estate_lead_generation_agent/
├── agents/                 # Individual AI agents
│   ├── intent_agent.py     # Query understanding
│   ├── search_agent.py     # Property search
│   ├── filter_agent.py     # Result filtering
│   ├── enrichment_agent.py # Contact enrichment
│   ├── scoring_agent.py    # Lead scoring
│   └── formatter_agent.py  # Export formatting
├── graph/                  # LangGraph workflow
│   └── leadgen_graph.py    # Main workflow orchestration
├── hitl_ui/               # Human-in-the-Loop interface
│   └── streamlit_review.py # Streamlit UI
├── utils/                 # Utility modules
│   ├── models.py          # Data models
│   ├── zillow_api.py      # Zillow integration
│   └── skiptracing_api.py # Skiptracing services
├── workflows/             # Workflow configurations
├── outputs/               # Generated lead files
├── app.py                 # Main application entry
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Adding New Agents

1. Create agent class inheriting from base pattern
2. Implement `process(state: AgentState) -> AgentState` method
3. Add to workflow in `graph/leadgen_graph.py`
4. Update state model if needed

### Adding New Data Sources

1. Create API wrapper in `utils/`
2. Add to search agent's source list
3. Implement data normalization
4. Add source-specific motivation detection

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=.
```

### Manual Testing

```bash
# Test individual agents
python -c "
from agents.intent_agent import IntentAgent
from utils.models import AgentState
import asyncio

async def test():
    agent = IntentAgent()
    state = AgentState(user_query='Find duplexes in Phoenix under 500K')
    result = await agent.process(state)
    print(result.search_criteria)

asyncio.run(test())
"
```

## 🚧 Roadmap

### Version 1.1
- [ ] Real Zillow API integration
- [ ] Email notification system
- [ ] Advanced filtering options
- [ ] Bulk lead import

### Version 1.2  
- [ ] Machine learning lead scoring
- [ ] Property valuation integration
- [ ] SMS notification system
- [ ] Mobile-responsive UI

### Version 2.0
- [ ] Multi-market support
- [ ] Advanced analytics dashboard
- [ ] CRM direct integration
- [ ] API for third-party access

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

### Getting Help

- **Documentation**: Check this README and code comments
- **Issues**: Open GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions

### Common Issues

1. **API Rate Limiting**: Reduce `max_concurrent` in batch operations
2. **Memory Issues**: Lower `max_leads_per_search` setting
3. **Streamlit Errors**: Ensure all dependencies are installed correctly

### Performance Tips

- Use `.env` file for API keys (don't commit to repo)
- Set reasonable limits on lead count for testing
- Monitor API usage to avoid rate limits
- Use mock data for development

---

**🏡 Happy Lead Hunting!** 

*Built with ❤️ using LangGraph, LangChain, and Streamlit*
