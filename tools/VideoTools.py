import math

from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from moviepy.video.VideoClip import VideoClip
from numpy.random import randint


def make_video(input_path: str, duration: float) -> VideoClip:
    """
    Создает видео заданной длины из GIF, видео или изображения.
    Зацикливает GIF или видео до указанной длины.
    Растягивает изображение до указанной длины.

    :param input_path: Путь к входному файлу (GIF, видео или изображение).
    :param duration: Длительность выходного видео в секундах.
    :return: Объект VideoClip.
    """

    # Определение расширения файла
    ext = input_path.split('.')[-1].lower()
    video_extensions = ['gif', 'mp4', 'mov', 'avi', 'mkv']
    image_extensions = ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp']

    if ext in video_extensions:
        try:
            base_clip = VideoFileClip(input_path, has_mask=False)
            final_clip = loop_video_clip(base_clip, duration)
            return final_clip
        except Exception as e:
            raise ValueError(f"Ошибка при обработке видео/GIF: {e}")
    elif ext in image_extensions:
        try:
            base_clip = ImageClip(input_path)
            final_clip = base_clip.set_duration(duration)
            return final_clip
        except Exception as e:
            raise ValueError(f"Ошибка при обработке изображения: {e}")
    else:
        raise ValueError("Неподдерживаемый формат файла. Пожалуйста, используйте GIF, видео или изображение.")


def insert_image_clip(base_clip: VideoClip, sample: ImageClip | VideoClip, pos: list[int], start: float,
                      end: float) -> VideoClip:
    """
    Встраивает изображение или видеоклип в видеоклип в заданные координаты (x, y) на указанный промежуток времени.

    :param base_clip: Исходный видеоклип.
    :param sample: Изображение или GIF.
    :param pos: Координаты X и Y верхнего левого угла изображения
    :param start: Время начала появления изображения в секундах.
    :param end: Время конца появления изображения в секундах.
    :return: Новый видеоклип с встраиванием изображения.
    """

    duration = end - start
    if not isinstance(sample, ImageClip):
        sample = loop_video_clip(sample, duration)

    img_clip = sample.set_position(pos).set_start(start).set_duration(duration)
    return CompositeVideoClip([base_clip, img_clip], size=base_clip.size)


from moviepy.editor import VideoClip, ImageClip


def scale_clips(base_clip: VideoClip, clips: list, k: float = 1) -> list:
    """
    Масштабирует набор клипов относительно фонового клипа.
    Находит самый большой клип по большей стороне, масштабирует его так,
    чтобы его большая сторона была в k раз больше большей стороны фонового клипа.
    Применяет тот же коэффициент масштабирования к остальным клипам.

    :param base_clip: Фоновый видеоклип.
    :param clips: Список видеоклипов или изображений (VideoClip или ImageClip).
    :param k: Положительное число, определяющее во сколько раз по большей стороне
              самый большой клип должен превзойти фон.
    :return: Список масштабированных клипов.
    """

    # Находим большую сторону фонового клипа
    bg_w, bg_h = base_clip.size
    if bg_w > bg_h:
        max_bg_side = bg_w
        max_bg_side_index = 0
    else:
        max_bg_side = bg_h
        max_bg_side_index = 1

    # Наход им максимальную большую сторону среди всех клипов
    max_side = 0
    for c in clips:
        bigger_side = c.size[max_bg_side_index]
        if bigger_side > max_side:
            max_side = bigger_side

    scale_factor = (k * max_bg_side) / max_side

    scaled_clips = [c.resize(scale_factor) for c in clips]

    return scaled_clips


def insert_image_clip_random(main_clip: VideoClip, sample: ImageClip | VideoClip, start: float,
                             end: float) -> ImageClip:
    """
    Создаёт вставляемый клип с случайной позицией и временным интервалом.

    :param main_clip: Основной видеоклип для получения размеров.
    :param sample: Вставляемый изображение или видео.
    :param start: Время начала появления клипа.
    :param end: Время окончания появления клипа.
    :return: Вставляемый ImageClip с установленными позицией и временем.
    """
    boards = main_clip.size
    sample_boards = sample.size
    allowed_pos = (boards[0] - sample_boards[0], boards[1] - sample_boards[1])
    if allowed_pos[0] < 0 or allowed_pos[1] < 0:
        raise ValueError("Невозможно вместить клип", allowed_pos)

    pos = (randint(0, allowed_pos[0] + 1), randint(0, allowed_pos[1] + 1))
    duration = end - start

    if not isinstance(sample, ImageClip):
        sample = loop_video_clip(sample, duration)

    img_clip = sample.set_position(pos).set_start(start).set_duration(duration)
    return img_clip


def loop_video_clip(clip: VideoClip, duration: float) -> VideoClip:
    clip_duration = clip.duration
    repeats = math.ceil(duration / clip_duration)
    looped_clip = clip.loop(n=repeats)
    return looped_clip.subclip(0, duration)
