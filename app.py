import streamlit as st
import streamlit.components.v1 as components
import anthropic
import json
from io import BytesIO
import PyPDF2
from docx import Document
import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import base64
import time

# Page configuration
st.set_page_config(
    page_title="ArkaneX - Interview Intelligence for Strategic Roles",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'mailto:karan.rajpal@berkeley.edu',
        'Report a bug': 'mailto:karan.rajpal@berkeley.edu',
        'About': "ArkaneX - Interview Intelligence Platform. Generate company-specific interview questions for Chief of Staff, BizOps, and Strategy roles. Built by Karan Rajpal."
    }
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Force light theme */
    .stApp {
        background-color: #ffffff;
    }
    
    /* ===== SIDEBAR STYLING ===== */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #1a1a1a !important;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #1a1a1a !important;
    }
    
    /* ===== HEADER ===== */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2.5rem;
    }
    
    .main-header p {
        color: #e0e7ff !important;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    /* ===== BUTTONS - COMPREHENSIVE OVERRIDE ===== */
    /* Regular buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: bold !important;
        padding: 0.75rem 2rem !important;
        border-radius: 8px !important;
        border: none !important;
        width: 100% !important;
        font-size: 1.1rem !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Force all button elements to have visible styling */
    button[kind="primary"],
    button[kind="secondary"],
    button[data-testid="baseButton-primary"],
    button[data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    /* Override any dark theme button styling */
    button {
        background-color: #667eea !important;
        color: white !important;
    }
    
    /* ===== DOWNLOAD BUTTONS ===== */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: bold !important;
        padding: 0.75rem 2rem !important;
        border-radius: 8px !important;
        border: none !important;
        width: 100% !important;
        font-size: 1.1rem !important;
    }
    
    .stDownloadButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Primary download button (PDF) */
    .stDownloadButton>button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        font-size: 1.2rem !important;
    }
    
    /* Secondary download buttons */
    .stDownloadButton>button[kind="secondary"] {
        background: linear-gradient(135deg, #8b9dc3 0%, #9da8c4 100%) !important;
        color: white !important;
    }
    
    /* ===== ACTION BUTTONS ===== */
    .action-buttons {
        display: flex;
        gap: 1rem;
        margin: 2rem 0;
        flex-wrap: wrap;
    }
    
    /* ===== UPLOAD SECTION ===== */
    .upload-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 2px dashed #667eea;
        margin: 1rem 0;
    }
    
    /* ===== QUESTION DISPLAY ===== */
    div[data-testid="stMarkdownContainer"] h3 {
        color: #333333 !important;
        font-size: 1.3rem !important;
        margin-bottom: 1rem !important;
    }
    
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] li {
        color: #333333 !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }
    
    div[data-testid="stMarkdownContainer"] strong {
        color: #000000 !important;
        font-size: 1.1rem !important;
    }
    
    /* ===== BADGES ===== */
    .excellent-badge {
        background: #d4edda !important;
        color: #155724 !important;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 1rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 1rem;
    }
    
    .redflag-badge {
        background: #f8d7da !important;
        color: #721c24 !important;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 1rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 1rem;
    }
    
    /* ===== GLOBAL TEXT VISIBILITY ===== */
    .stMarkdown, .stText {
        color: #333333 !important;
    }
    
    h2, h3 {
        color: #1f2937 !important;
        font-weight: 600 !important;
    }
    
    /* ===== EXPANDER STYLING ===== */
    .streamlit-expanderHeader {
        color: #333333 !important;
        font-size: 1rem !important;
    }
    
    .streamlit-expanderContent {
        color: #333333 !important;
    }
    
    /* ===== INPUT FIELDS ===== */
    input[type="text"],
    input[type="email"],
    input[type="url"] {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 1px solid #d1d5db !important;
        border-radius: 6px !important;
        padding: 0.5rem !important;
    }
    
    input[type="text"]:focus,
    input[type="email"]:focus,
    input[type="url"]:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 1px #667eea !important;
    }
    
    textarea {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 1px solid #d1d5db !important;
        border-radius: 6px !important;
        padding: 0.5rem !important;
    }
    
    textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 1px #667eea !important;
    }
    
    input::placeholder,
    textarea::placeholder {
        color: #9ca3af !important;
        opacity: 1 !important;
    }
    
    label {
        color: #1f2937 !important;
        font-weight: 500 !important;
    }
    
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    .stTextArea > div > div > textarea {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    
    /* ===== FILE UPLOADER STYLING ===== */
    /* Main file uploader container */
    [data-testid="stFileUploader"] {
        background-color: #ffffff !important;
    }
    
    [data-testid="stFileUploader"] > div {
        background-color: #ffffff !important;
        border: 2px dashed #d1d5db !important;
        border-radius: 8px !important;
        padding: 1.5rem !important;
    }
    
    [data-testid="stFileUploader"] section {
        background-color: #f9fafb !important;
        border: 2px dashed #667eea !important;
    }
    
    [data-testid="stFileUploader"] section > div {
        color: #1a1a1a !important;
    }
    
    [data-testid="stFileUploader"] label {
        color: #1f2937 !important;
    }
    
    [data-testid="stFileUploader"] small {
        color: #6b7280 !important;
    }
    
    /* File uploader button */
    [data-testid="stFileUploader"] button {
        background-color: #667eea !important;
        color: white !important;
        border: none !important;
    }
    
    /* Uploaded file display */
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDeleteBtn"] {
        color: #dc2626 !important;
    }
    
    /* File name text */
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"] {
        color: #1a1a1a !important;
    }
