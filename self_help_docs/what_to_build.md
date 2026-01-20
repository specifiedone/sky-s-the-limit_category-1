# Junie Pro: Autonomous Esports Coaching Agent
## Complete Build Guide for Hackathon

---

# SECTION 1: COMPLETE DOCUMENTATION

## 🎯 Project Overview

**What We're Building:**
An AI-powered autonomous coaching assistant that monitors Valorant esports matches, identifies recurring player mistakes using pattern analysis, and automatically delivers actionable coaching insights to players via Discord - all without human intervention.

**Important Clarification:**
This tool **does NOT replace human coaches**. Human coaches are irreplaceable for:
- Strategic planning and adaptation
- Team dynamics and leadership
- Mental coaching and motivation
- In-game adjustments and communication
- Player development and mentorship

**What This Tool Does:**
Handles the tedious, time-consuming work of watching every round and finding patterns, so human coaches can focus on higher-level strategic and interpersonal aspects of coaching.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    JUNIE PRO SYSTEM                         │
└─────────────────────────────────────────────────────────────┘

[Match Ends] 
    ↓
┌──────────────────────────────────────┐
│ 1. DATA COLLECTION                   │
│ GRID API fetches official match data │
│ • Player deaths                      │
│ • Kill locations                     │
│ • Round outcomes                     │
│ • Timestamps                         │
└────────┬─────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ 2. DATA STORAGE                      │
│ SQLite database saves events         │
│ • Prevents re-downloading            │
│ • Enables historical analysis        │
└────────┬─────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ 3. PATTERN ANALYSIS                  │
│ GPT-4 analyzes player behavior       │
│ • Finds recurring mistakes           │
│ • Identifies positional patterns     │
│ • Detects tactical weaknesses        │
└────────┬─────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ 4. INSIGHT GENERATION                │
│ Format AI analysis into coaching tips│
│ • Clear problem identification       │
│ • Specific rounds affected           │
│ • Actionable recommendations         │
└────────┬─────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ 5. AUTOMATED DELIVERY                │
│ Discord bot posts insights           │
│ • Sent to team channel               │
│ • Professional formatting            │
│ • Immediate after-match delivery     │
└──────────────────────────────────────┘
```

---

## 📦 Components Breakdown

### **Component 1: GRID API Data Collection**

**Purpose:** Fetch official match data from GRID's esports database

**Input Required:**
- GRID API key (from developer account)
- Match ID or team name
- Time range (e.g., "last 24 hours")

**What It Does:**
1. Connects to GRID API endpoint
2. Requests match data for specified team
3. Receives JSON response with all match events
4. Parses relevant events (deaths, kills, positions)

**Output:**
```json
{
  "match_id": "c9_vs_sen_012025",
  "date": "2025-01-20",
  "team": "Cloud9",
  "map": "Ascent",
  "players": {
    "TenZ": {
      "deaths": [
        {
          "round": 3,
          "location": "A Main",
          "time": 45,
          "killed_by": "zekken",
          "weapon": "Vandal"
        },
        {
          "round": 7,
          "location": "A Main",
          "time": 52,
          "killed_by": "TenZ",
          "weapon": "Operator"
        }
        // ... more death events
      ]
    }
  }
}
```

**Technologies:**
- Python `requests` library
- JSON parsing
- HTTP authentication

**Files Involved:**
- `modules/grid_fetcher.py`
- `config.py` (API keys)

---

### **Component 2: Data Storage**

**Purpose:** Save match data locally for fast access and historical analysis

**Input:**
- JSON match data from GRID API

**What It Does:**
1. Creates SQLite database if doesn't exist
2. Defines tables for matches and player events
3. Inserts new data (avoiding duplicates)
4. Provides query methods for analysis

**Database Schema:**

**Table: matches**
| Column | Type | Description |
|--------|------|-------------|
| match_id | TEXT PRIMARY KEY | Unique match identifier |
| date | TEXT | Match date (YYYY-MM-DD) |
| team | TEXT | Team name (e.g., "Cloud9") |
| opponent | TEXT | Opposing team |
| map | TEXT | Map name |
| score | TEXT | Final score |

**Table: player_deaths**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment ID |
| match_id | TEXT | Foreign key to matches |
| player | TEXT | Player name |
| round | INTEGER | Round number (1-24) |
| location | TEXT | Death location |
| time | INTEGER | Seconds into round |
| killed_by | TEXT | Enemy player |
| weapon | TEXT | Weapon used |

**Output:**
- SQLite database file: `data/esports_data.db`
- Fast querying capability for analysis

**Technologies:**
- SQLite3 (built into Python)
- SQL queries

**Files Involved:**
- `modules/database.py`

---

### **Component 3: AI Pattern Analysis**

**Purpose:** Use GPT-4 to identify recurring mistakes and tactical patterns

**Input:**
```python
{
  "player": "TenZ",
  "match_id": "c9_vs_sen_012025",
  "deaths": [
    {"round": 3, "location": "A Main", "time": 45},
    {"round": 7, "location": "A Main", "time": 52},
    {"round": 12, "location": "A Main", "time": 63},
    {"round": 18, "location": "A Main", "time": 38}
  ]
}
```

**What It Does:**
1. Queries database for player's deaths in match
2. Formats data into natural language prompt
3. Sends to GPT-4 via OpenAI API
4. Receives structured analysis
5. Parses response into actionable components

**GPT-4 Prompt Template:**
```
You are an expert Valorant coach analyzing match performance.

