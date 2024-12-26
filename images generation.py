from PIL import Image, ImageFilter
import os
import shutil
import random
import numpy as np

# Папка с исходными изображениями логотипов
input_folder = "Образцы"
output_folder = "..\\Датасет логотипов авто 28x28 px\\Тестовые"

# Очистка папки перед началом генерации, если она не пустая
if os.path.exists(output_folder):
    # Удаляем все файлы и подпапки в папке
    for filename in os.listdir(output_folder):
        file_path = os.path.join(output_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Удаляем файл или символическую ссылку
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Удаляем подпапку и её содержимое
        except Exception as e:
            print(f"Ошибка при удалении {file_path}: {e}")
else:
    os.makedirs(output_folder)  # Создаем папку, если она не существует

# Параметры генерации
num_variations = 10         # Количество вариаций для каждого логотипа
rotation_range = (-30, 30)  # Пределы поворота
translation_range = (-5, 5) # Смещение
scaling_range = (0.8, 1.2)  # Масштабирование
noise_intensity = 30        # Интенсивность шума
blur_radius = 1             # Радиус размытия
perspective_range = (-7, 7) # Изменение перспективы
light_augmentation_probability = 0.85  # Вероятность применения лёгкой аугментации

def apply_light_augmentations(image, augmentations_type):
    """Применение не более двух лёгких аугментаций."""
    augmentations = []

    # Лёгкие аугментации
    if random.random() < 0.8:  # 80% шанс
        augmentations.append(lambda img: rotate_image(img, augmentations_type))     # Поворот
    if random.random() < 0.7:  # 70% шанс
        augmentations.append(lambda img: translate_image(img, augmentations_type))  # Смещение
    if random.random() < 0.6:  # 60% шанс
        augmentations.append(lambda img: scale_image(img, augmentations_type))      # Масштабирование

    # Применяем не более двух аугментаций
    if augmentations:
        for augmentation in random.sample(augmentations, k=min(len(augmentations), 2)):
            image = augmentation(image)

    # Если ни одна аугментация не была выбрана, применяем случайную лёгкую аугментацию
    if not augmentations:
        fallback_augmentation = random.choice([
            lambda img: rotate_image(img, augmentations_type),
            lambda img: translate_image(img, augmentations_type),
            lambda img: scale_image(img, augmentations_type)
        ])
        image = fallback_augmentation(image)

    return image

def apply_aggressive_augmentations(image, augmentations_type):
    """Применение не более двух агрессивных аугментаций."""
    augmentations = []

    # Агрессивные аугментации
    if random.random() < 0.5:  # 50% шанс
        augmentations.append(lambda img: add_noise(img, augmentations_type))    # Шум
    if random.random() < 0.5:  # 50% шанс
        augmentations.append(lambda img: blur_image(img, augmentations_type))   # Размытие
    if random.random() < 0.4:  # 40% шанс
        augmentations.append(lambda img: change_perspective(img, augmentations_type)) # Изменение перспективы

    # Применяем не более двух аугментаций
    if augmentations:
        for augmentation in random.sample(augmentations, k=min(len(augmentations), 2)):
            image = augmentation(image)

    # Если ни одна аугментация не была выбрана, применяем случайную агрессивную аугментацию
    if not augmentations:
        fallback_augmentation = random.choice([
            lambda img: add_noise(img, augmentations_type),
            lambda img: blur_image(img, augmentations_type),
            lambda img: change_perspective(img, augmentations_type)
        ])
        image = fallback_augmentation(image)

    return image

def rotate_image(image, augmentations_type):
    """Поворот изображения на случайный угол."""
    angle = random.uniform(*rotation_range)
    augmentations_type.append("rotate")
    return image.rotate(angle, resample=Image.BICUBIC, fillcolor=255)

def translate_image(image, augmentations_type):
    """Смещение изображения."""
    dx = random.randint(*translation_range)
    dy = random.randint(*translation_range)
    # Проверка, чтобы смещение не выходило за пределы изображения
    dx = max(0, min(dx, image.size[0] - 1))
    dy = max(0, min(dy, image.size[1] - 1))
    translated = Image.new("L", image.size, (255))
    translated.paste(image, (dx, dy))
    augmentations_type.append("translate")
    return translated

def scale_image(image, augmentations_type):
    """Масштабирование изображения с центрированием."""
    scale = random.uniform(*scaling_range)
    new_width = int(image.size[0] * scale)
    new_height = int(image.size[1] * scale)
    # Масштабируем изображение
    scaled = image.resize((new_width, new_height), resample=Image.BICUBIC)
    # Создаем новый холст размером 28x28 с белым фоном
    centered = Image.new("L", (28, 28), 255)
    # Вычисляем позицию для вставки масштабированного изображения
    left = (28 - new_width) // 2
    top = (28 - new_height) // 2
    # Вставляем масштабированное изображение в центр холста
    centered.paste(scaled, (left, top))
    augmentations_type.append("scale")
    return centered

def add_noise(image, augmentations_type):
    """Добавление шума."""
    array = np.array(image)
    noise = np.random.randint(-noise_intensity, noise_intensity, array.shape, dtype="int16")
    array = np.clip(array + noise, 0, 255).astype("uint8")
    augmentations_type.append("noise")
    return Image.fromarray(array)

def blur_image(image, augmentations_type):
    """Размытие изображения с случайным радиусом."""
    radius = random.uniform(0, blur_radius)
    augmentations_type.append("blur")
    return image.filter(ImageFilter.GaussianBlur(radius=radius))

def change_perspective(image, augmentations_type):
    """Изменение перспективы."""
    coeffs = [1, random.uniform(*perspective_range) / 100, 0,
              random.uniform(*perspective_range) / 100, 1, 0, 0, 0]
    augmentations_type.append("perspective")
    return image.transform(image.size, Image.PERSPECTIVE, coeffs, resample=Image.BICUBIC, fillcolor=255)

def generate_variations(image, num_variations, output_path_base):
    for i in range(num_variations):
        augmentations_type = []  # Очищаем список перед каждой аугментацией

        # Случайно выбираем тип аугментации
        if random.random() < light_augmentation_probability:
            augmented_image = apply_light_augmentations(image, augmentations_type)
        else:
            augmented_image = apply_aggressive_augmentations(image, augmentations_type)

        # Сохранение результата
        variation_path = f"{output_path_base}_variation_{i+1}_{'_'.join(augmentations_type)}.png"
        augmented_image.save(variation_path)

# Обработка всех логотипов
for file_name in os.listdir(input_folder):
    try:
        if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
            brand = os.path.splitext(file_name)[0]
            input_path = os.path.join(input_folder, file_name)

            # Открываем изображение
            image = Image.open(input_path).convert("L")

            # Центрирование и создание вариаций
            centered = image.resize((28, 28))
            output_path_base = os.path.join(output_folder, brand)

            generate_variations(centered, num_variations, output_path_base)
            print(f"-вариации для {brand} созданы.")

    except Exception as e:
        print(f"Ошибка при обработке файла {file_name}: {e}")

print("Создание изображений завершено!")
