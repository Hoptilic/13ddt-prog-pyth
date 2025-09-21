```
                                               
         ,--.                                  
       ,--.'|  ,----..     ,---,         ,---, 
   ,--,:  : | /   /   \   '  .' \     ,`--.' | 
,`--.'`|  ' :|   :     : /  ;    '.   |   :  : 
|   :  :  | |.   |  ;. /:  :       \  :   |  ' 
:   |   \ | :.   ; /--` :  |   /\   \ |   :  | 
|   : '  '; |;   | ;    |  :  ' ;.   :'   '  ; 
'   ' ;.    ;|   : |    |  |  ;/  \   \   |  | 
|   | | \   |.   | '___ '  :  | \  \ ,'   :  ; 
'   : |  ; .''   ; : .'||  |  '  '--' |   |  ' 
|   | '`--'  '   | '/  :|  :  :       '   :  | 
'   : |      |   :    / |  | ,'       ;   |.'  
;   |.'       \   \ .'  `--''         '---'    
'---'          `---`                           
                                               

N C A I  —  New Zealand Curriculum Artificial Intelligence
```

# NCAI (PyQt6 Desktop App)

A desktop app that helps students submit writing, sends it to an LLM for feedback, and shows inline, hoverable highlights with a grade estimate. Built with PyQt6 and SQLite, with a simple login system and file‑backed sessions/cookies.

## Features

- Clean PyQt6 UI with pages: Login, Home, New Submission, Submissions, User (account)
- LLM feedback with inline highlighted HTML and tooltips for targeted suggestions
- Character limit and live counter on submissions (50,000 characters)
- Background processing with a modal progress dialog (no UI freezes)
- Rate‑limit resilience: short retries and a friendly message if the service is busy
- SQLite storage for exemplars and saved submissions; user login DB with salted+hashed passwords
- .env configuration for API keys (no hardcoded secrets)

## Screens/Pages

- Login: Register or log in; sessions/cookies are persisted locally
- Home: Quick actions (new submission, view submissions)
- New Submission: Pick standard/year, type/paste text, submit for feedback; rendered highlights + grade
- Submissions: Grid of recent items; click to view full details
- User: Change password, delete account

## Tech Stack

- Python 3.11+ (works with 3.13)
- PyQt6 for UI
- SQLite for databases (submissions, exemplars, login)
- openai (OpenAI‑compatible client for OpenRouter)
- python‑dotenv for environment variables

## Setup

1) Clone the repo and create a virtual environment (optional but recommended)

2) Install dependencies (examples; adjust to your environment):

```powershell
# Inside your virtual environment
pip install PyQt6 openai python-dotenv
```

3) Configure environment variables (create a .env at the project root):

```
OPENROUTER_API_KEY=your_api_key_here
# Optional override (defaults supported by the app if you omit this)
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

There is a `.env.example` in the repo you can copy and fill.

## Run the app

```powershell
python .\main.py
```

On first launch, register a user on the Login page. After login, you'll land on Home. Start a New Submission to paste your writing and submit.

## Data & Storage

- Databases live under `database/`:
	- `LLM_testdatabase.db` (exemplars/standards for testing)
	- `login.db` (user credentials)
	- `submissions` table is created automatically on first run
- Session and cookie storage are file‑backed:
	- `session.txt` holds current username + cookie ID
	- `cookies.txt` maintains issued cookies and expiry

## Notes on behavior

- Character limit: The New Submission editor enforces a hard limit of 50,000 characters and shows a live counter under the editor (amber near limit, red at the limit).
- Rate limiting: If the LLM service returns HTTP 429, the app retries quickly (up to 5 short attempts). If still busy, the app shows a friendly message: “We're a bit busy right now… Please try again in a minute.”
- Rendering: The app converts the LLM's HighlightedHTML into styled, clickable spans with tooltips; common HTML entities in prose are normalized.

## Testing (optional helpers)

- Quick DB introspection: `tests/test_db_llm.py` prints available tables and parses exemplar JSON.
- Additional tests live in `tests/` and cover various parts of the app.

Run tests with your usual Python test runner or simply execute the scripts with Python if they're standalone.

## Troubleshooting

- Missing API key
	- Symptom: “LLM Error: Missing OPENROUTER_API_KEY…”
	- Fix: Create `.env` and set `OPENROUTER_API_KEY`. Restart the app.

- Rate limited (429)
	- Symptom: Friendly busy message after a few quick retries.
	- Fix: Wait a minute and try again. Your text is still in the editor.

- No standards/years in dropdowns
	- Symptom: Empty standard/year lists
	- Fix: Ensure `database/LLM_testdatabase.db` exists and has the expected tables.

- Windows scaling / DPI
	- If fonts or widgets look off, try adjusting system display scaling or tweak PyQt's application attributes.

## Project structure (high level)

```
gui/                 # UI pages and widgets
database/            # SQLite managers and files
socketing/           # Login/session/cookie helpers
llm/socketing/       # LLM handler (prompting, parsing, rate‑limit handling)
tests/               # Misc test scripts
main.py              # App entry point
```