Player: {player_name}
Match: {team} vs {opponent} on {map}
Date: {date}

Death Events:
{formatted_death_list}

Task:
1. Identify any patterns (repeated mistakes in positioning, timing, or decision-making)
2. If a pattern exists, specify which rounds were affected
3. Provide ONE specific, actionable coaching tip

Format your response EXACTLY as:
PATTERN: [clear description of the pattern]
ROUNDS: [comma-separated round numbers]
TIP: [specific actionable advice]

If no clear pattern exists (fewer than 3 similar events), respond with:
PATTERN: No significant pattern detected
```

**Output:**
```
PATTERN: Player repeatedly died in A Main during the first minute of rounds, suggesting aggressive early positioning without utility support or team coordination.
ROUNDS: 3, 7, 12, 18
TIP: Before entering A Main, coordinate with your sentinel to hold long angles or request initiator recon abilities (drone/dart) to clear common positions. Consider delaying A Main entry by 10-15 seconds to allow enemy positioning to commit.
```

**Technologies:**
- OpenAI API (GPT-4)
- Prompt engineering
- Response parsing

**Files Involved:**
- `modules/analyzer.py`
- `config.py` (OpenAI API key)

**Cost:** ~$0.01 per match analyzed

---

### **Component 4: Insight Formatter**

**Purpose:** Transform AI analysis into professional, readable coaching messages

**Input:**
```python
{
  "player": "TenZ",
  "match": "Cloud9 vs Sentinels",
  "map": "Ascent",
  "date": "2025-01-20",
  "pattern": "Player repeatedly died in A Main during first minute...",
  "rounds": [3, 7, 12, 18],
  "tip": "Before entering A Main, coordinate with sentinel..."
}
```

**What It Does:**
1. Takes parsed GPT-4 response
2. Adds formatting (bold, emojis, sections)
3. Calculates statistics (frequency, percentage)
4. Structures for Discord display

**Output:**
```markdown
🎯 **Post-Match Insights: Cloud9 vs Sentinels**
📅 Match Date: January 20, 2025
🗺️ Map: Ascent

**Player: TenZ**
📍 **Pattern Detected:** Repeated early deaths in A Main
📊 **Frequency:** 4 occurrences in 24 rounds (16.7%)
🎮 **Rounds Affected:** 3, 7, 12, 18

💡 **Coaching Insight:**
You're consistently dying in A Main during the first minute of rounds. This suggests aggressive positioning without proper utility support or team coordination.

✅ **Actionable Tip:**
Before entering A Main, coordinate with your sentinel to hold long angles or request initiator recon abilities to clear common positions. Consider delaying entry by 10-15 seconds.

---
🤖 *Generated by Junie Pro | Powered by GRID + JetBrains AI*
```

**Technologies:**
- Discord Markdown formatting
- String templating
- Python string formatting

**Files Involved:**
- `modules/formatter.py`

---

### **Component 5: Discord Delivery**

**Purpose:** Automatically post coaching insights to team's Discord channel

**Input:**
- Formatted message (from Component 4)
- Discord webhook URL or bot token
- Target channel ID

**What It Does:**
1. Establishes connection to Discord via webhook
2. Sends formatted message as embedded content
3. Handles errors (network issues, rate limits)
4. Logs successful delivery

**Output:**
Message appears in Discord channel automatically:

```
[Junie Pro Bot Icon] Junie Pro  BOT  Today at 3:47 PM

