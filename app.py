"""
🏡 RealEstateGenAI - AI-Powered Real Estate Lead Generation
Main application entry point with Human-in-the-Loop workflow
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
import argparse

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from graph.leadgen_graph import RealEstateLeadGenGraph
from hitl_ui.streamlit_review import launch_hitl_ui

# Load environment variables
load_dotenv()

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='Real Estate Lead Generation AI')
    parser.add_argument('--mode', choices=['cli', 'ui'], default='ui', 
                       help='Run in CLI mode or launch Streamlit UI')
    parser.add_argument('--query', type=str, 
                       help='Search query for CLI mode')
    
    args = parser.parse_args()
    
    if args.mode == 'ui':
        print("🏡 Launching RealEstateGenAI Streamlit UI...")
        launch_hitl_ui()
    elif args.mode == 'cli':
        if not args.query:
            args.query = input("Enter your real estate search query: ")
        
        print(f"🔍 Running search: {args.query}")
        asyncio.run(run_cli_mode(args.query))

async def run_cli_mode(query: str):
    """Run the lead generation in CLI mode"""
    try:
        # Initialize the graph
        graph = RealEstateLeadGenGraph()
        
        # Run the workflow
        result = await graph.run_workflow(query)
        
        print("\n✅ Lead generation complete!")
        print(f"📊 Found {len(result.get('leads', []))} leads")
        print(f"📁 Results saved to: {result.get('output_file', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
