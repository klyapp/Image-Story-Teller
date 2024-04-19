from flask import Flask, request, render_template, jsonify
import cv2  # type: ignore
import random
import os
import tempfile
from werkzeug.utils import secure_filename
from gradio_client import Client

app = Flask(__name__)

# Создает экземпляр клиента Gradio, указывая URL к Hugging Face Space
gradio_client = Client("https://tonyassi-image-story-teller.hf.space/--replicas/liw84/")

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
            # Создает временный файл для видео
            temp_video = tempfile.NamedTemporaryFile(delete=False)
            file.save(temp_video.name)
            # Извлекает случайный кадр
            cap = cv2.VideoCapture(temp_video.name)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            random_frame = random.randint(0, frame_count - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame)
            success, frame = cap.read()
            cap.release()

            if success:
                # Создает временный файл для кадра
                temp_image = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                cv2.imwrite(temp_image.name, frame)

                # Отправляет изображение на модель Hugging Face с помощью клиента Gradio
                with open(temp_image.name, 'rb') as f:
                    result = gradio_client.predict(
                        files={"file": f},
                        api_name="/predict"
                    )

                # Удаляет временные файлы
                os.unlink(temp_video.name)
                os.unlink(temp_image.name)

                # Возвращает результат пользователю
                return jsonify(result)
            else:
                # Удаляет временный файл видео, если не удалось извлечь кадр
                os.unlink(temp_video.name)
                return "Ошибка при извлечении кадра из видео", 500
        else:
            return "Ошибка загрузки файла", 400
    else:
        # Если GET запрос, показывать форму для загрузки видео
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