🎯 **Post-Match Insights: Cloud9 vs Sentinels**
📅 Match Date: January 20, 2025
🗺️ Map: Ascent

**Player: TenZ**
📍 **Pattern Detected:** Repeated early deaths in A Main
📊 **Frequency:** 4 occurrences in 24 rounds (16.7%)
🎮 **Rounds Affected:** 3, 7, 12, 18

💡 **Coaching Insight:**
You're consistently dying in A Main during the first minute of rounds.

✅ **Actionable Tip:**
Before entering A Main, coordinate with your sentinel to hold long angles or request initiator recon abilities to clear common positions.

---
🤖 *Generated by Junie Pro | Powered by GRID + JetBrains AI*
```

**Technologies:**
- Discord webhooks (simple) OR Discord.py bot (advanced)
- Async HTTP requests
- Error handling

**Files Involved:**
- `modules/discord_bot.py`

---

### **Component 6: Simple Dashboard (Optional - Low Priority)**

**Purpose:** Web interface showing historical patterns and statistics

**Input:**
- Data from SQLite database
- Team selection
- Date range filter

**What It Shows:**
- Recent matches analyzed
- Common mistake patterns by player
- Trend charts (deaths by location over time)
- System status (last run, matches processed)

**Output:**
Simple HTML page with:
- Table of analyzed matches
- Bar charts of common death locations
- List of insights sent to Discord

**Technologies:**
- Flask (simple Python web framework)
- Chart.js or matplotlib (for graphs)
- HTML/CSS (basic styling)

**Files Involved:**
- `dashboard/app.py`
- `dashboard/templates/index.html`

**Note:** This is LOWEST priority. Only build if you have extra time. Discord messages are the primary delivery method.

---

## 📂 Project File Structure

```
junie-pro/
│
├── main.py                      # Main orchestration script
├── config.py                    # API keys and configuration
├── requirements.txt             # Python dependencies
├── setup.sh                     # One-command setup script
├── README.md                    # Project documentation
│
├── modules/
│   ├── __init__.py
│   ├── grid_fetcher.py          # Component 1: GRID API integration
│   ├── database.py              # Component 2: SQLite operations
│   ├── analyzer.py              # Component 3: GPT-4 analysis
│   ├── formatter.py             # Component 4: Message formatting
│   └── discord_bot.py           # Component 5: Discord delivery
│
├── data/
│   ├── esports_data.db          # SQLite database (auto-created)
│   └── .gitkeep
│
├── logs/
│   ├── system.log               # Execution logs
│   └── .gitkeep
│
├── dashboard/                   # Optional - build last
│   ├── app.py
│   └── templates/
│       └── index.html
│
└── tests/
    ├── test_grid.py             # Test GRID API connection
    ├── test_analyzer.py         # Test GPT-4 integration
    └── test_discord.py          # Test Discord delivery
