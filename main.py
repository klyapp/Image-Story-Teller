from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import cv2
import random
import os
import tempfile
import gradio as gr
import numpy as np

app = Flask(__name__)

# Путь к директории, где будут сохраняться загруженные файлы
upload_folder = 'D:\\image_story_teller_web'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Проверяем, есть ли файл в запросе
        if 'video' not in request.files:
            return "Файл не найден", 400
        file = request.files['video']
        if file.filename == '':
            return "Файл не выбран", 400
        if file:
            # Создаем безопасное имя файла и сохраняем его в указанной директории
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            # Извлекаем случайный кадр из видео
            cap = cv2.VideoCapture(file_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            random_frame = random.randint(0, frame_count - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame)
            success, frame = cap.read()
            cap.release()  # Убедитесь, что ресурсы освобождены

            if success:
                # Создаем временный файл для кадра
                temp_image_path = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False).name
                cv2.imwrite(temp_image_path, frame)

                # Здесь ваш код для обработки изображения

                # Попытка удалить временные файлы
                try:
                    os.unlink(temp_image_path)
                except PermissionError:
                    # Если файл все еще используется, попробуйте удалить его позже
                    pass
                os.unlink(file_path)

                return jsonify({"message": "Изображение успешно обработано"})
            else:
                os.unlink(file_path)
                return jsonify({"error": "Ошибка при извлечении кадра из видео"}), 500
        else:
            return jsonify({"error": "Ошибка загрузки файла"}), 400
    else:
        # Если GET запрос, показываем форму для загрузки файла
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
