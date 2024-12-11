import math

from moviepy.editor import VideoFileClip, ImageClip
from moviepy.video.VideoClip import VideoClip


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
            # Обработка видео или GIF: зацикливание
            base_clip = VideoFileClip(input_path)
            base_duration = base_clip.duration
            repeats = math.ceil(duration / base_duration)
            looped_clip = base_clip.loop(n=repeats)
            final_clip = looped_clip.subclip(0, duration)
            return final_clip
        except Exception as e:
            raise ValueError(f"Ошибка при обработке видео/GIF: {e}")
    elif ext in image_extensions:
        try:
            # Обработка изображения: растягивание
            base_clip = ImageClip(input_path)
            final_clip = base_clip.set_duration(duration)
            return final_clip
        except Exception as e:
            raise ValueError(f"Ошибка при обработке изображения: {e}")
    else:
        raise ValueError("Неподдерживаемый формат файла. Пожалуйста, используйте GIF, видео или изображение.")


if __name__ == "__main__":
    video = make_video('/home/rokoko/Desktop/cat-кошка.gif', 15.0)
    video.write_videofile("output.mp4", fps=24)

    # audio_file = '/home/rokoko/Desktop/rickroll.mp3'
    #
    # analyzer = MusicAnalyzer(audio_path=audio_file, log_file='logs/music_handler.log')
    #
    # analyzer.process()
    #
    # top_beats = analyzer.get_strong_beats_above_threshold()
    # print(top_beats)
    #
    # analyzer.visualize_beats(top_n=len(top_beats))