```

---

## 🛠️ Technology Stack

### **Required:**
- **Python 3.11+** - Main programming language
- **requests** - HTTP library for API calls
- **sqlite3** - Built-in database (no install needed)
- **openai** - OpenAI API client for GPT-4
- **discord.py** or **webhooks** - Discord integration
- **aiohttp** - Async HTTP for Discord

### **Optional:**
- **Flask** - Web framework for dashboard
- **matplotlib** - Charting library
- **pytest** - Testing framework

### **Development Tools:**
- **JetBrains PyCharm** - IDE (required for hackathon)
- **Junie AI** - JetBrains AI coding assistant
- **Git** - Version control

---

## 💰 Cost Breakdown

| Service | Cost | Notes |
|---------|------|-------|
| GRID API | Free | With Open Access approval |
| OpenAI GPT-4 | ~$0.01/match | ~$5/month for 500 matches |
| Discord | Free | Unlimited webhooks |
| Hosting (optional) | Free | Railway/Render free tier |
| **Total** | **~$5/month** | Extremely affordable |

---

## 🎓 Learning Resources

### **If You're New to Python:**
- Codecademy Python Course (25 hours, free)
- Python official tutorial (docs.python.org)
- "Automate the Boring Stuff" book (free online)

### **If You're New to APIs:**
- "What is an API?" - FreeCodeCamp (YouTube)
- Postman API tutorial
- requests library documentation

### **If You're New to Discord Bots:**
- Discord.py documentation
- "Discord Bot Tutorial" - Tech With Tim (YouTube)

### **If You're New to SQL:**
- SQLite tutorial - sqlitetutorial.net
- W3Schools SQL course

**Estimated Learning Time if Starting from Scratch:**
- 40 hours for Python basics
- 10 hours for API fundamentals
- 5 hours for Discord bots
- 5 hours for SQL basics

**Recommended:** Partner with someone who knows Python if you're a complete beginner.

---

## 🚨 Common Mistakes to Avoid

### **1. Over-Engineering**
❌ **Don't:** Try to add video clips, voice narration, real-time streaming
✅ **Do:** Focus on the core loop working perfectly

### **2. Perfect AI Output**
❌ **Don't:** Spend days tweaking GPT-4 prompts
✅ **Do:** Get it "good enough" in 1 day, iterate if time allows

### **3. Fancy UI**
❌ **Don't:** Build a complex web dashboard
✅ **Do:** Discord messages ARE your UI

### **4. Complex Database**
❌ **Don't:** Set up PostgreSQL with migrations
✅ **Do:** Use SQLite with 2-3 simple tables

### **5. Testing at the End**
❌ **Don't:** Code for 10 days then test
✅ **Do:** Test each component immediately

---

## 🎯 Success Metrics

### **Technical Success:**
- System runs automatically every hour
- Successfully analyzes 10+ matches
- Discord messages delivered reliably
- AI insights are coherent and actionable
- Zero crashes over 24-hour period

### **Hackathon Success:**
- Demo video under 3 minutes
- Live demo works without errors
- Clear JetBrains/Junie integration shown
- Judges understand the value proposition
- Code is on GitHub with good README

### **Real-World Success:**
- A coach says "I would actually use this"
- Insights identify mistakes human coaches missed
- Players find recommendations helpful
- System scales to multiple teams
- Deployment time under 5 minutes

---

---

# SECTION 2: TIME-BOUND BUILD PLAN

## 📅 13-Day Development Sprint

---

## **DAY 1-2: Data Collection Foundation**

### **Goal:** Get GRID API working and fetching match data

### **What to Build:**
File: `modules/grid_fetcher.py`

**Function 1: Connect to GRID API**
```python
def connect_to_grid(api_key):
    """Test GRID API connection"""
    # Input: GRID API key string
    # Output: True if connected, False otherwise
```

**Function 2: Fetch Latest Matches**
```python
def fetch_team_matches(team_name, hours=24):
    """Get recent matches for a team"""
    # Input: Team name (e.g., "Cloud9"), time range
    # Output: List of match IDs
```

**Function 3: Get Match Details**
```python
def get_match_data(match_id):
    """Fetch all events for a specific match"""
    # Input: Match ID from GRID
    # Output: JSON with player deaths, kills, rounds
```

### **Input Required:**
- GRID API key (apply on day 1, hopefully approved by day 2)
- Team name: "Cloud9"
- Time range: Last 24 hours

### **Expected Output:**
```json
{
  "match_id": "cloud9-sentinels-012025",
  "date": "2025-01-20",
  "teams": ["Cloud9", "Sentinels"],
  "players": {
    "TenZ": {
      "agent": "Jett",
      "deaths": [
        {"round": 3, "location": "A Main", "time": 45},
        {"round": 7, "location": "A Main", "time": 52}
      ]
    }
  }
}
```

### **Success Criteria:**
- ✅ Can successfully call GRID API
- ✅ Receive match data in JSON format
- ✅ Parse JSON and extract player death events
- ✅ Script runs without errors
- ✅ Can print match data to console

### **Testing:**
```bash
python -c "from modules.grid_fetcher import *; print(fetch_team_matches('Cloud9'))"
# Should print list of recent match IDs
```

---

## **DAY 3-4: Data Storage Setup**

### **Goal:** Save match data to SQLite database

### **What to Build:**
File: `modules/database.py`

**Function 1: Initialize Database**
```python
def init_database():
    """Create tables if they don't exist"""
    # Input: None
    # Output: SQLite database file created
```

**Function 2: Save Match**
```python
def save_match(match_data):
    """Store match metadata"""
    # Input: Match JSON from GRID API
    # Output: Match saved to 'matches' table
```

**Function 3: Save Player Events**
```python
def save_player_deaths(match_id, player, deaths):
    """Store player death events"""
    # Input: Match ID, player name, list of death events
    # Output: Events saved to 'player_deaths' table