</style>
""", unsafe_allow_html=True)

# Google Analytics (replace G-XXXXXXXXXX with your actual tracking ID)
# To get a tracking ID: https://analytics.google.com/
st.markdown("""
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_questions' not in st.session_state:
    st.session_state.generated_questions = None
if 'company_info' not in st.session_state:
    st.session_state.company_info = None
if 'job_info' not in st.session_state:
    st.session_state.job_info = None
if 'candidate_info' not in st.session_state:
    st.session_state.candidate_info = None

# Helper function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Helper function to extract text from DOCX
def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text

# Web scraping function for company website
def scrape_company_info(url):
    """Scrape basic company information from website"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to extract company description
        description = ""
        
        # Look for common meta tags
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            description = meta_desc.get('content', '')
        
        # Look for about section
        if not description:
            about_section = soup.find(['p', 'div'], class_=lambda x: x and ('about' in x.lower() or 'description' in x.lower()))
            if about_section:
                description = about_section.get_text(strip=True)[:500]
        
        # If still no description, get first substantial paragraph
        if not description:
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 100:
                    description = text[:500]
                    break
        
        return description if description else "Unable to extract company information automatically. Please add manually."
    
    except Exception as e:
        return f"Error scraping website: {str(e)}"

# Web scraping function for job description
def scrape_job_description(url):
    """Scrape job description from URL"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find job description container
        jd_text = ""
        
        # Common job board selectors
        jd_containers = soup.find_all(['div', 'section'], class_=lambda x: x and any(
            term in x.lower() for term in ['job-description', 'description', 'content', 'posting']
        ))
        
        for container in jd_containers:
            text = container.get_text(separator='\n', strip=True)
            if len(text) > 200:  # Substantial content
                jd_text = text
                break
        
        # If no specific container, get main content
        if not jd_text:
            main = soup.find('main') or soup.find('body')
            if main:
                jd_text = main.get_text(separator='\n', strip=True)
        
        return jd_text if jd_text else "Unable to extract job description. Please paste manually."
    
    except Exception as e:
        return f"Error scraping job posting: {str(e)}"

