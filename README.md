# Resumaster: AI-Powered Resume Customization Tool

## Overview

Resumaster is an intelligent web application that leverages Anthropic's Claude AI to help job seekers customize their resumes for specific job descriptions. By analyzing your existing resume, job requirements, and optional additional context, the tool generates a tailored resume that highlights your most relevant skills and experiences.

## Features

- 📄 Resume Upload: Easily upload your existing resume
- 📋 Job Description Input: Provide the job description you're targeting
- 🔍 AI-Powered Customization: Intelligent resume tailoring using Claude AI
- 🌟 Optional Enhancements:
  - GitHub Profile Inclusion
  - Personal Writeup Inclusion

## How It Works

1. **Upload Documents**
   - Resume file
   - Job description file
   - Optional: GitHub profile information
   - Optional: Personal writeup

2. **AI Customization Process**
   - Analyze job requirements
   - Match skills and experiences
   - Preserve factual accuracy
   - Maintain original resume structure
   - Highlight relevant achievements

3. **Tailored Output**
   - Customized resume optimized for the specific job
   - Concise and impactful presentation

## Technology Stack

- **Backend**: FastAPI
- **AI Service**: Anthropic Claude (Claude-3-5-Sonnet)
- **Logging**: Logfire (Observability Platform)
- **Environment**: Python 3.11+

### About Logfire

Logfire is an advanced observability platform built by the Pydantic team. Key features include:
- Built on OpenTelemetry
- Easy-to-use instrumentation
- Detailed performance analytics
- Comprehensive application monitoring

### Setting Up Logfire

To enable logging and observability using Logfire, follow these steps:

1. **Create a Logfire Account**
   - Visit [Logfire's official website](https://logfire.pydantic.dev/)
   - Sign up for an account
   - Create a new project
   - Obtain your **write token** from the Logfire dashboard

2. **Configure Logfire in Resumaster**
   - Add your write token to the `.env` file:
     ```plaintext
     LOGFIRE_WRITE_TOKEN=your_write_token_here
     ```
   - Ensure Logfire is properly initialized in the application

3. **Verify Logging**
   - Run the application and check Logfire’s dashboard to monitor logs and analytics

## Prerequisites

- Python 3.11+
- Anthropic API Key
- Astral's `uv` (Universal Python Package Manager)
- Logfire account (for logging, optional but recommended)

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/resumaster.git
cd resumaster
```

2. Create a virtual environment
```bash
uv venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

3. Install dependencies
```bash
uv sync
```

4. Set up environment variables
   - Create a `.env` file
   - Add your Anthropic API key: `ANTHROPIC_API_KEY=your_api_key_here`

## Running the Application

```bash
uvicorn src.main:app --reload
```

Navigate to `http://localhost:8000` in your web browser.

## Configuration

- Customize the prompt template in `src/prompt.md`
- Adjust AI model parameters in `src/services/anthropic.py`

## Security and Privacy

- No resume data is stored permanently
- API keys are managed through environment variables
- Sensitive information is processed securely

## Limitations

- Requires a valid Anthropic API key
- AI customization is a suggestion, not a guarantee
- Review the results carefully

## Contributing

Contributions are welcome! Please read the contributing guidelines before getting started.

## Disclaimer

Resumaster is an AI-assisted tool. Always review and validate the generated resume to ensure accuracy and personal representation.