```

**Function 4: Query Player Stats**
```python
def get_player_deaths(match_id, player):
    """Retrieve deaths for analysis"""
    # Input: Match ID, player name
    # Output: List of death events with location, time, round
```

### **Input:**
Match data from Day 1-2 (GRID API JSON)

### **Process:**
1. Create database schema (tables: matches, player_deaths)
2. Insert match metadata
3. Insert each death event
4. Query and verify data is saved correctly

### **Expected Output:**
SQLite database: `data/esports_data.db`

**Query result example:**
```sql
SELECT * FROM player_deaths WHERE player = 'TenZ';

| match_id         | player | round | location | time |
|------------------|--------|-------|----------|------|
| c9_sen_012025    | TenZ   | 3     | A Main   | 45   |
| c9_sen_012025    | TenZ   | 7     | A Main   | 52   |
| c9_sen_012025    | TenZ   | 12    | A Main   | 63   |
```

### **Success Criteria:**
- ✅ Database file created automatically on first run
- ✅ Match data saves without errors
- ✅ Can query and retrieve saved data
- ✅ No duplicate entries for same match
- ✅ Data persists after script ends

### **Testing:**
```bash
python -c "from modules.database import *; init_database(); print('DB created')"
# Should create data/esports_data.db file
```

---

## **DAY 5-6: AI Pattern Analysis**

### **Goal:** Integrate GPT-4 to analyze player patterns

### **What to Build:**
File: `modules/analyzer.py`

**Function 1: Format Data for GPT-4**
```python
def format_deaths_for_analysis(deaths):
    """Convert death list to natural language"""
    # Input: List of death dicts
    # Output: Formatted string for GPT-4 prompt
```

**Function 2: Call GPT-4**
```python
def analyze_player_patterns(player, match_id):
    """Send data to GPT-4 for analysis"""
    # Input: Player name, match ID
    # Output: GPT-4 analysis text
```

**Function 3: Parse GPT-4 Response**
```python
def parse_coaching_insight(gpt_response):
    """Extract pattern, rounds, tip from response"""
    # Input: Raw GPT-4 text response
    # Output: Structured dict with pattern, rounds, tip
```

### **Input:**
```python
deaths = [
    {"round": 3, "location": "A Main", "time": 45},
    {"round": 7, "location": "A Main", "time": 52},
    {"round": 12, "location": "A Main", "time": 63},
    {"round": 18, "location": "A Main", "time": 38}
]
```

### **Process:**
1. Query database for player deaths
2. Format into prompt:
```
You are an expert Valorant coach.

Player: TenZ
Deaths:
- Round 3: Died at A Main at 0:45
- Round 7: Died at A Main at 0:52
- Round 12: Died at A Main at 1:03
- Round 18: Died at A Main at 0:38

Find patterns and provide coaching insight.
Format as:
PATTERN: [description]
ROUNDS: [list]
TIP: [advice]
```
3. Send to OpenAI API
4. Receive and parse response

### **Expected Output:**
```python
{
    "pattern": "Repeated early deaths in A Main suggesting aggressive positioning without utility",
    "rounds": [3, 7, 12, 18],
    "tip": "Coordinate with sentinel before entering A Main or request initiator recon abilities"
}
```

### **Success Criteria:**
- ✅ Successfully connect to OpenAI API
- ✅ GPT-4 returns coherent analysis
- ✅ Pattern detection works for obvious patterns
- ✅ Response parsing extracts all components
- ✅ Cost per analysis is under $0.02

### **Testing:**
```bash
python -c "from modules.analyzer import *; result = analyze_player_patterns('TenZ', 'c9_sen_012025'); print(result)"
# Should print structured analysis
```

---

## **DAY 7: Discord Integration**

### **Goal:** Automatically post insights to Discord channel

### **What to Build:**
File: `modules/discord_bot.py`

**Function 1: Create Webhook Connection**
```python
def setup_discord_webhook(webhook_url):
    """Initialize Discord webhook"""
    # Input: Discord webhook URL
    # Output: Webhook object ready to send
```

**Function 2: Send Message**
```python
async def send_coaching_insight(message):
    """Post formatted message to Discord"""
    # Input: Formatted coaching message string
    # Output: Message posted to Discord channel
```

**Function 3: Handle Errors**
```python
def retry_on_failure(func, max_retries=3):
    """Retry Discord posts if they fail"""
    # Input: Function to retry
    # Output: Success/failure status
