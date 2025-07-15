#!/usr/bin/env python3
"""
Quick test script for Real Estate Lead Generation AI
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from graph.leadgen_graph import RealEstateLeadGenGraph

async def test_workflow():
    """Test the complete workflow with a sample query"""
    
    print("🏡 Testing Real Estate Lead Generation AI")
    print("=" * 50)
    
    # Sample query
    query = "Find property owners selling duplexes in Phoenix, AZ under $500K with equity or distress signs"
    
    try:
        # Initialize the graph
        graph = RealEstateLeadGenGraph()
        
        print(f"📝 Query: {query}")
        print("\n🔄 Starting workflow...\n")
        
        # Run the workflow
        result = await graph.run_workflow(query)
        
        if result["success"]:
            print("\n🎉 Test Successful!")
            print(f"📊 Found {result['total_leads']} leads")
            
            if result.get('output_file'):
                print(f"📁 Output saved to: {result['output_file']}")
            
            # Show sample leads
            if result['leads']:
                print("\n📋 Sample leads:")
                for i, lead in enumerate(result['leads'][:3], 1):
                    print(f"  {i}. {lead.get('address', 'N/A')} - Score: {lead.get('score', 0):.1f}")
        else:
            print(f"❌ Test Failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test Failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_individual_agents():
    """Test individual agents"""
    
    print("\n🧪 Testing Individual Agents")
    print("=" * 30)
    
    from agents.intent_agent import IntentAgent
    from utils.models import AgentState
    
    try:
        # Test Intent Agent
        print("🎯 Testing Intent Agent...")
        intent_agent = IntentAgent()
        
        state = AgentState(user_query="Find motivated sellers in Austin, TX under $400K")
        result_state = await intent_agent.process(state)
        
        if result_state.search_criteria:
            print(f"   ✅ Intent analysis successful")
            print(f"   📍 Location: {result_state.search_criteria.location}")
            print(f"   💰 Max Price: ${result_state.search_criteria.price_max or 'No limit'}")
        else:
            print("   ❌ Intent analysis failed")
            
    except Exception as e:
        print(f"   ❌ Intent Agent test failed: {str(e)}")

def main():
    """Main test function"""
    print("🚀 Starting Real Estate Lead Generation AI Tests\n")
    
    # Check if we can import required modules
    try:
        import langchain
        import langgraph
        import streamlit
        print("✅ Required packages imported successfully")
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return
    
    # Run async tests
    asyncio.run(test_workflow())
    asyncio.run(test_individual_agents())
    
    print("\n🏁 Tests completed!")
    print("\nNext steps:")
    print("1. Set up your .env file with API keys")
    print("2. Run the Streamlit UI: python app.py --mode ui")
    print("3. Or try CLI mode: python app.py --mode cli")

if __name__ == "__main__":
    main()
