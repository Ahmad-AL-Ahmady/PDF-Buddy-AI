import os
from flask import Flask, render_template, request, send_file, jsonify
import pdfplumber
import docx
from werkzeug.utils import secure_filename
from fpdf import FPDF
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import markdown  # Added for markdown to HTML conversion
from dotenv import load_dotenv

# Flask app setup
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['RESULTS_FOLDER'] = 'results/'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'txt', 'docx'}

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Load environment variables from .env file
load_dotenv()

# Initialize LangChain LLM
llm = ChatGroq(
    api_key=os.environ.get("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",  # Updated model name
    temperature=0.0
)

# LangChain prompt templates
mcq_prompt = PromptTemplate(
    input_variables=["context", "num_questions"],
    template="""
You are an AI assistant helping the user generate multiple-choice questions (MCQs) from the text below:

Text:
{context}

Generate {num_questions} MCQs. Each should include:
- A clear question
- Four answer options labeled A, B, C, and D
- The correct answer clearly indicated at the end

Format:
## MCQ
Question: [question]
- A) [option A]
- B) [option B]
- C) [option C]
- D) [option D]
Correct Answer: [correct option]
"""
)

summary_prompt = PromptTemplate(
    input_variables=["context"],
    template="""
You are an AI assistant helping to create a comprehensive summary of the following text:

Text:
{context}

Please provide a detailed summary that includes:
1. Main points and key ideas
2. Important details and supporting information
3. Any significant conclusions or findings

Format the summary in a clear, organized manner with appropriate headings and bullet points where necessary.
"""
)

chat_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are an AI assistant helping the user understand the content of their document. Use the following text as context to answer their question:

Context:
{context}

User Question: {question}

Please provide a clear, detailed, and accurate response based on the context provided. If the question cannot be answered using the given context, please say so.
"""
)

mcq_chain = LLMChain(llm=llm, prompt=mcq_prompt)
summary_chain = LLMChain(llm=llm, prompt=summary_prompt)
chat_chain = LLMChain(llm=llm, prompt=chat_prompt)

# Store document content for chat context
document_contents = {}

# File validation
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Text extraction
def extract_text_from_file(file_path):
    ext = file_path.rsplit('.', 1)[1].lower()
    if ext == 'pdf':
        with pdfplumber.open(file_path) as pdf:
            return ''.join([page.extract_text() for page in pdf.pages if page.extract_text()])
    elif ext == 'docx':
        doc = docx.Document(file_path)
        return ' '.join([para.text for para in doc.paragraphs])
    elif ext == 'txt':
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    return None

# MCQ generation
def generate_mcqs_with_langchain(text, num_questions):
    response = mcq_chain.run({"context": text, "num_questions": num_questions})
    return response.strip()

# Generate summary
def generate_summary_with_langchain(text):
    response = summary_chain.run({"context": text})
    return response.strip()

# Save MCQs to text file
def save_mcqs_to_file(mcqs, filename):
    path = os.path.join(app.config['RESULTS_FOLDER'], filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(mcqs)
    return path

# Save summary to text file
def save_summary_to_file(summary, filename):
    path = os.path.join(app.config['RESULTS_FOLDER'], filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(summary)
    return path

# Save MCQs to PDF
def create_pdf(mcqs, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for mcq in mcqs.split("## MCQ"):
        if mcq.strip():
            pdf.multi_cell(0, 10, mcq.strip())
            pdf.ln(5)

    path = os.path.join(app.config['RESULTS_FOLDER'], filename)
    pdf.output(path)
    return path

# Save summary to PDF
def create_summary_pdf(summary, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, summary)
    path = os.path.join(app.config['RESULTS_FOLDER'], filename)
    pdf.output(path)
    return path

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    if 'file' not in request.files:
        return "No file uploaded."

    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        text = extract_text_from_file(file_path)
        if text:
            # Store the text content for chat context
            document_contents[filename] = text
            
            operation_type = request.form.get('operation_type', 'mcq')
            base_name = filename.rsplit('.', 1)[0]

            if operation_type == 'mcq':
                num_questions = int(request.form['num_questions'])
                result = generate_mcqs_with_langchain(text, num_questions)
                result_html = markdown.markdown(result, extensions=['extra'])
                txt_file = f"generated_mcqs_{base_name}.txt"
                pdf_file = f"generated_mcqs_{base_name}.pdf"
                save_mcqs_to_file(result, txt_file)
                create_pdf(result, pdf_file)
            else:  # summarization
                result = generate_summary_with_langchain(text)
                result_html = markdown.markdown(result, extensions=['extra'])
                txt_file = f"summary_{base_name}.txt"
                pdf_file = f"summary_{base_name}.pdf"
                save_summary_to_file(result, txt_file)
                create_summary_pdf(result, pdf_file)

            return render_template('results.html', 
                                content=result_html, 
                                txt_filename=txt_file, 
                                pdf_filename=pdf_file,
                                operation_type=operation_type,
                                filename=filename)

    return "Invalid file format or upload error."

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    filename = data.get('filename')
    question = data.get('question')
    
    if not filename or not question:
        return jsonify({'error': 'Missing filename or question'}), 400
    
    if filename not in document_contents:
        return jsonify({'error': 'Document context not found'}), 404
    
    # Generate response using the chat chain
    response = chat_chain.run({
        "context": document_contents[filename],
        "question": question
    })
    
    # Convert markdown to HTML
    response_html = markdown.markdown(response, extensions=['extra'])
    
    return jsonify({
        'response': response_html
    })

@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(app.config['RESULTS_FOLDER'], filename)
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)