# Function to generate interview questions using Claude
def generate_interview_questions(api_key, company_info, job_info, candidate_info, num_questions, question_type):
    """Generate interview questions using Claude API"""
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        if question_type == "Conversational Questions":
            question_style = "conversational behavioral and situational"
            style_guidance = """These should be open-ended questions that encourage storytelling and specific examples.
Assess: past experiences, problem-solving approach, leadership, stakeholder management, communication, influence, strategic thinking, prioritization, and cultural fit."""
        else:
            question_style = "scenario-based case study"
            style_guidance = """These should be realistic business scenarios with specific constraints, numbers, timelines, and named stakeholders.
Assess: real-time problem-solving, analytical thinking, operational execution, cross-functional coordination, resource allocation, and trade-off decisions."""

        system_prompt = f"""You are a senior interview designer specializing in Chief of Staff, Business Operations, and Strategy roles at high-growth companies.

Your job is to create {num_questions} {question_style} interview questions that are deeply grounded in the specific company, role, and candidate provided below.

GROUNDING RULES — follow these strictly:
1. Every question MUST reference at least one specific detail from the company context (e.g., industry, stage, product, challenge, competitor, team size).
2. Every scenario or setup MUST be plausible for THIS company — not generic. Use the company's actual domain, scale, and constraints.
3. At least half the questions should probe gaps or mismatches between the candidate's background and the role requirements. Identify what's untested.
4. Rubric items must be specific enough that two interviewers would agree on scoring. No vague criteria like "shows leadership."
5. Follow-ups should escalate difficulty — push deeper, not sideways.

STYLE: {style_guidance}

OUTPUT FORMAT: Return ONLY a valid JSON array. No markdown, no code fences, no commentary. Structure:
[
  {{
    "title": "5-7 word title",
    "scenario": "Detailed scenario grounded in company context (case study) or question setup with specific framing (conversational)",
    "question": "The core question to ask the candidate",
    "rubric": {{
      "excellent": ["Specific observable indicator 1", "Specific observable indicator 2", "...(5-6 total)"],
      "redFlags": ["Specific warning sign 1", "Specific warning sign 2", "...(4-5 total)"]
    }},
    "followUps": ["Escalating follow-up 1", "Escalating follow-up 2", "Escalating follow-up 3"]
  }}
]"""

        user_prompt = f"""<company>
{company_info}
</company>

<role>
{job_info}
</role>

<candidate>
{candidate_info}
</candidate>

Generate {num_questions} interview questions now."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        response_text = message.content[0].text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])
        
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        questions = json.loads(response_text)
        return questions, None
        
    except json.JSONDecodeError as e:
        return None, "Error parsing AI response. Please try generating again. If the issue persists, contact support."
    except anthropic.APIError as e:
        if "rate_limit" in str(e).lower():
            return None, "⚠️ Rate limit reached. Please wait a moment and try again."
        elif "invalid_api_key" in str(e).lower():
            return None, "⚠️ API configuration error. Please contact administrator."
        else:
            return None, f"⚠️ API error: {str(e)}. Please try again in a moment."
    except anthropic.APIConnectionError:
        return None, "⚠️ Network error. Please check your connection and try again."
    except anthropic.APITimeoutError:
        return None, "⚠️ Request timed out. The AI is taking longer than expected. Please try again."
    except Exception as e:
        return None, f"⚠️ Unexpected error: {str(e)}. Please try again or contact support."

# Function to generate PDF
def generate_pdf(questions, company_info, job_info, question_type):
    """Generate a professional PDF of the interview questions"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#333333'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=HexColor('#666666'),
        spaceAfter=8
    )
    
    # Extract company name and job title for cover
    company_name_extract = "Company Not Specified"
    if "Company:" in company_info:
        company_line = company_info.split('\n')[0]
        company_name_extract = company_line.replace("Company:", "").strip()
    
    job_title_extract = "Strategic Role"
    if "Job Title:" in job_info:
        job_line = [line for line in job_info.split('\n') if 'Job Title:' in line][0]
        job_title_extract = job_line.replace("Job Title:", "").strip()
    
    # Cover page - Enhanced
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("🎯 ArkaneX", title_style))
    story.append(Paragraph("Interview Intelligence Platform", styles['Normal']))
    story.append(Spacer(1, 0.5*inch))
    
    # Horizontal line
    story.append(Paragraph("_" * 80, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("<b>Interview Questions For:</b>", heading_style))
    story.append(Paragraph(f"<b>{company_name_extract}</b>", title_style))
    story.append(Paragraph(f"<i>{job_title_extract}</i>", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Paragraph(f"<b>Question Type:</b> {question_type}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Horizontal line
    story.append(Paragraph("_" * 80, styles['Normal']))
    story.append(Spacer(1, 0.5*inch))
    
    # Contact info on cover
    story.append(Paragraph("<b>Contact:</b>", styles['Normal']))
    story.append(Paragraph("Built by Karan Rajpal | Haas MBA '25 | Handshake AI", styles['Normal']))
    story.append(Paragraph("📧 karan.rajpal@berkeley.edu | 💼 linkedin.com/in/krajpal", styles['Normal']))
    
    story.append(PageBreak())
    
    # Company & job info
    story.append(Paragraph("Company & Role Information", heading_style))
    story.append(Paragraph(company_info.replace('\n', '<br/>'), styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(job_info.replace('\n', '<br/>'), styles['Normal']))
    story.append(PageBreak())
    
    # Questions
    for idx, q in enumerate(questions, 1):
        story.append(Paragraph(f"Question {idx}: {q['title']}", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        if q.get('scenario'):
            story.append(Paragraph("<b>Scenario/Context:</b>", subheading_style))
            story.append(Paragraph(q['scenario'], styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        story.append(Paragraph("<b>Question:</b>", subheading_style))
        story.append(Paragraph(q['question'], styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("<b>✅ Excellent Responses:</b>", subheading_style))
        for point in q['rubric']['excellent']:
            story.append(Paragraph(f"• {point}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        
        story.append(Paragraph("<b>🚩 Red Flags:</b>", subheading_style))
        for flag in q['rubric']['redFlags']:
            story.append(Paragraph(f"• {flag}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        
        story.append(Paragraph("<b>💡 Follow-up Questions:</b>", subheading_style))
        for i, followup in enumerate(q['followUps'], 1):
            story.append(Paragraph(f"{i}. {followup}", styles['Normal']))
        
        story.append(PageBreak())
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("<b>ArkaneX - Interview Intelligence Platform</b>", styles['Normal']))
    story.append(Paragraph("Generated with AI-powered interview intelligence for strategic roles", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("<b>Contact:</b>", styles['Normal']))
    story.append(Paragraph("Built by Karan Rajpal | Haas MBA '25 | Handshake AI", styles['Normal']))
    story.append(Paragraph("📧 karan.rajpal@berkeley.edu | 💼 linkedin.com/in/krajpal", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Function to create downloadable JSON
def create_session_json(company_name, company_url, company_context, job_title, job_description, jd_link, 
                        candidate_name, candidate_profile, num_questions, question_type, questions):
    """Create a JSON file with all session data"""
    session_data = {
        "timestamp": datetime.now().isoformat(),
        "inputs": {
            "company_name": company_name,
            "company_url": company_url,
            "company_context": company_context,
            "job_title": job_title,
            "job_description": job_description,
            "jd_link": jd_link,
            "candidate_name": candidate_name,
            "candidate_profile": candidate_profile,
            "num_questions": num_questions,
            "question_type": question_type
        },
        "questions": questions
    }
    return json.dumps(session_data, indent=2)

# Function to format questions as markdown for copying
def format_questions_markdown(questions, company_info, job_info):
    """Format questions as markdown text for clipboard"""
    md = f"# Interview Questions\n\n"
    md += f"**Generated by ArkaneX**\n"
    md += f"**Date:** {datetime.now().strftime('%B %d, %Y')}\n\n"
    md += f"## Company Information\n{company_info}\n\n"
    md += f"## Job Details\n{job_info}\n\n"
    md += "---\n\n"
    
    for idx, q in enumerate(questions, 1):
        md += f"## Question {idx}: {q['title']}\n\n"
        
        if q.get('scenario'):
            md += f"**Scenario/Context:**\n{q['scenario']}\n\n"
        
        md += f"**Question:**\n{q['question']}\n\n"
        
        md += "### ✅ Excellent Responses\n"
        for point in q['rubric']['excellent']:
            md += f"- {point}\n"
        md += "\n"
        
        md += "### 🚩 Red Flags\n"
        for flag in q['rubric']['redFlags']:
            md += f"- {flag}\n"
        md += "\n"
        
        md += "### 💡 Follow-up Questions\n"
        for i, followup in enumerate(q['followUps'], 1):
            md += f"{i}. {followup}\n"
        md += "\n---\n\n"
    
    return md

# Header
st.markdown("""
<div class="main-header">
    <h1>🎯 ArkaneX</h1>
    <p>Interview Intelligence for Strategic Roles</p>
    <p style="font-size: 0.95rem; margin-top: 0.5rem; opacity: 0.95;">
        Generate company-specific interview questions for Chief of Staff, Business Operations, and Strategy positions
    </p>
</div>
""", unsafe_allow_html=True)

# Get API key from Streamlit secrets
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except:
    st.error("⚠️ API key not configured. Please contact administrator.")
    st.stop()

# Sidebar
with st.sidebar:
    st.subheader("🎨 Question Style")
    question_type = st.radio(
        "Select Interview Format:",
        options=["Conversational Questions", "Case Study Questions"],
        help="Conversational: Behavioral and situational questions\nCase Study: Scenario-based problem-solving questions"
    )
    
    st.markdown("---")
    
    # Usage Tips
    st.subheader("💡 Tips for Best Results")
    st.markdown("""
    **For Better Questions:**
    - Include specific company challenges
    - Mention recent news or initiatives
    - Add candidate's relevant experience
    
    **Question Types:**
    - **Conversational**: Test past experiences
    - **Case Study**: Test real-time thinking
    
    **Pro Tip:** Use the Auto-Extract feature to save time!
    """)
    
    st.markdown("---")
    
    # Load saved session
    st.subheader("💾 Load Previous Session")
    uploaded_session = st.file_uploader("Upload .json session file", type=['json'])
    
    if uploaded_session:
        try:
            session_data = json.load(uploaded_session)
            st.success("✅ Session loaded! Data populated below.")
            # Store in session state
            st.session_state.loaded_session = session_data
        except:
            st.error("❌ Invalid session file")
    
    st.markdown("---")
    st.markdown("### About ArkaneX")
    st.markdown("""
    ArkaneX helps hiring teams create consistent, high-quality interviews for strategic roles.
    
    **Generate questions that:**
    - Test real operational skills
    - Match your company's specific challenges
    - Include evaluation criteria for fair assessment
    - Save time while improving hiring quality
    """)
    st.markdown("---")
    st.markdown("**Questions? Feedback?**")
    st.markdown("Built by Karan Rajpal")
    st.markdown("Haas MBA '25 | Handshake AI")
    st.markdown("📧 [Contact](mailto:karan.rajpal@berkeley.edu) | 💼 [LinkedIn](https://www.linkedin.com/in/krajpal/)")
    
    st.markdown("---")
    
    # Share button
    st.subheader("📤 Share This Tool")
    share_url = "https://arkanex.streamlit.app"  # Update with your actual URL after deployment
    
    if st.button("📋 Copy Share Link", use_container_width=True):
        st.code(share_url, language=None)
        st.info("👆 Copy the link above to share with your team!")
    
    st.markdown("""
    <div style='background: #f0f4ff; padding: 0.75rem; border-radius: 6px; font-size: 0.85rem;'>
        <strong>Share with colleagues:</strong><br>
        "Check out ArkaneX - generates interview questions for strategic roles. 
        Just upload a JD and candidate resume!"
    </div>
    """, unsafe_allow_html=True)

# Main content area

# How It Works section
st.markdown("""
<div style='background: linear-gradient(135deg, #f0f4ff 0%, #e8edff 100%); 
            padding: 1.5rem; 
            border-radius: 10px; 
            border-left: 4px solid #667eea;
            margin-bottom: 2rem;'>
    <h3 style='color: #667eea; margin-top: 0;'>💡 How It Works</h3>
    <ol style='margin-bottom: 0; color: #1f2937; line-height: 1.8;'>
        <li><strong>Enter company information</strong> - Add company name or website URL</li>
        <li><strong>Provide job description</strong> - Paste the JD text or link to posting</li>
        <li><strong>Upload candidate resume</strong> - Add the candidate's profile or resume</li>
        <li><strong>Generate questions</strong> - Get customized interview questions with scoring rubrics in 30-60 seconds</li>
    </ol>
</div>
""", unsafe_allow_html=True)

st.header("📝 Input Information")

# Check if session was loaded
loaded_session = st.session_state.get('loaded_session', None)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏢 Company & Role Details")
    
    company_input_type = st.radio("Company Information:", ["Company Name", "Company Website URL"], horizontal=True)
    
    if company_input_type == "Company Name":
        company_name = st.text_input(
            "Company Name", 
            placeholder="e.g., Render, Coinbase, Kraken",
            value=loaded_session['inputs']['company_name'] if loaded_session and loaded_session['inputs'].get('company_name') else ""
        )
        company_url = None
    else:
        company_url = st.text_input(
            "Company Website URL", 
            placeholder="https://company.com",
            value=loaded_session['inputs']['company_url'] if loaded_session and loaded_session['inputs'].get('company_url') else ""
        )
        company_name = None
        
        # Auto-scrape button
        if company_url and company_url.startswith('http'):
            if st.button("🔍 Auto-Extract Company Info"):
                with st.spinner("Scraping company website..."):
                    scraped_info = scrape_company_info(company_url)
                    st.session_state.scraped_company_info = scraped_info
                    st.success("✅ Company info extracted!")
    
    st.markdown("---")
    
    jd_input_type = st.radio("Job Description:", ["Paste JD Text", "Provide JD Link"], horizontal=True)
    
    if jd_input_type == "Paste JD Text":
        job_title = st.text_input(
            "Job Title", 
            placeholder="e.g., Chief of Staff, Business Operations Lead",
            value=loaded_session['inputs']['job_title'] if loaded_session and loaded_session['inputs'].get('job_title') else ""
        )
        
        # Show scraped company info if available
        default_context = st.session_state.get('scraped_company_info', '')
        if not default_context and loaded_session:
            default_context = loaded_session['inputs'].get('company_context', '')
        
        company_context = st.text_area(
            "Company Context",
            height=150,
            placeholder="Describe the company: stage, industry, recent funding, key challenges...",
            value=default_context
        )
        
        job_description = st.text_area(
            "Job Description",
            height=300,
            placeholder="Paste the full job description here...",
            value=loaded_session['inputs']['job_description'] if loaded_session and loaded_session['inputs'].get('job_description') else ""
        )
        jd_link = None
    else:
        jd_link = st.text_input(
            "Job Description URL", 
            placeholder="https://company.com/careers/job-posting",
            value=loaded_session['inputs']['jd_link'] if loaded_session and loaded_session['inputs'].get('jd_link') else ""
        )
        job_title = st.text_input("Job Title", placeholder="e.g., Chief of Staff")
        
        # Auto-scrape button
        if jd_link and jd_link.startswith('http'):
            if st.button("🔍 Auto-Extract Job Description"):
                with st.spinner("Scraping job posting..."):
                    scraped_jd = scrape_job_description(jd_link)
                    st.session_state.scraped_jd = scraped_jd
                    st.success("✅ Job description extracted!")
        
        # Show scraped JD as editable job description
        default_jd_text = st.session_state.get('scraped_jd', '')
        if not default_jd_text and loaded_session:
            default_jd_text = loaded_session['inputs'].get('job_description', '')
        
        job_description = st.text_area(
            "Extracted Job Description",
            height=200,
            placeholder="Click 'Auto-Extract' above, or paste the job description here...",
            value=default_jd_text
        )
        
        default_context = ''
        if loaded_session:
            default_context = loaded_session['inputs'].get('company_context', '')
        
        company_context = st.text_area(
            "Company Context (Optional)",
            height=100,
            placeholder="Add any additional company context: stage, industry, challenges...",
            value=default_context
        )

with col2:
    st.subheader("👤 Candidate Information")
    
    candidate_name = st.text_input(
        "Candidate Name (Optional)", 
        placeholder="John Doe",
        value=loaded_session['inputs']['candidate_name'] if loaded_session and loaded_session['inputs'].get('candidate_name') else ""
    )
    
    resume_input_type = st.radio("Resume/Profile:", ["Paste Text", "Upload File"], horizontal=True)
    
    if resume_input_type == "Upload File":
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
        st.markdown('</div>', unsafe_allow_html=True)
        
        candidate_profile = None
        
        if uploaded_file is not None:
            try:
                if uploaded_file.type == "application/pdf":
                    candidate_profile = extract_text_from_pdf(uploaded_file)
                    st.success(f"✅ PDF extracted successfully! ({len(candidate_profile)} characters)")
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    candidate_profile = extract_text_from_docx(uploaded_file)
                    st.success(f"✅ DOCX extracted successfully! ({len(candidate_profile)} characters)")
                
                with st.expander("📄 Preview Extracted Text"):
                    st.text(candidate_profile[:1000] + "..." if len(candidate_profile) > 1000 else candidate_profile)
            except Exception as e:
                st.error(f"❌ Error extracting text: {str(e)}")
                candidate_profile = None
    else:
        uploaded_file = None
        candidate_profile = st.text_area(
            "Candidate Resume/Profile",
            height=450,
            placeholder="Paste candidate's resume or profile summary...",
            value=loaded_session['inputs']['candidate_profile'] if loaded_session and loaded_session['inputs'].get('candidate_profile') else ""
        )
    
    st.markdown("---")
    
    num_questions = st.slider(
        "Number of Questions", 
        min_value=3, 
        max_value=7, 
        value=loaded_session['inputs']['num_questions'] if loaded_session and loaded_session['inputs'].get('num_questions') else 5
    )

# Generate button
st.markdown("---")
generate_col1, generate_col2, generate_col3 = st.columns([1, 3, 1])

with generate_col1:
    # Demo button
    demo_button = st.button("🎯 Try Demo", use_container_width=True, help="See example with pre-filled data")

with generate_col2:
    generate_button = st.button("🚀 Generate Interview Questions", use_container_width=True, type="primary")

# Handle demo button
if demo_button:
    # Set demo data in session state
    st.session_state.demo_mode = True
    
    # Pre-fill with demo data
    company_name = "Anthropic"
    company_url = None
    company_context = "AI safety company building Claude, a helpful, harmless, and honest AI assistant. Series C funded, ~150 employees, competing with OpenAI and Google DeepMind."
    job_title = "Chief of Staff"
    job_description = """We're looking for a Chief of Staff to work directly with our CEO and executive team. This role will coordinate cross-functional initiatives, drive strategic projects, and help scale our operations as we grow.

Key Responsibilities:
- Partner with CEO on strategic planning and execution
- Coordinate across engineering, research, policy, and business teams
- Drive key company initiatives from ideation to completion
- Manage board meeting preparation and follow-up
- Build processes and systems as we scale

Requirements:
- 5+ years experience in operations, strategy, or consulting
- Strong analytical and communication skills
- Ability to context-switch across diverse topics
- Experience with AI/ML or technical products preferred
- Comfort with ambiguity and fast-paced environment"""
    jd_link = None
    candidate_name = "Alex Chen"
    candidate_profile = """MBA from Stanford GSB with 6 years experience in tech operations. 

Previously at:
- Google (Strategy & Operations, YouTube) - Led creator monetization initiatives, scaled from $1B to $3B in revenue
- McKinsey (Associate) - Technology practice, AI/ML strategy for Fortune 500 clients

Skills: Strategic planning, cross-functional coordination, data analysis, stakeholder management

Education: Stanford MBA, MIT Computer Science BS"""
    uploaded_file = None
    num_questions = 5
    
    # Trigger generation immediately
    with st.spinner("🤖 Generating demo interview questions... This may take 30-60 seconds..."):
        company_info = f"Company: {company_name}\nContext: {company_context}"
        job_info = f"Job Title: {job_title}\nDescription:\n{job_description}"
        candidate_info = f"Candidate: {candidate_name}\nProfile:\n{candidate_profile}"
        
        questions, error = generate_interview_questions(
            api_key, company_info, job_info, candidate_info, num_questions, question_type
        )
    
    if error:
        st.error(f"❌ {error}")
    elif questions:
        st.session_state.generated_questions = questions
        st.session_state.company_info = company_info
        st.session_state.job_info = job_info
        st.session_state.candidate_info = candidate_info
        st.success(f"✅ Demo generated! {len(questions)} questions created for Anthropic Chief of Staff role.")
        st.rerun()

# Generate questions
if generate_button:
    if (not job_description and not jd_link):
        st.error("⚠️ Please provide job description!")
    elif (not candidate_profile and not uploaded_file):
        st.error("⚠️ Please provide candidate information!")
    else:
        company_info = f"Company: {company_name or company_url or 'Not specified'}\n"
        if company_context:
            company_info += f"Context: {company_context}"
        
        job_info = f"Job Title: {job_title or 'See description'}\n"
        if job_description:
            job_info += f"Description:\n{job_description}"
        elif st.session_state.get('scraped_jd'):
            job_info += f"Description (extracted from {jd_link}):\n{st.session_state.scraped_jd}"
        elif jd_link:
            st.warning("⚠️ No job description text available. Click 'Auto-Extract Job Description' first, or paste the JD manually for better results.")
            job_info += f"Job Posting URL: {jd_link}"
        
        candidate_info = f"Candidate: {candidate_name or 'Anonymous'}\n"
        if candidate_profile:
            candidate_info += f"Profile:\n{candidate_profile}"
        
        # Enhanced loading state with progress messages
        progress_placeholder = st.empty()
        
        with st.spinner(""):
            # Show progressive messages
            import time
            
            progress_placeholder.markdown("""
            <div style='text-align: center; padding: 1rem;'>
                <h4 style='color: #667eea;'>🤖 Generating Your Interview Questions...</h4>
                <p style='color: #666;'>⚡ Analyzing job requirements...</p>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(1)
            
            progress_placeholder.markdown("""
            <div style='text-align: center; padding: 1rem;'>
                <h4 style='color: #667eea;'>🤖 Generating Your Interview Questions...</h4>
                <p style='color: #666;'>🎯 Customizing for candidate background...</p>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(1)
            
            progress_placeholder.markdown("""
            <div style='text-align: center; padding: 1rem;'>
                <h4 style='color: #667eea;'>🤖 Generating Your Interview Questions...</h4>
                <p style='color: #666;'>📝 Creating evaluation rubrics...</p>
                <p style='color: #999; font-size: 0.9rem;'>(30-60 seconds remaining)</p>
            </div>
            """, unsafe_allow_html=True)
            
            questions, error = generate_interview_questions(
                api_key, company_info, job_info, candidate_info, num_questions, question_type
            )
        
        progress_placeholder.empty()  # Clear the progress messages
        
        if error:
            st.error(f"❌ {error}")
        elif questions:
            # Store in session state
            st.session_state.generated_questions = questions
            st.session_state.company_info = company_info
            st.session_state.job_info = job_info
            st.session_state.candidate_info = candidate_info
            
            # Signal to Francium parent
            import json as _json
            _signal_data = _json.dumps({
                "type": "francium_signal",
                "toolId": "arkanex",
                "event": "questions_generated",
                "data": {
                    "company": company_name or company_url or "not specified",
                    "job_title": job_title or "not specified",
                    "question_type": question_type,
                    "num_questions": num_questions,
                    "has_candidate_profile": bool(candidate_profile),
                }
            })
            components.html(f"<script>window.top.postMessage({_signal_data}, '*');</script>", height=0)
            
            # Enhanced success message
            st.markdown("""
            <div style='background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); 
                        padding: 1.5rem; 
                        border-radius: 10px; 
                        border-left: 4px solid #28a745;
                        margin: 2rem 0;
                        text-align: center;'>
                <h3 style='color: #155724; margin-top: 0;'>✅ Success! Generated {} Questions</h3>
                <p style='color: #155724; margin-bottom: 0.5rem; font-size: 1.05rem;'>
                    📥 <strong>Download the PDF</strong> to share with your hiring team, or generate 
                    a new set with different parameters.
                </p>
                <p style='color: #155724; margin: 0; font-size: 0.9rem;'>
                    Scroll down to see all questions with evaluation rubrics ↓
                </p>
            </div>
            """.format(len(questions)), unsafe_allow_html=True)

# Display questions if they exist
if st.session_state.generated_questions:
    questions = st.session_state.generated_questions
    
    st.markdown("---")
    st.header("📋 Generated Interview Questions")
    
    # Primary action - PDF download (full width)
    pdf_buffer = generate_pdf(questions, st.session_state.company_info, st.session_state.job_info, question_type)
    st.download_button(
        label="🚀 Download Professional PDF",
        data=pdf_buffer,
        file_name=f"interview_questions_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True,
        type="primary"
    )
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # Secondary actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Copy to clipboard
        markdown_text = format_questions_markdown(questions, st.session_state.company_info, st.session_state.job_info)
        st.download_button(
            label="📋 Copy as Markdown",
            data=markdown_text,
            file_name=f"interview_questions_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with col2:
        # Save session as JSON
        session_json = create_session_json(
            company_name, company_url, company_context, job_title, job_description, jd_link,
            candidate_name, candidate_profile, num_questions, question_type, questions
        )
        st.download_button(
            label="💾 Save Session",
            data=session_json,
            file_name=f"arkanex_session_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        # Generate new set button
        if st.button("🔄 Generate New Set", use_container_width=True):
            st.session_state.generated_questions = None
            st.rerun()
    
    st.markdown("---")
    
    # Display each question
    for idx, q in enumerate(questions, 1):
        st.markdown(f"""
        <div class="question-card">
            <h3>Question {idx}: {q.get('title', 'Untitled')}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if q.get('scenario'):
            st.markdown("**Scenario/Context:**")
            st.write(q['scenario'])
        
        st.markdown("**Question:**")
        st.markdown(f"*{q.get('question', 'No question provided')}*")
        
        st.markdown("---")
        
        col_good, col_bad = st.columns(2)
        
        with col_good:
            st.markdown('<span class="excellent-badge">✅ EXCELLENT RESPONSES</span>', unsafe_allow_html=True)
            if q.get('rubric', {}).get('excellent'):
                for point in q['rubric']['excellent']:
                    st.markdown(f"- {point}")
        
        with col_bad:
            st.markdown('<span class="redflag-badge">🚩 RED FLAGS</span>', unsafe_allow_html=True)
            if q.get('rubric', {}).get('redFlags'):
                for flag in q['rubric']['redFlags']:
                    st.markdown(f"- {flag}")
        
        if q.get('followUps'):
            with st.expander("💡 Follow-up Questions"):
                for i, followup in enumerate(q['followUps'], 1):
                    st.markdown(f"{i}. {followup}")
        
        st.markdown("---")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p style='font-size: 1.1rem; margin-bottom: 0.5rem;'><strong>ArkaneX</strong> - Interview Intelligence Platform</p>
    <p style='margin-bottom: 0.5rem;'>Built by Karan Rajpal | Haas MBA '25 | Handshake AI</p>
    <p style='font-size: 0.9rem;'>
        📧 karan.rajpal@berkeley.edu | 
        💼 <a href='https://www.linkedin.com/in/krajpal/' target='_blank' style='color: #667eea;'>LinkedIn</a> |
        🌐 <a href='https://github.com/AAP67' target='_blank' style='color: #667eea;'>Portfolio</a>
    </p>
    <p style='font-size: 0.85rem; margin-top: 1rem; color: #999;'>© 2026 | Built with Streamlit & Claude AI</p>
</div>
""", unsafe_allow_html=True)
