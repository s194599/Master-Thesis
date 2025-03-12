import fitz  # PyMuPDF for PDF processing
import requests
import json

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path, max_pages=10):
    doc = fitz.open(pdf_path)
    text = ""

    for page_num in range(min(len(doc), max_pages)):  # Limit to 10 pages
        text += doc[page_num].get_text("text") + "\n\n"

    return text.strip()

# Function to generate quiz using Ollama
def generate_quiz(pdf_text, model="llama3.2"):  # Change model if needed
    OLLAMA_API = "http://localhost:11434/api/generate"

    prompt = f"""
    You are a quiz generator. Based on the following text, create a 2-question quiz 
    with multiple-choice answers. Label the correct answer.

    Text:
    {pdf_text}

    Output format:
    1. Question?
        A) Option 1
        B) Option 2
        C) Option 3
        D) Option 4
    Correct answer: B
    """

    payload = {"model": model, "prompt": prompt, "stream": False}

    response = requests.post(OLLAMA_API, json=payload)

    if response.status_code == 200:
        return response.json().get("response", "No response received.")
    else:
        return f"Error: {response.status_code}\n{response.text}"

# Main function
def main():
    pdf_path = "Project Plan.pdf"  # 🔹 Replace with your PDF file path
    print("Extracting text from PDF...")
    
    pdf_text = extract_text_from_pdf(pdf_path)

    if len(pdf_text) > 10000:  # 🔹 Limit text length for token constraints
        print("Warning: PDF is too long. Using only the first 10,000 characters.")
        pdf_text = pdf_text[:10000]

    print("\nGenerating quiz...\n")
    quiz = generate_quiz(pdf_text)
    
    print(quiz)

# Run the script
if __name__ == "__main__":
    main()
