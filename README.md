# AI SDR Agent

An autonomous AI agent that automates the SDR (Sales Development Representative) workflow, from finding leads to sending personalized emails and logging interactions.

## Features

- ✅ Takes an ICP (Ideal Customer Profile) as input
- ✅ Finds 5-10 real, verified leads
- ✅ Writes personalized cold emails
- ✅ Sends emails via Gmail API or other providers
- ✅ Logs interactions in a CRM (Airtable, Supabase, or local CSV)
- ✅ Acts autonomously using GPT-4 or Gemini function calling

## Architecture

```
             +------------------+
             |   User Input     |  (CLI: Goal + ICP)
             +------------------+
                      |
                      v
           +-----------------------+
           |   Agent Planner       |  (OpenAI/Gemini Function Calling)
           +-----------------------+
            |     |      |     |     
            |     |      |     |
            ↓     ↓      ↓     ↓
+----------------+----------------+----------------+----------------+
|  get_leads()   |  write_email() | send_email()   |  log_to_crm()  |
| (Apollo, CSV)  | (LLM Prompt)   | (Gmail API)    | (Airtable)     |
+----------------+----------------+----------------+----------------+
```

## Installation

1. Clone the repository
2. Install dependencies:

```bash
cd ai_sdr_agent
pip install -r requirements.txt
```

3. Copy the environment variables example file and fill in your values:

```bash
cp env.example .env
# Edit .env with your API keys and configuration
```

## Usage

### Basic Usage

Run the agent in test mode (easiest to get started):

```bash
python main.py --mode test
```

Run the agent in interactive mode:

```bash
python main.py --mode interactive
```

Run the agent in automatic mode:

```bash
python main.py --mode auto
```

### Configuration

You can configure the agent by editing the `config.json` file (will be created automatically on first run) or by passing a custom config file:

```bash
python main.py --config my_config.json
```

Example configuration:

```json
{
  "goal": "Book meetings",
  "industry": "AI SaaS",
  "location": "United States",
  "role": "Founder",
  "product": "an AI that improves cold outreach response rate by 40%",
  "lead_source": "csv",
  "email_provider": "gmail",
  "crm": "airtable",
  "leads_per_day": 5,
  "follow_up_days": 2
}
```

### LLM Providers

The agent supports multiple LLM providers:

1. **OpenAI** (default)
   - Set `LLM_PROVIDER=openai` in your `.env` file
   - Requires `OPENAI_API_KEY`
   - Optionally set `OPENAI_MODEL` (default: gpt-4)

2. **Google Gemini**
   - Set `LLM_PROVIDER=gemini` in your `.env` file
   - Requires `GEMINI_API_KEY`
   - Optionally set `GEMINI_MODEL` (default: gemini-2.5-pro)

## Modules

### 1. Lead Generation

Supports multiple lead sources:
- Apollo.io API (paid)
- CSV import (included sample data)
- PhantomBuster (planned)

### 2. Email Writing

Uses LLMs to generate personalized cold emails based on:
- Recipient's name, title, and company
- Industry context
- Your product description

### 3. Email Sending

Supports multiple email providers:
- Gmail API
- MailerSend
- SendGrid (planned)

### 4. CRM Logging

Logs all interactions to your preferred CRM:
- Airtable
- Supabase
- Local CSV (default fallback)
- Notion (planned)

## Testing

By default, the agent runs in test mode, which means:
- Emails are not actually sent (just logged to console)
- CRM entries are not actually created (just logged to console)

To enable real sending/logging, set the following in your `.env` file:

```
EMAIL_TEST_MODE=false
CRM_TEST_MODE=false
```

## License

MIT 