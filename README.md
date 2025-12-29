# Early Web3 Project Poster

Automated Twitter bot that fetches the latest Web3 projects from Web3 Alerts and posts daily summaries to X/Twitter via Typefully.

## Features

- Fetches latest projects from Web3 Alerts API
- Summarizes descriptions using Google Gemini AI
- Posts to X/Twitter via Typefully API
- Scheduled publishing (upload now, publish later)
- Rate limit handling with graceful fallback

## How It Works

1. **Fetch**: Retrieves latest projects from Web3 Alerts (sorted by discovery date)
2. **Summarize**: Uses Gemini AI to create concise 10-word summaries
3. **Format**: Creates a formatted tweet with project names, handles, and summaries
4. **Schedule**: Uploads to Typefully with 6-hour delayed publishing

## Setup

### Prerequisites

- Python 3.10+
- Web3 Alerts account (for cookies)
- Typefully API key
- Google Gemini API key

### Installation

```bash
git clone https://github.com/0xjayfi/early-project-poster.git
cd early-project-poster
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```bash
# Typefully Configuration
TYPEFULLY_API_KEY=your_typefully_api_key

# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash-lite

# Scheduling
TYPEFULLY_HOURS_DELAY=6

# Bot Configuration
PROJECTS_COUNT=10
SUMMARY_MAX_WORDS=10
```

### Cookies Setup

Export cookies from Web3 Alerts website:

1. Log into https://web3alerts.app
2. Use a browser extension to export cookies as JSON
3. Save to `credentials/cookies.json`

## Usage

### Run Manually

```bash
# Scheduled mode (publish in 6 hours)
python main.py

# Instant publish
python main.py --now
```

### Cron Job (Daily at 11 AM SGT)

```bash
crontab -e
```

Add:
```cron
# 11 AM SGT (3 AM UTC)
0 3 * * * cd /path/to/early-project-poster && /usr/bin/python3 main.py >> /var/log/web3alerts.log 2>&1
```

If your server uses SGT timezone:
```cron
0 11 * * * cd /path/to/early-project-poster && /usr/bin/python3 main.py >> /var/log/web3alerts.log 2>&1
```

## Gemini API Rate Limits

| Model | RPM (Requests/Min) | TPM (Tokens/Min) | RPD (Requests/Day) |
|-------|-------------------|------------------|-------------------|
| Gemini 2.5 Pro | 5 | 250,000 | 100 |
| Gemini 2.5 Flash | 10 | 250,000 | 250 |
| **Gemini 2.5 Flash-Lite** | **15** | **250,000** | **1,000** |
| Gemini 2.0 Flash | 15 | 1,000,000 | 200 |
| Gemini 2.0 Flash-Lite | 30 | 1,000,000 | 200 |

**Recommended**: `gemini-2.5-flash-lite` for best balance of rate limits (1,000 RPD) and quality.

## Output Format

```
Early web3 projects (Dec 29)

1 ProjectName (@handle): AI-generated summary here.

2 ProjectName (@handle): AI-generated summary here.

...

10 ProjectName (@handle): AI-generated summary here.
```

## Project Structure

```
early-project-poster/
├── main.py                 # Main bot script
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in repo)
├── .env.example            # Example environment file
├── credentials/
│   └── cookies.json        # Web3 Alerts cookies (not in repo)
├── modules/
│   ├── web3alerts_scraper.py    # Web3 Alerts API client
│   ├── gemini_summarizer.py     # Gemini AI summarizer
│   └── typefully_publisher.py   # Typefully API client
└── docs/
    ├── typefully-api-docs.md    # Typefully API reference
    └── web3-scraping-guide.md   # Web3 Alerts scraping guide
```

## Notes

- **GitHub Actions**: Not recommended - Web3 Alerts blocks datacenter IPs
- **Local/VM**: Run on local machine or VM with residential IP
- **Cookies Expiry**: Re-export cookies if authentication fails

## License

MIT
