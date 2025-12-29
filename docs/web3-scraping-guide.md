# Web3 Startup Analysis Project - Research & Implementation Guide

## Project Overview
Personal research project for analyzing trending startups in web3 using data from Web3 Alerts website.

---

## Initial Analysis & Framework Discussion

### Project Goal
Build a personal project for research purposes to analyze trending startups in web3, with startup information obtained from the Web3 Alerts website.

### Website Structure (Based on Screenshot Analysis)
The Web3 Alerts website displays:
- **Project metadata**: Name, description, logo
- **Metrics**: Star rating (e.g., 112), upvote count (e.g., 88)
- **Social metrics**: Twitter followers (e.g., 34,201)
- **Temporal data**: "Found X days ago"
- **Categories/Tags**: Gaming, social capital, etc.
- **Notable followers**: @DeFi_Dad, @SpiderCrypto0x, etc.
- **Platform indicators**: @base chain references
- **Filtering options**: Trending Past (3 Days dropdown), Sort By (Quality Score)

### Initial Data Collection Architecture

#### Core Components to Extract:
- Project metadata (name, description, logo URL)
- Metrics (star rating, upvote count, Twitter followers)
- Temporal data (discovery date, trending period)
- Social proof (notable followers)
- Categories and tags
- Platform/chain indicators

#### Technical Stack Options Considered:

**Option A: Browser Automation**
- Playwright or Puppeteer with cookie injection
- Handles JavaScript-rendered content
- Can navigate pagination and load more buttons
- Simulate user interactions if needed

**Option B: Direct API Approach**
- Inspect network tab to find API endpoints
- Use cookies for authenticated requests
- More efficient but requires reverse engineering

### Data Pipeline Framework
```
[Web Scraper] → [Data Validator] → [Storage] → [Analysis Engine] → [Dashboard]
```

### Proposed Data Storage Schema
```json
{
  "project_id": "unique_identifier",
  "name": "YZY MONEY",
  "metrics": {
    "stars": 112,
    "upvotes": 88,
    "twitter_followers": 34201,
    "quality_score": "calculated_value"
  },
  "temporal": {
    "discovered_date": "2024-01-20",
    "trending_duration": "3 days",
    "last_updated": "timestamp"
  },
  "social_signals": {
    "notable_followers": ["@DeFi_Dad", "@SpiderCrypto0x"],
    "follower_quality": "score"
  }
}
```

### Analysis Features to Build
- **Trend Detection**: Track projects gaining momentum over time
- **Quality Scoring**: Combine metrics for comprehensive ranking
- **Category Analysis**: Identify hot sectors (Gaming, DeFi, Social)
- **Influencer Mapping**: Which accounts consistently follow winners
- **Early Signal Detection**: Projects with high quality scores but low discovery time

---

## Technical Implementation Discussion

### BeautifulSoup vs Playwright Analysis

#### Quick Test to Determine Requirements
1. Right-click → View Page Source on the website
2. Search for project names in the source
3. If data isn't visible in source, it's JavaScript-rendered

#### Why Playwright Would Be Necessary
**Signs of a Dynamic Site:**
- Interactive filters (Trending Past dropdown, Sort By dropdown)
- Real-time metrics (Twitter followers: 34,201)
- Likely pagination or infinite scroll
- Modern web3 site = probably React/Vue/Next.js

#### Hybrid Approach (Best of Both Worlds)
```python
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_with_hybrid():
    with sync_playwright() as p:
        # Use Playwright to handle JS and authentication
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Load cookies, navigate, wait for content
        page.goto(url)
        page.wait_for_load_state('networkidle')
        
        # Get fully rendered HTML
        html = page.content()
        browser.close()
    
    # Use BeautifulSoup for parsing (easier syntax)
    soup = BeautifulSoup(html, 'html.parser')
    projects = soup.find_all('div', class_='project-container')
    # Parse as needed...
```

### Performance Comparison

| Method | Speed | Complexity | Reliability |
|--------|-------|------------|-------------|
| **API endpoints** (if found) | ⚡ Fastest | Low | High |
| **BeautifulSoup alone** | ⚡ Fast | Low | Won't work for JS sites |
| **Playwright alone** | 🐢 Slower | Medium | High |
| **Playwright + BS4** | 🐢 Slower | Low | High |

---

## Discovery: API Endpoints Found! 🎉

