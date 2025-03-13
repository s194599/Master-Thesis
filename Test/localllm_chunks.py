import fitz  # PyMuPDF for PDF processing
import requests
import json
import math

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path, max_pages=10):
    doc = fitz.open(pdf_path)
    text = ""

    for page_num in range(min(len(doc), max_pages)):  # Limit to 10 pages
        text += doc[page_num].get_text("text") + "\n\n"

    return text.strip()

# Function to split text into equal chunks
def split_text(text, num_chunks):
    chunk_size = math.ceil(len(text) / num_chunks)
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# Function to generate quiz using Ollama
def generate_quiz(pdf_text, num_questions=6, model="mistral"):  # Change model if needed
    OLLAMA_API = "http://localhost:11434/api/generate"

    # Determine the number of prompts (each should generate 2 questions)
    num_prompts = num_questions // 2

    # Split the text into corresponding chunks
    text_chunks = split_text(pdf_text, num_prompts)

    quiz = ""  # Store all generated questions

    for i, chunk in enumerate(text_chunks):
        quiz_format = f"""
        1. [Spørgsmål 1]  
            A) [Mulighed 1]  
            B) [Mulighed 2]  
            C) [Mulighed 3]  
            D) [Mulighed 4]  
        Korrekt svar: [Korrekt bogstav]

        2. [Spørgsmål 2]  
            A) [Mulighed 1]  
            B) [Mulighed 2]  
            C) [Mulighed 3]  
            D) [Mulighed 4]  
        Korrekt svar: [Korrekt bogstav]
        """

        prompt = f"""
        Du er en quiz-generator. Baseret på følgende danske tekst skal du lave en **2-spørgsmåls multiple-choice quiz**.  
        Brug **kun** det præcise format herunder.  

        **Tekst:**  
        {chunk}  

        **Format:**  
        {quiz_format}

        Svar **kun** med quizzen. Giv **ingen** forklaringer, opsummeringer eller ekstra tekst. Skriv quizzen på dansk.
        """

        payload = {"model": model, "prompt": prompt, "stream": False}
        response = requests.post(OLLAMA_API, json=payload)

        if response.status_code == 200:
            quiz += response.json().get("response", "") + "\n\n"
        else:
            quiz += f"Error: {response.status_code}\n{response.text}\n\n"

    return quiz.strip()


# Main function
def main():
    num_questions = 6  # Should be an even number
    pdf_files = [
        "Files/romantikken.pdf", 
        "Files/kompendium-om-1800-tallet.pdf",
    ]

    print("Extracting text from PDF...")
    
    # Extract and combine text from all PDFs
    all_text = ""
    for pdf in pdf_files:
        print(f"Processing: {pdf}")
        all_text += extract_text_from_pdf(pdf) + "\n\n"

    if len(all_text) > 128000:  # 🔹 Limit text length for token constraints
        print("Warning: Combined PDF text is too long. Using only the first 128,000 characters.")
        all_text = all_text[:128000]

    print("\nGenerating quiz...\n")
    quiz = generate_quiz(all_text, num_questions, "mistral")
    
    print(quiz)

# Run the script
if __name__ == "__main__":
    main()
