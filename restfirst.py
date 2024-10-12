from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

# Директория для хранения загруженных файлов
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')  # Отображение HTML-страницы

@app.route('/api/file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Сохраняем файл
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    return jsonify({"message": f"File {file.filename} uploaded successfully"}), 200

if __name__ == '__main__':
    app.run(debug=False)
