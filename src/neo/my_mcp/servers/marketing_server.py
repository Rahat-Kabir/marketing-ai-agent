from mcp.server.fastmcp import FastMCP
from sqlalchemy import text
import os
import pandas as pd
from dotenv import load_dotenv
from uuid import UUID
import json
import io
from contextlib import redirect_stdout, redirect_stderr

load_dotenv()


# ----------------------------
# DB Session
# ----------------------------

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(url=os.getenv("SUPABASE_URI"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ----------------------------
# MCP Server
# ----------------------------

mcp = FastMCP("marketing")


@mcp.tool()
async def create_campaign(
    name: str,
    type: str,
    description: str,
) -> str:
    """Create a marketing campaign.
    
    Args:
        name: The name of the campaign.
        type: The type of the campaign. One of: loyalty, referral, re-engagement
        description: The description of the campaign.

    Returns:
        The ID of the created campaign.
    """
    with SessionLocal() as session:
        result = session.execute(
            text(
                """
                INSERT INTO marketing_campaigns (name, type, description)
                VALUES (:name, :type, :description)
                RETURNING id
                """
            ),
            {"name": name, "type": type, "description": description},
        )
        session.commit()
        return str(result.fetchone()[0])

@mcp.tool()
async def send_campaign_email(
    campaign_id: UUID,
    customer_id: int,
    subject: str,
    body: str,
) -> str:
    """Send a campaign email.
    
    Args:
        campaign_id: The ID of the campaign.
        customer_id: The ID of the customer.
        subject: The subject of the email.
        body: The body of the email.

    Returns:
        A confirmation that the email was sent.
    """
    # TODO: Send email via MCP

    # Create email record in db
    with SessionLocal() as session:
        session.execute(
            text(
                """
                INSERT INTO campaign_emails (campaign_id, customer_id, subject, body)
                VALUES (:campaign_id, :customer_id, :subject, :body)
                """
            ),
            {"campaign_id": campaign_id, "customer_id": customer_id, "subject": subject, "body": body},
        )
        session.commit()

    return f"Successfully sent <{subject}> to customer <{customer_id}>!"


# ----------------------------
# Social Media Campaign Tools
# ----------------------------

@mcp.tool()
async def create_social_media_campaign(
    name: str,
    platform: str,
    target_segment: str,
    campaign_objective: str = None,
) -> str:
    """Create a social media marketing campaign for a specific platform and customer segment.

    Args:
        name: The name of the social media campaign.
        platform: The social media platform. One of: facebook, linkedin, instagram, twitter
        target_segment: The customer segment to target. One of: Champion, Recent Customer, Frequent Buyer, Big Spender, At Risk, Others
        campaign_objective: Optional objective/description of the campaign.

    Returns:
        The ID of the created social media campaign.
    """
    with SessionLocal() as session:
        result = session.execute(
            text(
                """
                INSERT INTO social_media_campaigns (name, platform, target_segment, campaign_objective)
                VALUES (:name, :platform, :target_segment, :campaign_objective)
                RETURNING id
                """
            ),
            {
                "name": name,
                "platform": platform,
                "target_segment": target_segment,
                "campaign_objective": campaign_objective
            },
        )
        session.commit()
        campaign_id = str(result.fetchone()[0])

        # Add target audience to campaign_audience table
        session.execute(
            text(
                """
                INSERT INTO campaign_audience (campaign_id, customer_id, segment)
                SELECT :campaign_id, "Customer ID", :segment
                FROM rfm
                WHERE "Segment" = :segment
                """
            ),
            {"campaign_id": campaign_id, "segment": target_segment},
        )
        session.commit()

        return campaign_id


@mcp.tool()
async def generate_social_media_post(
    campaign_id: str,
    platform: str,
    post_tone: str = "friendly",
) -> str:
    """Generate a social media post for a specific campaign and platform.

    Args:
        campaign_id: The ID of the social media campaign.
        platform: The social media platform. One of: facebook, linkedin, instagram, twitter
        post_tone: The tone of the post. One of: professional, casual, friendly, promotional, educational

    Returns:
        The generated post content with platform-specific formatting.
    """
    # Get campaign details
    with SessionLocal() as session:
        campaign_result = session.execute(
            text(
                """
                SELECT name, target_segment, campaign_objective
                FROM social_media_campaigns
                WHERE id = :campaign_id
                """
            ),
            {"campaign_id": campaign_id},
        )
        campaign_data = campaign_result.fetchone()

        if not campaign_data:
            return "Campaign not found"

        _, target_segment, objective = campaign_data

        # Generate platform-specific content based on segment and platform
        post_content = _generate_platform_content(
            platform, target_segment, objective, post_tone
        )

        # Generate hashtags
        hashtags = _generate_hashtags(platform, target_segment)

        # Save the generated post
        session.execute(
            text(
                """
                INSERT INTO social_media_posts (campaign_id, platform, post_content, post_tone, hashtags)
                VALUES (:campaign_id, :platform, :post_content, :post_tone, :hashtags)
                """
            ),
            {
                "campaign_id": campaign_id,
                "platform": platform,
                "post_content": post_content,
                "post_tone": post_tone,
                "hashtags": hashtags,
            },
        )
        session.commit()

        return f"Generated {platform} post:\n\n{post_content}\n\n{hashtags}"


def _generate_platform_content(platform: str, segment: str, objective: str, tone: str) -> str:
    """Generate platform-specific content based on customer segment."""

    # Segment-specific messaging
    segment_messages = {
        "Champion": "Thank you for being our most valued customer!",
        "Recent Customer": "Welcome to our community!",
        "Frequent Buyer": "We appreciate your continued loyalty!",
        "Big Spender": "Exclusive offers for our premium customers",
        "At Risk": "We miss you! Come back and see what's new",
        "Others": "Discover what makes us special"
    }

    base_message = segment_messages.get(segment, "Join our community!")

    # Platform-specific formatting
    if platform == "linkedin":
        if tone == "professional":
            return f"🚀 {base_message}\n\nAt our company, we believe in building lasting relationships with our clients. {objective or 'Join us in our journey of excellence.'}\n\n#Business #CustomerSuccess #Growth"
        else:
            return f"👋 {base_message}\n\n{objective or 'We value every customer and strive to provide the best experience.'}\n\n#Community #CustomerFirst"

    elif platform == "facebook":
        return f"🎉 {base_message}\n\n{objective or 'Share this post with friends who might be interested!'}\n\nWhat do you love most about our products? Let us know in the comments! 👇"

    elif platform == "instagram":
        return f"✨ {base_message}\n\n{objective or 'Tag a friend who needs to see this!'}\n\n📸 Share your experience with us!"

    elif platform == "twitter":
        return f"{base_message} {objective or 'Follow us for more updates!'}"

    return f"{base_message} {objective or ''}"


def _generate_hashtags(platform: str, segment: str) -> str:
    """Generate platform-appropriate hashtags."""

    base_tags = ["#CustomerLove", "#Community"]

    segment_tags = {
        "Champion": ["#VIP", "#Loyalty"],
        "Recent Customer": ["#Welcome", "#NewCustomer"],
        "Frequent Buyer": ["#Loyalty", "#ThankYou"],
        "Big Spender": ["#Premium", "#Exclusive"],
        "At Risk": ["#ComeBack", "#WeNeedYou"],
        "Others": ["#JoinUs", "#Discover"]
    }

    platform_tags = {
        "linkedin": ["#Business", "#Professional"],
        "facebook": ["#Social", "#Community"],
        "instagram": ["#Lifestyle", "#Visual"],
        "twitter": ["#Updates", "#News"]
    }

    all_tags = base_tags + segment_tags.get(segment, []) + platform_tags.get(platform, [])

    if platform == "twitter":
        # Twitter has character limits, so fewer hashtags
        return " ".join(all_tags[:3])
    else:
        return " ".join(all_tags)


@mcp.tool()
async def get_campaign_audience(campaign_id: str) -> str:
    """Get the target audience for a social media campaign.

    Args:
        campaign_id: The ID of the social media campaign.

    Returns:
        JSON string with campaign audience details.
    """
    with SessionLocal() as session:
        result = session.execute(
            text(
                """
                SELECT
                    smc.name as campaign_name,
                    smc.platform,
                    smc.target_segment,
                    COUNT(ca.customer_id) as audience_size,
                    smc.created_at,
                    smc.status
                FROM social_media_campaigns smc
                LEFT JOIN campaign_audience ca ON smc.id = ca.campaign_id
                WHERE smc.id = :campaign_id
                GROUP BY smc.id, smc.name, smc.platform, smc.target_segment, smc.created_at, smc.status
                """
            ),
            {"campaign_id": campaign_id},
        )

        campaign_data = result.fetchone()

        if not campaign_data:
            return "Campaign not found"

        campaign_info = {
            "campaign_name": campaign_data[0],
            "platform": campaign_data[1],
            "target_segment": campaign_data[2],
            "audience_size": campaign_data[3],
            "created_at": str(campaign_data[4]),
            "status": campaign_data[5]
        }

        return json.dumps(campaign_info, indent=2)


@mcp.tool()
async def generate_visualization(
    name: str,
    sql_query: str,
    plotly_code: str
) -> str:
    '''Generate a visualization using Python, SQL, and Plotly. If the visualization is successfully generated, it's automatically rendered for the user on the frontend.

    Args:
        name: The name of the visualization. Should be a short name with underscores and no spaces.
        sql_query: The SQL query to retrieve data for the visualization. Must be a valid postgres SQL string that can be executed directly. The query will be executed and the result will be loaded into a DataFrame named 'df'.
        plotly_code: Python code that generates a Plotly figure. The code should create a variable named 'fig' that contains the Plotly figure object.

    Returns:
        str: Success message if successful or an error message.

    ## Assumptions
    Assume the data is already loaded into a DataFrame named 'df' and the following libraries are already imported for immediate use:

    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    import plotly

    ## Example:
    User asks "Show me the top 5 customers by total spending"

    sql_query = "SELECT c.\"Customer ID\", c.\"Name\", SUM(t.\"TotalPrice\") AS total_spending FROM customers c JOIN transactions t ON c.\"Customer ID\" = t.\"Customer ID\" GROUP BY c.\"Customer ID\", c.\"Name\" ORDER BY total_spending DESC LIMIT 5;"
    plotly_code = "fig = px.bar(df, x='Name', y='total_spending', title='Top 5 Customers by Total Spending')\\nfig.update_layout(xaxis_title='Customer', yaxis_title='Total Spending ($)')"
    '''
    
    # Import our new visualization system
    from neo.visualization import VisualizationEngine, ChartDisplayManager, ChartUtils
    
    print(f"[VISUALIZATION] Starting chart generation: {name}")
    
    # Validate inputs
    sql_valid, sql_error = ChartUtils.validate_sql_query(sql_query)
    if not sql_valid:
        return f"❌ SQL Query Error: {sql_error}"
        
    plotly_valid, plotly_error = ChartUtils.validate_plotly_code(plotly_code)
    if not plotly_valid:
        return f"❌ Plotly Code Error: {plotly_error}"
    
    # Initialize the visualization engine
    viz_engine = VisualizationEngine()
    display_manager = ChartDisplayManager()
    
    # Generate the chart with multiple formats
    result = viz_engine.generate_chart(
        name=name,
        sql_query=sql_query,
        plotly_code=plotly_code,
        engine=engine,
        auto_open=True,  # Automatically open in browser
        export_formats=['html', 'json', 'png']  # Generate multiple formats
    )
    
    if result['success']:
        # Create terminal-friendly summary
        summary = display_manager.display_chart_summary(result)
        
        # Add ASCII preview if possible
        try:
            # Try to get data preview for ASCII chart
            data_preview = ChartUtils.preview_data(engine, sql_query, limit=10)
            if data_preview['success']:
                ascii_chart = display_manager.create_ascii_chart(
                    data_preview['data'], 
                    chart_type='bar'
                )
                summary += f"\n\n📊 Quick Preview:\n{ascii_chart}"
        except Exception:
            # Don't fail if ASCII preview fails
            pass
            
        return summary
    else:
        # Return error summary
        return display_manager.display_chart_summary(result)


if __name__ == "__main__":
    mcp.run(transport="stdio")
