# PDF Buddy AI

A modern web application that processes documents (PDF, DOCX, TXT) using advanced AI (Groq LLM via LangChain) to generate multiple-choice questions (MCQs) or comprehensive summaries.

![PDF Buddy AI Dashboard](image.png)
_Main dashboard interface of PDF Buddy AI_

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the App](#running-the-app)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Features in Detail](#features-in-detail)
  - [MCQ Generation](#mcq-generation)
  - [Document Summarization](#document-summarization)
  - [Interactive Chat](#interactive-chat)
- [Credits](#credits)
- [License](#license)

## Features

- Upload PDF, DOCX, or TXT files
- Choose between two operations:
  - Generate multiple-choice questions (MCQs)
  - Create comprehensive document summaries
- Interactive chat interface to ask questions about your document
- Download generated content as .txt or .pdf
- Beautiful, modern UI with glassmorphism and animations
- Loading animations for document processing
- Secure file handling

![File Upload Interface](image.png)
_User-friendly file upload interface_

## Getting Started

### Prerequisites

- Python 3.8+
- A Groq API key (for LLM-powered document processing)

### Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

- Set your Groq API key in `app.py` (for production, use environment variables for security).

### Running the App

```bash
python app.py
```

- Visit [http://localhost:5000](http://localhost:5000) in your browser.

## Usage

1. Upload a document (PDF, DOCX, or TXT).
2. Choose your desired operation:
   - Generate MCQs: Specify the number of questions you want
   - Generate Summary: Get a comprehensive summary of the document
3. Click "Process Document" and wait for the results.
4. View the generated content and download it as .txt or .pdf.
5. Use the chat interface to ask questions about your document's content.

## Project Structure

```
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
├── templates/
│   ├── index.html
│   └── results.html
├── uploads/
├── results/
└── ...
```

## Features in Detail

### MCQ Generation

![MCQ Generation](image.png)
_Example of generated multiple-choice questions_

- Generate multiple-choice questions from your document
- Specify the number of questions (1-20)
- Questions are designed to test understanding of key concepts

### Document Summarization

![Document Summary](image.png)
_Example of a generated document summary_

- Create comprehensive summaries of your documents
- Focus on main points and key information
- Maintain context and important details

### Interactive Chat

![Chat Interface](image.png)
_Interactive chat interface for document queries_

- Ask questions about your document's content
- Get instant AI-powered responses
- Continue the conversation to explore topics in depth

## Credits

- [Flask](https://flask.palletsprojects.com/)
- [LangChain](https://python.langchain.com/)
- [Groq LLM](https://groq.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Animate.css](https://animate.style/)
- [FPDF](https://pyfpdf.github.io/)
- [pdfplumber](https://github.com/jsvine/pdfplumber)
- [python-docx](https://python-docx.readthedocs.io/)
