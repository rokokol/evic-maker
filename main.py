import random as rnd

from audiofile import duration
from moviepy.audio.io.AudioFileClip import AudioFileClip
from tqdm import tqdm

from tools.MusicAnalyzer import MusicAnalyzer
from tools.VideoTools import make_video, insert_image_clip, scale_clips, insert_image_clip_random
from moviepy.editor import VideoFileClip, VideoClip, ImageClip, CompositeVideoClip


def analyze_music_and_add_images(backstage_path: str, images_path: list[str], music_path: str, sensitivity: float) -> VideoFileClip:
    print('Анализ музыкального файла...')

    analyzer = MusicAnalyzer(audio_path=music_path, log_file='logs/music_handler.log')
    analyzer.process()

    top_beats = analyzer.get_strong_beats_above_threshold(sensitivity)
    max_strength_percent = top_beats['Strength'].max() / 100

    print('Создание главного клипа...')
    main_clip = make_video(backstage_path, analyzer.get_audio_duration())

    print('Создание дочерних клипов...')
    image_clips = scale_clips(main_clip, [make_video(img, 5) for img in images_path], 0.3)

    print('Добавление дочерних клипов в видео...')
    accumulated_clips = []  # Список для накопления всех вставляемых клипов

    percentile_30 = top_beats['Strength'].quantile(.3)
    percentile_70 = top_beats['Strength'].quantile(.7)

    for time, strength in tqdm(top_beats.to_numpy(), desc="Добавление клипов по битам"):
        if strength < percentile_30:
            count = 1
        elif strength < percentile_70:
            count = 2
        else:
            count = 3

        for _ in range(count):
            chosen_clip = rnd.choice(image_clips)
            new_clip = insert_image_clip_random(main_clip, chosen_clip, time, time + 2 + count)
            accumulated_clips.append(new_clip)

    print('Создание итогового CompositeVideoClip...')
    final_clip = CompositeVideoClip([main_clip] + accumulated_clips)

    print('Добавляем аудио...')
    audio_clip = AudioFileClip(music_path).subclip(0, final_clip.duration)
    final_clip = final_clip.set_audio(audio_clip)

    return final_clip




if __name__ == "__main__":
    test_paths = [
    "data/test_dump/cd.png",
    # "data/test_dump/computer.gif",
    "data/test_dump/error.png",
    # "data/test_dump/folder.gif",
    # "data/test_dump/loading.gif",
    "data/test_dump/warning.png"
    ]

    res = analyze_music_and_add_images(
        'data/test_dump/background.png',
        test_paths,
        'data/test_dump/test.mp3',
        0.80
    )

    print('Сохранение файла...')
    res.write_videofile("output.mp4", fps=24)

    # video = make_video('data/test_dump/background.png', 15)
    # # clip = ImageClip('/home/rokoko/Desktop/dreamlady.webp')
    # res = scale_clips(video, [make_video(img, 5) for img in test_paths], 0.3)
    # video = insert_image_clip_random(video, res[3], 2, 8)
    # video = insert_image_clip_random(video, res[0], 0, 11)
    # video.write_videofile("output.mp4", fps=30)

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