```

### **Input:**
Formatted message from formatter (markdown text)

### **Process:**
1. Set up Discord webhook in server settings
2. Copy webhook URL
3. Send POST request with message content
4. Verify message appears in Discord

### **Expected Output:**
Message appears in Discord channel within 2 seconds:

```
[Junie Pro Bot] Today at 3:47 PM

🎯 **Post-Match Insights: Cloud9 vs Sentinels**

**Player: TenZ**
📍 Pattern: Repeated deaths in A Main
🎮 Rounds: 3, 7, 12, 18

💡 **Tip:** Coordinate with sentinel before entering
```

### **Success Criteria:**
- ✅ Message posts successfully to Discord
- ✅ Formatting appears correctly (bold, emojis)
- ✅ Error handling works (retries on failure)
- ✅ Delivery time under 3 seconds
- ✅ No rate limit issues

### **Testing:**
```bash
python -c "from modules.discord_bot import *; import asyncio; asyncio.run(send_coaching_insight('Test message'))"
# Should see "Test message" in Discord
```

---

## **DAY 8-9: End-to-End Integration**

### **Goal:** Connect all components into one automated pipeline

### **What to Build:**
File: `main.py`

**Main Orchestration Script:**
```python
def run_junie_pro():
    """Execute full pipeline"""
    # 1. Fetch latest matches
    # 2. Save to database
    # 3. Analyze patterns
    # 4. Format insights
    # 5. Send to Discord
```

### **Input:**
- GRID API key (from config)
- OpenAI API key (from config)
- Discord webhook URL (from config)
- Team name: "Cloud9"

### **Process Flow:**
```
START
  ↓
Fetch Cloud9 matches from last 24h (grid_fetcher.py)
  ↓
For each match:
  ↓
  Save match data (database.py)
  ↓
  For each player:
    ↓
    Analyze patterns (analyzer.py)
    ↓
    Format insight (formatter.py)
    ↓
    Send to Discord (discord_bot.py)
  ↓
Log completion
  ↓
END
```

### **Expected Output:**
```bash
$ python main.py

🤖 Junie Pro starting...
📡 Fetching Cloud9 matches from last 24 hours...
✅ Found 2 new matches

📊 Processing match: Cloud9 vs Sentinels (Ascent)
💾 Match data saved
🧠 Analyzing TenZ... Pattern found!
📨 Sent insight to Discord
🧠 Analyzing Zellsis... No pattern
🧠 Analyzing OXY... Pattern found!
📨 Sent insight to Discord

📊 Processing match: Cloud9 vs 100T (Haven)
💾 Match data saved
🧠 Analyzing TenZ... No pattern
🧠 Analyzing Zellsis... Pattern found!
📨 Sent insight to Discord

✅ Junie Pro finished! 3 insights generated.
```

### **Success Criteria:**
- ✅ Entire pipeline runs without errors
- ✅ Processes multiple matches automatically
- ✅ Skips players with no patterns
- ✅ Discord receives all generated insights
- ✅ Completion time under 3 minutes per match

### **Testing:**
Run full pipeline on one recent Cloud9 match and verify Discord message

---

## **DAY 10: Automation & Scheduling**

### **Goal:** Make system run automatically without manual execution

### **What to Build:**
1. **Cron job / Task Scheduler setup**
2. **Error logging**
3. **Deployment script**

### **File: `setup.sh`**
```bash
#!/bin/bash
# One-command deployment script

echo "🚀 Junie Pro Setup"
echo "===================="

# Install dependencies
pip install -r requirements.txt

# Get API keys
echo "Enter your GRID API key:"
read GRID_KEY
echo "Enter your OpenAI API key:"
read OPENAI_KEY
echo "Enter your Discord webhook URL:"
read DISCORD_URL

# Save to config
cat > config.py <<EOF
GRID_API_KEY = "$GRID_KEY"
OPENAI_API_KEY = "$OPENAI_KEY"
DISCORD_WEBHOOK_URL = "$DISCORD_URL"
TEAMS_TO_WATCH = ["Cloud9"]
CHECK_INTERVAL_HOURS = 1
EOF

# Initialize database
python -c "from modules.database import init_database; init_database()"

# Add cron job (runs every hour)
(crontab -l; echo "0 * * * * cd $(pwd) && python main.py >> logs/system.log 2>&1") | crontab -

