# Симуляция жидкости с использованием WebGPU

<img align=right src="https://www.w3.org/2023/02/webgpu-logos/webgpu-notext.svg" height="50px" width="50px">
Визуализация течения жидкости с использованием WebGPU на основе алгоритма Stable Fluids.

- [Видео демонстрация](./DEMO/coursework.mp4)
- [Деплой](https://stable-fluids-webgpu.vercel.app/) (требуется браузер с поддержкой WebGPU)
- [Отчет о курсовой](./report/main.pdf)
- [Презентация](./DEMO/coursework.pdf)
- [Источники](./insipration.md)

## Настройка браузера

> Приложение разрабатывалось на Chromium + Vulkan в Ubuntu 24.04

WebGPU относительно новая технология,
поэтому для её использования могут потребоваться дополнительные настройки браузера.

Смотрите [статус](https://github.com/gpuweb/gpuweb/wiki/Implementation-Status)
реализации спецификации WebGPU под разные браузеры.

### Включение WebGPU

| Браузер  | Подключение                             |
| -------- | --------------------------------------- |
| Chromium | chrome://flags -> #enable-unsafe-webgpu |

### Включение Vulkan

Рекомендуется также установить `Vulkan` для лучшей производительности

```bash
sudo apt update
sudo apt install mesa-vulkan-drivers
sudo apt install vulkan-tools

# Check installation
vkcube
vulkaninfo --summary
```

| Браузер  | Подключение                           |
| -------- | ------------------------------------- |
| Chromium | chrome://flags -> #enable-vulkan flag |

## Этапы работы

1. Изучение предметной области
2. Выбор алгоритма визуализации жидкости
3. Исследование алгоритма и возможностей WebGPU
4. Реализация алгоритма
5. Разработка веб-приложения для визуализации
6. Тестирование, оптимизация и анализ результатов

## Дедлайны

- 13.12.25 Расчетно-пояснительная записка
- 20.12.25 предпоказ (презентация + речь)
- 27.12.25 Защита

## Отчёт

### Настройка VS Code и LaTeX

Установить расширения для VS Code:

- LaTeX Workshop
- LTeX — LanguageTool (grammar and spell checking) + выбрать русский язык `"ltex.language": "ru-RU",`

```bash
# Times New Roman шрифт для LaTeX
sudo apt install ttf-mscorefonts-installer

# Воруем шаблон отчёта
git clone https://github.com/mirea-ninja/Latex-Template-for-Report-Diploma-Thesis.git report
cd report
rm -rf .git

# Берем нормальный .gitignore
curl -sSL https://raw.githubusercontent.com/AndreyAkinshin/Russian-Phd-LaTeX-Dissertation-Template/refs/heads/master/.gitignore -o .gitignore

# Создаем .latexmkrc, чтобы LaTeX Workshop использовал xelatex (требуется шаблоном)
cat > .latexmkrc <<'EOF'
$pdf_mode = 1;
$pdflatex = 'xelatex --shell-escape --synctex=1 %O %S';
$pdf_previewer = 'start evince';
EOF

# Компиляция отчёта (на деле Latex Workshop сам всё делает)
xelatex -shell-escape main.tex
```

### Конвертация latex формул в png

[src](https://webapps.stackexchange.com/questions/4824/adding-equations-to-google-slides)

Используйте онлайн редактор формул:
<https://editor.codecogs.com/>

```bash
# Пример конвертации из svg в png с помощью ImageMagick
convert -density 1200 'CodeCogsEqn(1).svg' out2.png
```

## Веб приложение

- Nextjs
- [typeGPU](https://docs.swmansion.com/TypeGPU/)
- [WebGPU-Dev-Extension](https://webgpufundamentals.org/webgpu/lessons/webgpu-debugging.html#webgpu-dev-extension)
  - Включить "Show Shader Errors" (выключается при перезагрузке браузера)
- [VS code wgsl extension](https://marketplace.visualstudio.com/items?itemName=wgsl-analyzer.wgsl-analyzer)

### Графические библиотеки

- lil-gui
- [wgpu-matrix](https://wgpu-matrix.org/docs/)
