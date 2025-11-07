# 🤖 Neo - AI Marketing Agent

Neo is an intelligent Marketing AI agent that analyzes customer behavior and creates personalized marketing campaigns using AI, LangGraph, and real customer data.

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Node.js

### Setup

1. **Install dependencies**

```bash
git clone <repository-url>
cd marketing-ai-agent
uv sync
```

2. **Configure environment**
   Create `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URI=your_postgresql_connection_string_here
```

3. **Setup database**

```bash
cd db
uv run python generate_data_tables.py
```

4. **Start Neo**

**Text Interface:**

```bash
cd frontend
uv run python chat_local.py
```

**Voice Interface:**

```bash
cd frontend
uv run python voice_chat.py
```

## 🎯 What Neo Can Do

- **Customer Analysis**: Analyze spending patterns and behavior
- **RFM Segmentation**: Categorize customers by Recency, Frequency, Monetary value
- **Campaign Creation**: Build targeted marketing campaigns
- **Email Automation**: Send personalized emails to customer segments
- **Social Media Campaigns**: Create platform-specific campaigns for Facebook, LinkedIn, Instagram, Twitter
- **Content Generation**: Generate platform-appropriate posts with segment-specific messaging
- **Voice Interaction**: Talk to Neo using speech-to-text and text-to-speech capabilities
- **Data Visualization**: Generate interactive charts and graphs that automatically open in your browser

## 💬 Example Commands

```
"Analyze customer purchase patterns from the last 3 months"
"Find customers who spent more than $500 but haven't bought anything recently"
"Create a referral campaign targeting our most frequent buyers"
"Show me which products are most popular among champion customers"
"Send personalized discount emails to at-risk customers"
"What's the average order value for each customer segment?"
"Create a loyalty program announcement for big spenders"
"Find customers who only bought once and send them a welcome-back offer"
"Create a Facebook campaign targeting Champion customers"
"Show me the top 10 customers by spending in a bar chart"
"Create a pie chart of customer segments"
"Display monthly sales trends as a line chart"
"Generate a scatter plot of customer age vs spending"
```

## 🏗️ Architecture

```
Text/Voice Interface ◄──► Neo Agent (LangGraph) ◄──► Database (PostgreSQL)
                                    │
                                    ▼
                            MCP Marketing Server
                                    │
                                    ├──► OpenAI (STT/TTS/LLM)
                                    └──► Visualization Engine (Plotly/Charts)
```

## 🛠️ Tech Stack

- **LangGraph**: AI agent framework
- **MCP**: Model Context Protocol for tool integration
- **PostgreSQL**: Customer data storage
- **OpenAI**: Language model + Speech-to-Text (Whisper) + Text-to-Speech
- **Python**: Backend implementation
- **Audio Libraries**: sounddevice, soundfile, numpy, scipy
- **Plotly**: Interactive data visualization and charting
- **Pandas**: Data processing for charts and analytics

## 📊 Database Tables

### Core Tables

- `customers` - Customer information
- `transactions` - Purchase history
- `items` - Product catalog
- `rfm` - Customer segments

### Marketing Tables

- `marketing_campaigns` - Email campaign tracking
- `campaign_emails` - Email delivery logs

### Social Media Tables

- `social_media_campaigns` - Social media marketing campaigns
- `social_media_posts` - Generated social media content
- `campaign_audience` - Campaign target audience mapping

## 📱 Social Media Campaign Features

### Supported Platforms

- **Facebook**: Community-focused content with engagement features
- **LinkedIn**: Professional, business-oriented messaging
- **Instagram**: Visual, lifestyle-focused content with hashtags
- **Twitter**: Short, news-style updates with trending hashtags

### Customer Segments

- **Champion**: Most valued customers (high RFM scores)
- **Recent Customer**: New customers who recently made their first purchase
- **Frequent Buyer**: Customers who purchase regularly
- **Big Spender**: Customers who spend large amounts
- **At Risk**: Customers who haven't purchased recently
- **Others**: General customer base

### Post Tones

- Professional, Casual, Friendly, Promotional, Educational

## 🎤 Voice Features

### Voice Interface

- **Speech-to-Text**: Uses OpenAI `whisper-1` model for accurate transcription
- **Text-to-Speech**: Uses OpenAI `gpt-4o-mini-tts` with `alloy` voice
- **Simple Controls**: Press Enter to record, say "goodbye" to exit
- **Smart Filtering**: Only speaks agent responses, filters out technical tool calls
- **Voice-Optimized**: Conversational prompts designed for natural speech

### Voice Commands

Say the same commands as text interface:

- "Show me our champion customers"
- "Create a loyalty campaign for big spenders"
- "What's our revenue from recent customers?"
- "goodbye" (to exit)

## 📊 Data Visualization Features

### Interactive Charts

- **Automatic Browser Display**: Charts open automatically in your default browser
- **Multiple Export Formats**: HTML (interactive), PNG, SVG, JSON
- **Terminal Previews**: ASCII charts display immediately in terminal
- **Chart Management**: Organized file storage with timestamped names

### Supported Chart Types

- **📊 Bar Charts**: Compare categories and values
- **📈 Line Charts**: Show trends over time
- **🥧 Pie Charts**: Display proportions and percentages
- **⚡ Scatter Plots**: Explore relationships between variables
- **📋 Histograms**: Analyze data distributions
- **📊 Custom Charts**: Any Plotly visualization type

### Chart Viewing Tools

```bash
# List all available charts
python chart_viewer.py --list

# View a specific chart
python chart_viewer.py --view customer_analysis

# Quick terminal preview
python chart_viewer.py --preview sales_data

# Interactive chart browser
python chart_viewer.py
```

### File Organization

All charts are automatically saved to `output/charts/` with:

- Interactive HTML files for browser viewing
- PNG/SVG exports for presentations
- JSON data for programmatic access
- Timestamped filenames to prevent conflicts

## 📁 Project Structure

```
├── frontend/
│   ├── chat_local.py      # Text interface
│   └── voice_chat.py      # Voice interface
├── src/neo/
│   ├── graph.py           # LangGraph agent
│   ├── prompts.py         # System prompts (text + voice)
│   ├── voice/
│   │   ├── __init__.py
│   │   └── voice_utils.py # Audio processing
│   └── visualization/     # Data visualization system
│       ├── __init__.py
│       ├── core.py        # Visualization engine
│       ├── display.py     # Chart display management
│       └── utils.py       # Visualization utilities
├── output/charts/         # Generated charts and visualizations
├── db/                    # Database setup
├── chart_viewer.py        # Interactive chart management tool
├── view_charts.py         # Legacy chart viewer (redirects to new system)
└── VISUALIZATION_GUIDE.md # Comprehensive visualization documentation
```