echo "✅ Setup complete! Junie Pro will run every hour."
echo "Test now: python main.py"
```

### **Input:**
- User provides API keys via prompts
- System is configured automatically

### **Process:**
1. User runs `bash setup.sh`
2. Script installs dependencies
3. Prompts for API keys
4. Creates config file
5. Sets up automated scheduling
6. Initializes database

### **Expected Output:**
```bash
$ bash setup.sh

🚀 Junie Pro Setup
====================
Installing dependencies... ✅
Enter your GRID API key: ***********
Enter your OpenAI API key: ***********
Enter your Discord webhook URL: ***********
Saving configuration... ✅
Initializing database... ✅
Setting up cron job... ✅

✅ Setup complete! Junie Pro will run every hour.
Test now: python main.py
```

### **Success Criteria:**
- ✅ Script runs without errors
- ✅ Config file created correctly
- ✅ Cron job added successfully
- ✅ System runs automatically on schedule
- ✅ Logs are generated in `logs/system.log`

### **Automation Test:**
Wait 1 hour and check Discord for new messages (proves it ran automatically)

---

## **DAY 11: Testing & Bug Fixes**

### **Goal:** Test with real matches and fix any issues

### **What to Do:**

**Test 1: Fresh Cloud9 Match**
- Find a match that happened in the last 24 hours
- Run system manually: `python main.py`
- Verify Discord receives insights
- Check if patterns detected are accurate

**Test 2: Multiple Matches**
- Run on Cloud9's last 5 matches
- Ensure database doesn't create duplicates
- Verify all matches processed

**Test 3: Edge Cases**
- Match with no clear patterns (should skip gracefully)
- Player with perfect performance (no deaths in same location)
- Network failure (retry logic works)

**Test 4: GPT-4 Output Quality**
- Read 10+ generated insights
- Are they actionable and specific?
- Do they make tactical sense?
- Improve prompts if needed

### **Input:**
Real Cloud9 match data from GRID

### **Expected Output:**
System handles all cases gracefully:
- Successful matches → Insights posted
- No patterns → Skips player, no error
- Network issues → Retries, then logs error
- Invalid data → Logs warning, continues

### **Success Criteria:**
- ✅ Zero crashes over 24-hour test period
- ✅ All insights are coherent and helpful
- ✅ Error handling works for all edge cases
- ✅ Performance is acceptable (< 5 min per match)
- ✅ Database size stays reasonable (< 100MB)

---

## **DAY 12: JetBrains Integration & Demo Prep**

### **Goal:** Show you used JetBrains tools and prepare demo video

### **What to Build:**

**1. Record Junie Usage**
- Open JetBrains PyCharm
- Enable Junie AI assistant
- Ask Junie to help with a feature
- Screen record this interaction

Example prompts to Junie:
- "Help me write a function to parse GRID API responses"
- "Generate error handling for Discord webhook"
- "Write unit tests for the analyzer module"

**2. Add Junie Branding**
Update Discord message footer:
```python
footer_text = """
---
🤖 Generated by **Junie Pro**
Built with JetBrains AI | Powered by GRID Esports Data
"""
```

**3. Create Demo Content**

File: `DEMO_SCRIPT.md`
```markdown
# Demo Video Script (3 minutes)

