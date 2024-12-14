from tools.MusicAnalyzer import MusicAnalyzer
from tools.VideoTools import make_video, insert_image_clip, scale_clips, insert_image_clip_random
from moviepy.editor import VideoFileClip, VideoClip, ImageClip, CompositeVideoClip

def analyze_music_and_add_images(backstage_path: str, images_path: list[str], music_path: str, sensitivity: float):
    print('Анализ музыкального файла...')

    analyzer = MusicAnalyzer(audio_path=music_path, log_file='logs/music_handler.log')
    analyzer.process()

    top_beats = analyzer.get_strong_beats_above_threshold(sensitivity)
    print(top_beats)

if __name__ == "__main__":
    print('Анализ музыкального файла...')

    analyzer = MusicAnalyzer(audio_path='/home/rokoko/Desktop/rickroll.mp3', log_file='logs/music_handler.log')
    analyzer.process()

    top_beats = analyzer.get_strong_beats_above_threshold()
    print(top_beats)
    # video = make_video('/home/rokoko/Desktop/cat-кошка.gif', 15)
    # clip = ImageClip('/home/rokoko/Desktop/dreamlady.webp')
    # res = scale_clips(video, [clip, video.copy()], 0.3)
    # video = insert_image_clip_random(video, res[0], 0, 11)
    # video = insert_image_clip_random(video, res[1], 2, 8)
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
