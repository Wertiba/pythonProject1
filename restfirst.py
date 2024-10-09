from flask import Flask, send_file, jsonify
import os
import zipfile
import io

app = Flask(__name__)

# Папка для загрузки файлов
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/api/download_all', methods=['POST'])
def download_all_files():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                zip_file.write(file_path, arcname=filename)

    zip_buffer.seek(0)  # Вернуться в начало буфера

    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name='all_files.zip',
        mimetype='application/zip'
    )

if __name__ == '__main__':
    app.run(debug=True)
