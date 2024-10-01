#img3.akspic.ru-nacionalnyj_park_glejsher-ozero_tu_medisin-lavina_ozero-gora_rejnoldsa-ozero_makdonald-7680x4320.jpg

from flask import Flask, request, send_file, jsonify
import os

app = Flask(__name__)

# Директория для хранения загруженных файлов
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/api/upload', methods=['POST'])
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


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_file(file_path)


if __name__ == '__main__':
    app.run(debug=True)
