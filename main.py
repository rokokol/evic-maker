from tools.MusicAnalyzer import MusicAnalyzer


if __name__ == "__main__":
    audio_file = '/home/rokoko/Desktop/rickroll.mp3'

    analyzer = MusicAnalyzer(audio_path=audio_file, log_file='logs/music_handler.log')

    analyzer.process()

    top_beats = analyzer.get_strong_beats_above_threshold()
    print(top_beats)

    analyzer.visualize_beats(top_n=len(top_beats))
