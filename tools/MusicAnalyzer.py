import librosa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import librosa.display
from typing import Optional, List
import logging
import os


class MusicException(Exception):
    """Исключение, связанное с ошибками в классе MusicAnalyzer."""
    pass


class MusicAnalyzer:
    """
    Класс для анализа музыкальных аудиофайлов. Позволяет загружать аудио, обнаруживать биты,
    оценивать их силу, выбирать самые сильные биты и визуализировать результаты.
    """

    def __init__(
            self,
            audio_path: str,
            frame_length: int = 2048,
            hop_length: int = 512,
            strength_window: float = 0.05,
            verbose: bool = False,
            log_file: Optional[str] = None
    ) -> None:
        """
        Инициализация класса.

        :param audio_path: Путь к аудиофайлу.
        :type audio_path: `str`
        :param frame_length: Длина окна для вычисления RMS (по умолчанию 2048).
        :type frame_length: `int`
        :param hop_length: Шаг окна (по умолчанию 512).
        :type hop_length: `int`
        :param strength_window: Окно времени (в секундах) вокруг бита для оценки его силы (по умолчанию 0.05).
        :type strength_window: `float`
        :param verbose: Флаг для вывода подробной информации (по умолчанию False).
        :type verbose: `bool`
        :param log_file: Путь к файлу для сохранения логов (по умолчанию None).
        :type log_file: Optional[str]
        """
        self.audio_path: str = audio_path
        self.frame_length: int = frame_length
        self.hop_length: int = hop_length
        self.strength_window: float = strength_window
        self.__verbose: bool = verbose

        # Инициализация переменных
        self.y: Optional[np.ndarray] = None
        self.sr: Optional[int] = None
        self.tempo: Optional[float] = None
        self.beat_frames: Optional[np.ndarray] = None
        self.beat_times: Optional[np.ndarray] = None
        self.rms: Optional[np.ndarray] = None
        self.times: Optional[np.ndarray] = None
        self.beat_strengths: Optional[List[float]] = None
        self.df_beats: Optional[pd.DataFrame] = None
        self.top_beats: Optional[pd.DataFrame] = None

        # Настройка логирования
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)  # Устанавливаем максимальный уровень для обработки

        # Форматтер для логов
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Удаляем все обработчики, чтобы избежать дублирования при повторных инициализациях
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # Обработчик для консоли
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO if self.__verbose else logging.WARNING)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Обработчик для файла, если указан
        if log_file:
            # Создаем директорию для файла логов, если она не существует
            os.makedirs(os.path.dirname(log_file), exist_ok=True) if os.path.dirname(log_file) else None
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)  # Записываем все уровни в файл
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def set_verbose(self, verbose: bool) -> None:
        """
        Установка флага verbose для вывода подробной информации.

        :param verbose: Флаг для вывода подробной информации.
        :type verbose: `bool`
        """
        self.__verbose = verbose
        # Изменение уровня консольного обработчика
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(logging.INFO if self.__verbose else logging.WARNING)
        self.logger.info(f"Verbose mode set to {self.__verbose}.")

    def load_audio(self) -> None:
        """
        Загрузка аудиофайла с помощью librosa.

        :raises MusicException: Если не удалось загрузить аудиофайл.
        """
        try:
            self.y, self.sr = librosa.load(self.audio_path)
            self.logger.info(f"Аудиофайл '{self.audio_path}' загружен. Частота дискретизации: {self.sr} Гц.")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки аудиофайла: {e}")
            raise MusicException(f"Ошибка загрузки аудиофайла: {e}")

    def compute_rms(self) -> None:
        """
        Вычисление энергии (RMS) для каждого фрейма.

        :raises MusicException: Если аудиофайл не загружен.
        """
        if self.y is None or self.sr is None:
            raise MusicException("Аудиофайл не загружен. Вызовите метод load_audio() перед compute_rms().")

        self.rms = librosa.feature.rms(y=self.y, frame_length=self.frame_length, hop_length=self.hop_length)[0]
        self.times = librosa.frames_to_time(np.arange(len(self.rms)), sr=self.sr, hop_length=self.hop_length)
        self.logger.info("RMS энергия вычислена.")

    def detect_beats(self) -> None:
        """
        Обнаружение битов с помощью librosa.

        :raises MusicException: Если не удалось обнаружить биты.
        """
        if self.y is None or self.sr is None:
            raise MusicException("Аудиофайл не загружен. Вызовите метод load_audio() перед detect_beats().")

        try:
            self.tempo, self.beat_frames = librosa.beat.beat_track(y=self.y, sr=self.sr)
            self.beat_times = librosa.frames_to_time(self.beat_frames, sr=self.sr, hop_length=self.hop_length)
            self.logger.info(f"Биты обнаружены. Темп: {self.tempo} BPM. Количество битов: {len(self.beat_times)}.")
        except Exception as e:
            self.logger.error(f"Ошибка обнаружения битов: {e}")
            raise MusicException(f"Ошибка обнаружения битов: {e}")

    def _get_beat_strength(self, beat_time: float) -> float:
        """
        Получение RMS энергии в окне вокруг бита.

        :param beat_time: Время бита в секундах.
        :type beat_time: `float`
        :return: Среднее значение RMS энергии в окне вокруг бита.
        :rtype: `float`
        """
        start_time = beat_time - self.strength_window / 2
        end_time = beat_time + self.strength_window / 2
        indices = np.where((self.times >= start_time) & (self.times <= end_time))[0]
        if len(indices) == 0:
            return 0.0
        return float(np.mean(self.rms[indices]))

    def calculate_beat_strengths(self) -> None:
        """
        Оценка силы каждого бита на основе RMS энергии в окне вокруг бита.

        :raises MusicException: Если биты не обнаружены или RMS не вычислена.
        """
        if self.beat_times is None or self.rms is None or self.times is None:
            raise MusicException("Необходимые данные отсутствуют. Выполните методы detect_beats() и compute_rms().")

        self.beat_strengths = [self._get_beat_strength(bt) for bt in self.beat_times]
        self.logger.info("Сила битов рассчитана.")

    def create_beats_dataframe(self) -> None:
        """
        Создание DataFrame с таймкодами битов и их силой.

        :raises MusicException: Если силы битов не рассчитаны.
        """
        if self.beat_times is None or self.beat_strengths is None:
            raise MusicException(
                "Необходимые данные отсутствуют. Выполните методы detect_beats() и calculate_beat_strengths().")

        self.df_beats = pd.DataFrame({
            'Beat Time (s)': self.beat_times,
            'Strength': self.beat_strengths
        })
        self.logger.info("DataFrame с битами создан.")

    def get_top_beats(self, top_n: int = 10) -> pd.DataFrame:
        """
        Получение топ-N самых сильных битов.

        :param top_n: Количество топ-битов для выбора (по умолчанию 10).
        :type top_n: `int`
        :return: DataFrame с топ-битами.
        :rtype: `pd.DataFrame`
        :raises MusicException: Если DataFrame битов не создан.
        """
        if self.df_beats is None:
            raise MusicException("DataFrame битов не создан. Выполните метод create_beats_dataframe().")

        self.top_beats = self.df_beats.sort_values(by='Strength', ascending=False).head(top_n)
        self.logger.info(f"Топ-{top_n} самых сильных битов выбраны.")
        return self.top_beats

    def get_strong_beats_above_threshold(self, percentile: float = 0.75) -> pd.DataFrame:
        """
        Получение битов с силой выше заданного процентиля.

        :param percentile: Процентиль для определения порога (должен быть в диапазоне (0, 1], по умолчанию 0.75).
        :type percentile: `float`
        :return: DataFrame с сильными битами.
        :rtype: `pd.DataFrame`
        :raises MusicException: Если DataFrame битов не создан или процентиль вне допустимого диапазона.
        """
        if self.df_beats is None:
            raise MusicException("DataFrame битов не создан. Выполните метод create_beats_dataframe().")

        if not 0 < percentile <= 1:
            raise MusicException("percentile должен быть в диапазоне (0, 1].")

        threshold = self.df_beats['Strength'].quantile(percentile)
        strong_beats = self.df_beats[self.df_beats['Strength'] >= threshold]
        self.logger.info(f"Биты с силой выше {percentile * 100}-го процентиля ({threshold:.4f}) выбраны.")
        return strong_beats

    def visualize_beats(self, top_n: int = 10) -> None:
        """
        Визуализация всех битов и топ-N самых сильных битов на временной шкале.

        :param top_n: Количество топ-битов для выделения (по умолчанию 10).
        :type top_n: `int`
        :raises MusicException: Если DataFrame битов не создан.
        """
        if self.df_beats is None:
            raise MusicException("DataFrame битов не создан. Выполните метод create_beats_dataframe().")

        plt.figure(figsize=(14, 6))

        # Визуализация сигнала
        librosa.display.waveshow(self.y, sr=self.sr, alpha=0.6, label='Waveform')

        # Нанесение всех битов
        plt.vlines(self.df_beats['Beat Time (s)'], ymin=-1, ymax=1, color='gray', linestyle='--', alpha=0.5,
                   label='Beats')

        # Нанесение топ-битов
        top_beats = self.get_top_beats(top_n)
        plt.vlines(top_beats['Beat Time (s)'], ymin=-1, ymax=1, color='r', linestyle='-', linewidth=2,
                   label='Top Beats')

        plt.legend()
        plt.xlabel('Время (с)')
        plt.ylabel('Амплитуда')
        plt.title('Обнаружение и визуализация битов в аудиофайле')
        plt.show()

    def save_beats_to_csv(self, filepath: str = 'beat_times.csv') -> None:
        """
        Сохранение всех битов и их силы в CSV файл.

        :param filepath: Путь для сохранения CSV файла (по умолчанию 'beat_times.csv').
        :type filepath: `str`
        :raises MusicException: Если DataFrame битов не создан.
        """
        if self.df_beats is None:
            raise MusicException("DataFrame битов не создан. Выполните метод create_beats_dataframe().")

        try:
            # Создаем директорию для файла, если она не существует
            os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None
            self.df_beats.to_csv(filepath, index=False)
            self.logger.info(f"Биты сохранены в файл '{filepath}'.")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения CSV файла: {e}")
            raise MusicException(f"Ошибка сохранения CSV файла: {e}")

    def process(self) -> None:
        """
        Полный процесс анализа: загрузка аудио, вычисление RMS, обнаружение битов,
        оценка их силы и создание DataFrame.

        :raises MusicException: Если любой из этапов анализа завершается с ошибкой.
        """
        try:
            self.load_audio()
            self.compute_rms()
            self.detect_beats()
            self.calculate_beat_strengths()
            self.create_beats_dataframe()
            self.logger.info("Анализ завершен.")
        except MusicException as e:
            self.logger.error(f"Процесс анализа прерван: {e}")
            raise