[0:00-0:20] Introduction & Problem
[0:20-0:40] Show GRID API data fetching
[0:40-1:00] Show GPT-4 analysis
[1:00-1:30] Show Discord delivery
[1:30-2:00] Show full pipeline running
[2:00-2:30] Show JetBrains/Junie usage
[2:30-3:00] Deployment demo + closing
```

### **Input:**
- Screen recording software (OBS, QuickTime, etc.)
- Recent Cloud9 match for demo
- JetBrains IDE with Junie enabled

### **Expected Output:**
- 30-second clip of Junie helping you code
- Professional demo script
- System ready to demonstrate

### **Success Criteria:**
- ✅ Clear proof you used JetBrains tools
- ✅ Demo script is under 3 minutes
- ✅ All components work for demo
- ✅ Backup plan if live demo fails (pre-recorded)

---

## **DAY 13: Demo Video Recording & Submission**

### **Goal:** Record killer demo video and submit project

### **What to Do:**

**Morning: Record Demo Video**

**Scene 1 (0:00-0:20): The Hook**
- Show your face
- State the problem: "Coaches can't watch everything"
- Personal touch: "I've followed esports for X years..."

**Scene 2 (0:20-0:40): The Problem**
- Screen: Show Cloud9's match schedule
- Explain: "60+ matches per year = 10,000+ rounds"
- Transition: "What if AI could help?"

**Scene 3 (0:40-1:30): The Demo**
- Screen recording of terminal: `python main.py`
- Show each step:
  - GRID data fetching
  - GPT-4 analyzing
  - Discord message appearing
- Point out timestamp (shows it ran automatically)

**Scene 4 (1:30-2:00): The Junie Connection**
- Screen recording: Show Junie helping you code
- Explain: "Built using JetBrains' AI assistant"
- Callback: "Junie helped me build an AI coaching agent"

**Scene 5 (2:00-2:30): Deployment**
- Screen recording: Run `bash setup.sh`
- Show how easy it is: "Any team can deploy in 30 seconds"
- Emphasize: "This augments coaches, doesn't replace them"

**Scene 6 (2:30-3:00): Closing**
- Your face: "This is Junie Pro"
- Call to action: "Built in 13 days for JetBrains hackathon"
- Show GitHub link
- Thank judges

**Afternoon: Polish & Submit**
1. Edit video (add subtitles for accessibility)
2. Export as MP4 (under 100MB)
3. Prepare submission materials:
   - GitHub repo link
   - Demo video link (YouTube/Vimeo)
   - Project description (300 words)
   - Screenshots

**Submission Checklist:**
- ✅ GitHub repo is public
- ✅ README.md is comprehensive
- ✅ requirements.txt is up to date
- ✅ setup.sh script works
- ✅ Demo video uploaded
- ✅ All links tested
- ✅ Submission form completed
- ✅ Submitted before deadline

### **Success Criteria:**
- ✅ Video is 2:45 - 3:00 minutes
- ✅ Audio is clear
- ✅ Demo shows working system
- ✅ JetBrains integration highlighted
- ✅ Submission confirmed

---

## 📊 Daily Success Checklist

### **Day 1-2:**
- [ ] GRID API key obtained
- [ ] Can fetch match data
- [ ] JSON parsing works
- [ ] Data prints to console

### **Day 3-4:**
- [ ] SQLite database created
- [ ] Match data saves successfully
- [ ] Can query saved data
- [ ] No duplicate entries

### **Day 5-6:**
- [ ] OpenAI API connected
- [ ] GPT-4 returns analysis
- [ ] Patterns are coherent
- [ ] Response parsing works

### **Day 7:**
- [ ] Discord webhook connected
- [ ] Messages post successfully
- [ ] Formatting looks good
- [ ] Error handling works

### **Day 8-9:**
- [ ] Full pipeline runs end-to-end
- [ ] Multiple matches processed
- [ ] Discord receives all insights
- [ ] No crashes

### **Day 10:**
- [ ] Automated scheduling set up
- [ ] System runs without manual trigger
- [ ] Logs are generated
- [ ] Setup script works

### **Day 11:**
- [ ] Tested on 5+ real matches
- [ ] All edge cases handled
- [ ] Bug fixes completed
- [ ] Performance acceptable

### **Day 12:**
- [ ] Junie usage recorded
- [ ] Demo script written
- [ ] System ready to demonstrate
- [ ] Backup plan prepared

### **Day 13:**
- [ ] Demo video recorded
- [ ] Video edited and uploaded
- [ ] GitHub repo polished
- [ ] Submission completed

---

## 🎯 Overall Success Indicators

### **Technical Success:**
You know you're succeeding if:
- System runs for 24 hours without crashing
- Analyzes 10+ matches successfully
- Discord receives all messages
- AI insights are helpful and specific
- Setup takes under 5 minutes

### **Demo Success:**
You know your demo is strong if:
- Video is under 3 minutes
- Live demo works first try
- Judges understand the value
- JetBrains integration is clear
- Someone says "I would use this"

### **Winning Indicators:**
You're in contention if:
- Your positioning is unique (autonomous agent vs dashboard)
- Demo shows real working system
- Junie integration is prominent
- Problem-solution narrative is clear
- Deployment is genuinely simple

---

## 🏆 Final Reality Check

**If by Day 11 you have:**
- ✅ GRID → Database → GPT-4 → Discord working end-to-end
- ✅ System that runs automatically
- ✅ Generated real insights from real matches
- ✅ Proof you used JetBrains tools

**Then you're in the top 10% of submissions.**

The rest is polish. Don't let perfect be the enemy of done.

**Now go build it. 🚀**
