import os
import csv
from PIL import Image
import numpy as np
import random

input_folder = "..\\Датасет логотипов авто 28x28 px\\Train"
output_csv = "..\\Датасет логотипов авто 28x28 px\\car_logos_train.csv"

# Функция для получения ключа из названия файла
def get_key_from_filename(filename):
    return filename.split('_')[0]

data_rows = [] # Список для хранения всех данных

# Обрабатываем каждое изображение в папке
for filename in os.listdir(input_folder):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        # Получаем ключ из названия файла
        label = get_key_from_filename(filename)

        # Открываем изображение и преобразуем его в массив пикселей
        image_path = os.path.join(input_folder, filename)
        image = Image.open(image_path).convert("L")
        pixels = np.array(image).flatten()  # Преобразуем в одномерный массив

        pixels = 255 - pixels   # Инвертируем значения пикселей
        data_rows.append([label] + list(pixels))

# Перемешиваем строки случайным образом
random.shuffle(data_rows)

# Открываем CSV-файл для записи
with open(output_csv, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data_rows)
print(f"CSV-файл успешно создан: {output_csv}")