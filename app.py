from flask import Flask, request, jsonify, render_template
from plagiarism import check_plagiarism  # Import function from plagiarism.py
import os

app = Flask(__name__)


@app.route('/')
def home():
    return "Plagiarism Checker is running!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Get port from environment variable
    app.run(host='0.0.0.0', port=port, debug=False)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Route to serve the frontend page
@app.route("/")
def index():
    return render_template("index.html")  # Make sure you have an index.html in templates folder

# Route to handle file upload and plagiarism check
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"})

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)  # Save file to uploads folder

    search_query = " ".join(file.filename.split())  # Generate search query from filename
    results = check_plagiarism(file_path, search_query)

    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(debug=True)