### Network Tab Analysis Results
Found direct API endpoints returning JSON:
- `/api/new_projects?ts=175598691294.144`
- `/api/watch_list?ts=17559...`
- Response type: `application/json`
- The `ts` parameter appears to be a timestamp for pagination/filtering

### Recommended Implementation: Direct API Calls

```python
import requests
import json
from typing import List, Dict
import time

class Web3AlertsScraper:
    def __init__(self, cookies_path: str):
        self.base_url = "https://web3alerts.app"
        self.session = requests.Session()
        self.load_cookies(cookies_path)
    
    def load_cookies(self, cookies_path: str):
        """Load exported cookies into the session"""
        with open(cookies_path, 'r') as f:
            cookies = json.load(f)
            for cookie in cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
    
    def get_new_projects(self, ts: str = None) -> List[Dict]:
        """Fetch new projects from the API"""
        url = f"{self.base_url}/api/new_projects"
        params = {'ts': ts} if ts else {}
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_watch_list(self, ts: str = None) -> List[Dict]:
        """Fetch watch list from the API"""
        url = f"{self.base_url}/api/watch_list"
        params = {'ts': ts} if ts else {}
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_all_projects_paginated(self, max_pages: int = 10):
        """Fetch all projects with pagination"""
        all_projects = []
        ts = None
        
        for page in range(max_pages):
            try:
                projects = self.get_new_projects(ts=ts)
                if not projects:
                    break
                    
                all_projects.extend(projects)
                
                # Extract timestamp for next page
                if projects:
                    ts = projects[-1].get('timestamp') or projects[-1].get('ts')
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error on page {page}: {e}")
                break
        
        return all_projects

# Usage
scraper = Web3AlertsScraper('cookies.json')
projects = scraper.get_new_projects()
print(json.dumps(projects, indent=2))
```

---

## Full Project Implementation

### 1. Endpoint Discovery
```python
def discover_endpoints():
    """Systematically discover all API endpoints"""
    potential_endpoints = [
        '/api/new_projects',
        '/api/trending_projects',
        '/api/watch_list',
        '/api/categories',
        '/api/top_gainers',
        '/api/project/{id}',
        '/api/search',
        '/api/filters',
    ]
    # Test each and document what works
```

### 2. Robust Data Pipeline
```python
import sqlite3
import pandas as pd
from datetime import datetime
import schedule

class Web3DataPipeline:
    def __init__(self):
        self.setup_database()
    
    def setup_database(self):
        """Create tables for storing historical data"""
        conn = sqlite3.connect('web3_projects.db')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                stars INTEGER,
                upvotes INTEGER,
                twitter_followers INTEGER,
                first_seen TIMESTAMP,
                last_updated TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS project_metrics (
                project_id TEXT,
                timestamp TIMESTAMP,
                stars INTEGER,
                upvotes INTEGER,
                twitter_followers INTEGER,
                trending_position INTEGER,
                FOREIGN KEY(project_id) REFERENCES projects(id)
            )
        ''')
        conn.commit()
    
    def track_metrics_over_time(self):
        """Store metrics periodically to track growth"""
        # Fetch current data
        # Compare with previous data
        # Calculate growth rates
        # Identify fast-moving projects
        pass
```

### 3. Intelligence Layer
```python
import numpy as np

def analyze_trends(df: pd.DataFrame):
    """Identify interesting patterns"""
    
    # Fast movers (high growth rate)
    df['follower_growth_rate'] = df.groupby('project_id')['twitter_followers'].pct_change()
    fast_movers = df[df['follower_growth_rate'] > 0.1]  # 10% growth
    
    # Quality signals
    df['quality_score'] = (
        df['stars'] * 0.3 + 
        df['upvotes'] * 0.2 + 
        np.log1p(df['twitter_followers']) * 0.5
    )
    
    # Early gems (high quality, recently discovered)
    early_gems = df[
        (df['quality_score'] > df['quality_score'].quantile(0.8)) &
        (df['days_since_found'] < 3)
    ]
    
    return {
        'fast_movers': fast_movers,
        'early_gems': early_gems,
        'top_quality': df.nlargest(10, 'quality_score')
    }
```

