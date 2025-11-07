#!/usr/bin/env python3
"""
Comprehensive test suite for the new visualization system
"""

import os
import sys
import asyncio
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
load_dotenv()

# Test parameters
TEST_CHARTS = [
    {
        'name': 'test_customer_segments',
        'sql': 'SELECT "Segment", COUNT(*) AS segment_count FROM rfm GROUP BY "Segment" ORDER BY segment_count DESC;',
        'plotly': '''fig = px.pie(df, names='Segment', values='segment_count', title='Customer Segments Distribution')
fig.update_traces(textposition='inside', textinfo='percent+label')'''
    },
    {
        'name': 'test_top_customers',
        'sql': 'SELECT c."Name", SUM(t."TotalPrice") AS total_spending FROM customers c JOIN transactions t ON c."Customer ID" = t."Customer ID" GROUP BY c."Customer ID", c."Name" ORDER BY total_spending DESC LIMIT 5;',
        'plotly': '''fig = px.bar(df, x='Name', y='total_spending', title='Top 5 Customers by Total Spending')
fig.update_layout(xaxis_title='Customer', yaxis_title='Total Spending ($)')'''
    },
    {
        'name': 'test_sales_scatter',
        'sql': 'SELECT "R" as recency_score, "M" as monetary_score FROM rfm LIMIT 100;',
        'plotly': '''fig = px.scatter(df, x='recency_score', y='monetary_score', title='Customer RFM Analysis: Recency vs Monetary')
fig.update_layout(xaxis_title='Recency Score', yaxis_title='Monetary Score')'''
    }
]

async def test_visualization_system():
    """Test the new visualization system comprehensively."""
    
    print("🧪 Testing New Visualization System")
    print("=" * 50)
    
    try:
        # Import the new visualization tool
        from neo.my_mcp.servers.marketing_server import generate_visualization
        from neo.visualization import VisualizationEngine, ChartDisplayManager, ChartUtils
        
        print("✅ Successfully imported visualization modules")
        
        # Initialize components
        viz_engine = VisualizationEngine()
        display_manager = ChartDisplayManager()
        
        print("✅ Visualization engine initialized")
        
        # Test each chart type
        test_results = []
        
        for i, test_chart in enumerate(TEST_CHARTS, 1):
            print(f"\n📊 Test {i}: {test_chart['name']}")
            print("-" * 30)
            
            try:
                # Test the visualization function
                result = await generate_visualization(
                    name=test_chart['name'],
                    sql_query=test_chart['sql'],
                    plotly_code=test_chart['plotly']
                )
                
                # Check if it was successful
                if "📊 Chart Generated Successfully!" in result:
                    print(f"✅ {test_chart['name']}: SUCCESS")
                    test_results.append((test_chart['name'], True, "Chart generated successfully"))
                    
                    # Print result summary
                    print(result)
                    
                else:
                    print(f"❌ {test_chart['name']}: FAILED")
                    print(f"Result: {result}")
                    test_results.append((test_chart['name'], False, result))
                    
            except Exception as e:
                print(f"❌ {test_chart['name']}: ERROR")
                print(f"Error: {e}")
                test_results.append((test_chart['name'], False, str(e)))
                
        # Test chart listing and management
        print(f"\n📋 Testing Chart Management")
        print("-" * 30)
        
        try:
            charts = viz_engine.list_recent_charts()
            print(f"✅ Listed {len(charts)} charts")
            
            if charts:
                # Test gallery display
                gallery = display_manager.show_chart_gallery(charts[:3])
                print("✅ Chart gallery generated")
                
                # Test chart preview
                if charts and 'json' in charts[0]['available_formats']:
                    preview = display_manager.display_chart_quick_preview(charts[0]['json_path'])
                    print("✅ Chart preview generated")
                    
        except Exception as e:
            print(f"❌ Chart management test failed: {e}")
            
        # Test utility functions
        print(f"\n🔧 Testing Utility Functions")
        print("-" * 30)
        
        try:
            # Test SQL validation
            valid_sql = 'SELECT * FROM customers LIMIT 5'
            invalid_sql = 'DROP TABLE customers'
            
            is_valid, _ = ChartUtils.validate_sql_query(valid_sql)
            is_invalid, _ = ChartUtils.validate_sql_query(invalid_sql)
            
            if is_valid and not is_invalid:
                print("✅ SQL validation working correctly")
            else:
                print("❌ SQL validation failed")
                
            # Test plotly validation
            valid_plotly = 'fig = px.bar(df, x="col1", y="col2")'
            invalid_plotly = 'import os; os.system("rm -rf /")'
            
            is_valid, _ = ChartUtils.validate_plotly_code(valid_plotly)
            is_invalid, _ = ChartUtils.validate_plotly_code(invalid_plotly)
            
            if is_valid and not is_invalid:
                print("✅ Plotly validation working correctly")
            else:
                print("❌ Plotly validation failed")
                
        except Exception as e:
            print(f"❌ Utility function test failed: {e}")
            
        # Summary report
        print(f"\n📊 Test Summary")
        print("=" * 50)
        
        successful_tests = sum(1 for _, success, _ in test_results if success)
        total_tests = len(test_results)
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        if successful_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! The visualization system is working correctly.")
        else:
            print(f"\n⚠️  {total_tests - successful_tests} tests failed. Please check the errors above.")
            
        # Show failed tests
        failed_tests = [test for test in test_results if not test[1]]
        if failed_tests:
            print(f"\n❌ Failed Tests:")
            for name, _, error in failed_tests:
                print(f"  • {name}: {error}")
                
        # Final recommendations
        print(f"\n💡 Recommendations:")
        print("  • Charts are now saved in output/charts/ directory")
        print("  • Use 'python chart_viewer.py' for chart management")
        print("  • Charts auto-open in browser when generated")
        print("  • Multiple formats available: HTML, JSON, PNG")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure you have installed all dependencies:")
        print("  pip install plotly kaleido pandas sqlalchemy")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_visualization_system())