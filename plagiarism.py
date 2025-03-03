import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
import docx
from collections import Counter
import re

# Load SBERT Model for semantic similarity
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to extract text from a Word document
def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = " ".join([para.text for para in doc.paragraphs])
    return text

# Function to extract keywords from text
def extract_keywords(text, num_keywords=5):
    words = re.findall(r'\b\w+\b', text.lower())
    common_words = {"the", "and", "of", "in", "to", "a", "is", "for", "on", "with", "as", "this"}  # Stopwords
    filtered_words = [word for word in words if word not in common_words]
    most_common = Counter(filtered_words).most_common(num_keywords)
    return [word[0] for word in most_common]

# Function to fetch research papers from arXiv
def search_arxiv(query, max_results=5):
    base_url = "http://export.arxiv.org/api/query?search_query="
    url = f"{base_url}{query}&start=0&max_results={max_results}"

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "xml")
        entries = soup.find_all("entry")

        papers = []
        for entry in entries:
            title = entry.title.text
            summary = entry.summary.text
            link = entry.id.text
            papers.append({"title": title, "summary": summary, "link": link})

        return papers
    else:
        return []

# Function to compare document text with research papers using SBERT
def check_plagiarism(file_path):
    # Extract text from Word document
    document_text = extract_text_from_docx(file_path)
    
    # Extract keywords dynamically
    search_query = " ".join(extract_keywords(document_text))
    print(f"Using search query: {search_query}")  # Debugging
    
    # Fetch research papers from arXiv
    papers = search_arxiv(search_query)

    # Convert document text to embedding
    doc_embedding = model.encode(document_text, convert_to_tensor=True)

    results = []
    
    # Compare with each research paper summary
    for paper in papers:
        paper_embedding = model.encode(paper['summary'], convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(doc_embedding, paper_embedding).item()

        results.append({
            "title": paper['title'],
            "link": paper['link'],
            "similarity": round(similarity * 100, 2)  # Convert to percentage
        })

    # Sort by highest similarity
    results.sort(key=lambda x: x["similarity"], reverse=True)

    return results

# Example usage
file_path = "uploads/klu Research Journal Management System.docx"  # Replace with your document
plagiarism_results = check_plagiarism(file_path)

print("\n🔍 Plagiarism Check Results:")
for i, result in enumerate(plagiarism_results):
    print(f"{i+1}. {result['title']}\n   Similarity: {result['similarity']}%\n   Link: {result['link']}\n")
