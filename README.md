# EViC maker
**Easy Video Clip maker** — приложение для создания клипа под музыку. Кросс-платформенное, написано на `Python3`

## Принцип работы
Загружаются исходники — фон, `.png` и/или `.gif` изображения, и, конечно, музыка. После на их основе создается видеофайл, где они будут появляться в случайных местах экрана в такт музыки. Дополнительно можно добавить некоторые эффекты. Таким образом получается простой и незамысловатый музыкальный клип

## Интерфейс
![img_1.png](img_1.png)

#### В принципе, тут все понятно:
- Видеоплеер
- Кнопка для повторной генерации, если текущая не понравилась
- Спектограмма музыки
- Лоток для картинок. Сверху закреплено фоновое изображение
- - Картинка
- - Название изображения
- - Флаги для эффектов
- - - должно становиться негативным
- - - помехи
- - - может появляться на границе клипа
- Ползунок чувствительности. Определяет насколько часто, насколько появляется то или иное изображение
- Кнопка для сохранения клипа
