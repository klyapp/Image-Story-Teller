from flask import Flask, request, render_template, jsonify, send_from_directory
import cv2 # type: ignore
import random
import requests # type: ignore
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp'  # Папка для временного хранения файлов

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Проверяет, есть ли файл в запросе
        if 'video' not in request.files:
            return "Файл не найден", 400
        file = request.files['video']
        if file.filename == '':
            return "Файл не выбран", 400
        if file:
            # Сохраняет видео файл
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            # Извлекает случайный кадр
            cap = cv2.VideoCapture(filepath)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            random_frame = random.randint(0, frame_count - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame)
            success, frame = cap.read()
            cap.release()

            if success:
                # Сохраняет кадр во временный файл
                temp_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'frame.jpg')
                cv2.imwrite(temp_image_path, frame)

                # Отправляет изображение на модель Hugging Face
                with open(temp_image_path, 'rb') as f:
                    response = requests.post(
                        'https://huggingface.co/spaces/tonyassi/image-story-teller',
                        files={'file': f}
                    )

                if response.status_code == 200:
                    # Возвращает результат пользователю
                    return jsonify(response.json())
                else:
                    return "Ошибка при запросе к API модели", 500
            else:
                return "Ошибка при извлечении кадра из видео", 500
        else:
            return "Ошибка загрузки файла", 400
    else:
        # Если GET запрос, показывать форму для загрузки видео
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)