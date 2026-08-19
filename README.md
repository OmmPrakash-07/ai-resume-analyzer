# AI Resume Analyzer

[![Live App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-resume-analyzer-ommprakash07.streamlit.app)

An AI-powered resume analyzer that compares a resume with a job description, estimates job compatibility, checks ATS readability, identifies skill gaps, and generates evidence-based Gemini recommendations.

## Live Demo

**Try the application:**  
https://ai-resume-analyzer-ommprakash07.streamlit.app

## Features

- Upload PDF and DOCX resumes
- Extract structured resume text
- Compare a resume with a job description
- Estimate overall job-match percentage
- Detect matched and missing technical skills
- Detect matched and missing soft skills
- Calculate text similarity
- Check ATS-readable resume sections
- Evaluate contact details, dates, length and file format
- Generate an ATS-friendly professional summary
- Improve resume bullets without inventing experience
- Map job requirements to resume evidence
- Suggest relevant interview-preparation topics
- Redact detected personal information before Gemini analysis
- Require user consent before sending anonymized content to Gemini
- Handle Gemini free-tier rate limits with a friendly message

## Technology Stack

- Python 3.13
- Streamlit
- Google Gemini API
- Google Gen AI Python SDK
- PyMuPDF
- python-docx
- scikit-learn
- RapidFuzz
- Pydantic
- python-dotenv

## How It Works

1. The user uploads a PDF or DOCX resume.
2. The application extracts readable text from the document.
3. The local analyzers evaluate:
   - Technical skills
   - Soft skills
   - Text similarity
   - Resume structure
   - ATS readability
4. The user may optionally consent to Gemini analysis.
5. Detected personal information is redacted.
6. The anonymized resume and job description are sent to Gemini.
7. Gemini returns structured recommendations validated with Pydantic.

## Project Structure

```text
ai-resume-analyzer/
├── analyzers/
│   ├── __init__.py
│   ├── ats_analyzer.py
│   └── match_analyzer.py
├── parsers/
│   ├── __init__.py
│   └── resume_parser.py
├── services/
│   ├── __init__.py
│   ├── gemini_service.py
│   └── privacy.py
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Local Installation

Clone the repository:

```powershell
git clone https://github.com/OmmPrakash-07/ai-resume-analyzer.git
cd ai-resume-analyzer
```

Create and activate a virtual environment:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Run the application:

```powershell
python -m streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## Privacy and Security

- The Gemini API key is stored outside the source code.
- The `.env` file is excluded from Git.
- Gemini analysis is optional and requires user consent.
- The application attempts to redact names, email addresses, phone numbers, URLs, addresses and sensitive identifiers.
- Gemini requests use stateless processing with `store=False`.
- Resume files are processed in memory and are not intentionally saved by the application.

Users should still avoid uploading highly sensitive documents unless they understand and accept the external AI provider’s data-processing terms.

## ATS Disclaimer

The ATS score is a transparent estimate based on resume text, structure, standard sections, skills and job-description similarity.

It does not guarantee selection, interview calls, employment, or identical results from every commercial ATS platform.

## Current Limitations

- Scanned or image-only PDFs require OCR and may not be readable.
- Complex multi-column resumes may produce imperfect text extraction.
- Gemini free-tier requests are subject to rate and quota limits.
- Keyword matches do not prove real-world skill proficiency.
- AI recommendations must be reviewed before being added to a resume.

## Future Improvements

- OCR support for scanned resumes
- Downloadable analysis report
- ATS-friendly resume builder
- Resume comparison history
- Additional file formats
- Role-specific scoring
- Automated testing
- User authentication
- Database-backed analysis history

## Author

Developed by [OmmPrakash-07](https://github.com/OmmPrakash-07).