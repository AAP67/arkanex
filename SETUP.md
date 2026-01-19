# ArkaneX - Complete Setup Instructions

## New Dependencies Required

Install these new packages:
```bash
pip install requests beautifulsoup4 reportlab
```

Or install everything from requirements.txt:
```bash
pip install -r requirements.txt
```

## New Features Added

### 1. ✅ Copy to Clipboard / Download as Markdown
- After generating questions, click "📋 Copy as Markdown"
- Downloads a formatted .md file with all questions
- Easy to paste into Google Docs, email, etc.

### 2. ✅ Export to PDF
- Click "📥 Download PDF" to get professional PDF
- Includes:
  - Cover page with ArkaneX branding
  - Company & job information
  - All questions with formatted rubrics
  - Follow-up questions
  - Your branding in footer

### 3. ✅ Save/Load Sessions
- Click "💾 Save Session" to download .json file
- Saves all inputs + generated questions
- Upload in sidebar to restore previous session
- Perfect for working on multiple roles

### 4. ✅ Web Scraping
- **Company Website:** Paste URL, click "🔍 Auto-Extract Company Info"
  - Automatically scrapes company description
  - Fills company context field
- **Job Posting:** Paste JD URL, click "🔍 Auto-Extract Job Description"
  - Scrapes full job description
  - Populates JD text field

## How to Test New Features

1. **Test Web Scraping:**
   - Enter "https://render.com" in Company Website URL
   - Click "Auto-Extract Company Info"
   - See company description populate

2. **Test PDF Export:**
   - Generate questions
   - Click "Download PDF"
   - Open the PDF - see professional formatting

3. **Test Save/Load:**
   - Generate questions
   - Click "Save Session"
   - Refresh page
   - Upload the .json file in sidebar
   - See everything restored

4. **Test Markdown Copy:**
   - Generate questions
   - Click "Copy as Markdown"
   - Open in text editor to see formatted output

## Running the App

```bash
streamlit run app.py
```

## Deploying to Streamlit Cloud

1. Push to GitHub repository
2. Add `requirements.txt` to repo
3. Add `.streamlit/secrets.toml` with your API key:
   ```toml
   ANTHROPIC_API_KEY = "your-key-here"
   ```
4. Deploy on Streamlit Cloud
5. Set secrets in Streamlit Cloud dashboard

## What's Next

The app is now production-ready with:
- ✅ Professional UI
- ✅ Web scraping
- ✅ PDF export
- ✅ Session management
- ✅ Easy sharing

Ready to deploy and send to companies!