### 4. Smart Monitoring & Alerts
```python
class AlertSystem:
    def __init__(self):
        self.alert_rules = []
    
    def add_rule(self, name, condition, action):
        """Add custom alert rules"""
        self.alert_rules.append({
            'name': name,
            'condition': condition,
            'action': action
        })
    
    def check_alerts(self, new_data):
        """Check if any alerts should fire"""
        for rule in self.alert_rules:
            if rule['condition'](new_data):
                rule['action'](new_data)

# Example rules
alert_system = AlertSystem()

alert_system.add_rule(
    name="New High-Quality Project",
    condition=lambda x: x['quality_score'] > 90 and x['is_new'],
    action=lambda x: send_notification(f"New gem found: {x['name']}")
)

alert_system.add_rule(
    name="Viral Growth Detected",
    condition=lambda x: x['follower_growth_24h'] > 100,
    action=lambda x: send_notification(f"{x['name']} is going viral!")
)
```

### 5. Performance Optimizations
```python
import asyncio
import aiohttp
import time
from functools import lru_cache

class OptimizedScraper:
    def __init__(self):
        self.session = None
        self.rate_limit = 2  # requests per second
        self.last_request = 0
    
    async def fetch_with_rate_limit(self, url):
        """Respect rate limits"""
        time_since_last = time.time() - self.last_request
        if time_since_last < (1 / self.rate_limit):
            await asyncio.sleep((1 / self.rate_limit) - time_since_last)
        
        async with self.session.get(url) as response:
            self.last_request = time.time()
            return await response.json()
    
    @lru_cache(maxsize=128)
    def get_cached_project(self, project_id):
        """Cache frequently accessed data"""
        pass
```

### 6. Quick Dashboard with Streamlit
```python
import streamlit as st
import plotly.express as px

def create_dashboard():
    st.title("Web3 Projects Tracker")
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Projects", len(df))
    with col2:
        st.metric("New Today", new_today_count)
    with col3:
        st.metric("Trending Now", trending_count)
    
    # Charts
    fig = px.scatter(df, 
                     x='twitter_followers', 
                     y='stars',
                     size='upvotes',
                     hover_data=['name'],
                     title='Project Quality Matrix')
    st.plotly_chart(fig)
```

---

## Testing Script for API Endpoints

```python
import requests
import json

def test_api_endpoints():
    # Load your cookies
    with open('cookies.json', 'r') as f:
        cookies = json.load(f)
    
    # Convert to requests format
    cookie_dict = {c['name']: c['value'] for c in cookies}
    
    # Test endpoints
    endpoints = [
        '/api/new_projects',
        '/api/watch_list',
        '/api/trending',
        '/api/projects',
    ]
    
    for endpoint in endpoints:
        try:
            url = f"https://web3alerts.app{endpoint}"
            response = requests.get(url, cookies=cookie_dict)
            print(f"\n{endpoint}:")
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Data type: {type(data)}")
                if isinstance(data, list):
                    print(f"  Items: {len(data)}")
                    if data:
                        print(f"  First item keys: {data[0].keys()}")
        except Exception as e:
            print(f"  Error: {e}")

test_api_endpoints()
```

---

## Implementation Best Practices

### Pro Tips:
1. **Save Everything**: Store raw API responses - you might discover useful fields later
2. **Track Deltas**: Monitor what changes between API calls (new projects, metric changes)
3. **Pattern Recognition**: Look for which influencers consistently find gems early
4. **Time-based Analysis**: Some projects might trend at specific times/days
5. **Cross-reference**: If possible, correlate with on-chain data or Twitter API

### Implementation Considerations
- **Respect robots.txt** and terms of service
- **Implement caching** to minimize repeated requests
- **Data freshness strategy**: How often to update each project
- **Incremental updates**: Only fetch new/changed data
- **Rate limiting**: Implement delays to avoid detection
- **Error recovery**: Retry logic for failed requests

### Advanced Features to Consider
- **Cross-reference data**: Pull additional data from Twitter API, on-chain data
- **ML predictions**: Predict which projects will trend based on early signals
- **Automated reports**: Daily/weekly summaries of top movers
- **API service**: Expose your analyzed data through your own API

---

## Conclusion

The discovery of API endpoints makes this project significantly more straightforward to implement. Using direct API calls is:
- **10-100x faster** than browser automation
- More reliable and stable
- Easier to maintain and scale
- Less resource-intensive

The API-based approach eliminates the need for BeautifulSoup or Playwright entirely, allowing you to work directly with JSON responses for a clean, efficient data pipeline.

---

*Document created: September 2025*  
*Project: Web3 Startup Analysis Tool*  
*Purpose: Personal research on trending web3 startups*