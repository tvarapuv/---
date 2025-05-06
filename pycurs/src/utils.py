import markdown
import os
import re
import shutil
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# Регистрируем шрифт для поддержки русского языка
FONT_PATH = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'  # Используем Arial Unicode для лучшей поддержки UTF-8
pdfmetrics.registerFont(TTFont('Arial-Unicode', FONT_PATH))

def export_to_html(filename, title, content):
    """Экспортирует документ в HTML с корректной обработкой изображений."""
    # Создаем директорию для изображений
    html_dir = os.path.dirname(filename)
    img_dir = os.path.join(html_dir, 'images')
    os.makedirs(img_dir, exist_ok=True)
    
    # Ищем все изображения в формате ![alt](path)
    img_pattern = r'!\[(.*?)\]\((.*?)\)'
    img_matches = re.findall(img_pattern, content)
    
    # Копируем изображения в директорию и обновляем пути
    for i, (alt, path) in enumerate(img_matches):
        if os.path.exists(path):
            # Получаем имя файла из пути
            img_filename = os.path.basename(path)
            # Новый путь к изображению
            new_path = os.path.join('images', img_filename)
            # Полный путь для копирования
            full_new_path = os.path.join(html_dir, new_path)
            
            # Копируем изображение
            try:
                shutil.copy2(path, full_new_path)
                # Заменяем путь в контенте
                content = content.replace(f"![{alt}]({path})", f"![{alt}]({new_path})")
            except Exception as e:
                print(f"Ошибка при копировании изображения: {e}")
    
    # Конвертируем Markdown в HTML
    html_content = markdown.markdown(content)
    
    # Создаем HTML документ
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 40px; 
            line-height: 1.6; 
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{ 
            color: #333; 
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        img {{ 
            max-width: 100%; 
            height: auto; 
            display: block;
            margin: 20px auto;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px;
        }}
        pre {{
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        code {{
            background-color: #f5f5f5;
            padding: 2px 5px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    {html_content}
</body>
</html>
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

def export_to_pdf(filename, title, content):
    """Экспортирует документ в PDF с поддержкой UTF-8 и встроенными изображениями."""
    # Регистрируем шрифт с поддержкой UTF-8
    try:
        pdfmetrics.registerFont(TTFont('Arial Unicode', 'Arial Unicode.ttf'))
    except:
        # Если шрифт не найден, используем стандартный
        pass
    
    # Создаем документ
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Создаем стили
    styles = getSampleStyleSheet()
    
    # Модифицируем существующий стиль Title вместо создания нового
    styles['Title'].fontName = 'Arial-Unicode'
    styles['Title'].fontSize = 16
    styles['Title'].alignment = TA_CENTER
    styles['Title'].spaceAfter = 12
    
    # Создаем стиль для обычного текста
    styles.add(ParagraphStyle(
        name='CustomNormal',
        fontName='Arial-Unicode',
        fontSize=12,
        alignment=TA_JUSTIFY,
        spaceAfter=6
    ))
    
    # Подготавливаем элементы документа
    elements = []
    
    # Добавляем заголовок
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Обрабатываем Markdown и ищем изображения
    html_content = markdown.markdown(content)
    
    # Ищем все изображения в формате ![alt](path)
    img_pattern = r'!\[(.*?)\]\((.*?)\)'
    img_matches = re.findall(img_pattern, content)
    
    # Заменяем изображения на плейсхолдеры
    for i, (alt, path) in enumerate(img_matches):
        placeholder = f"IMAGE_PLACEHOLDER_{i}"
        content = content.replace(f"![{alt}]({path})", placeholder)
    
    # Разбиваем текст на абзацы
    paragraphs = content.split('\n\n')
    
    # Обрабатываем каждый абзац
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # Проверяем, содержит ли абзац плейсхолдер изображения
        img_placeholder_match = re.search(r'IMAGE_PLACEHOLDER_(\d+)', paragraph)
        if img_placeholder_match:
            img_index = int(img_placeholder_match.group(1))
            alt, path = img_matches[img_index]
            
            # Проверяем, существует ли файл
            if os.path.exists(path):
                try:
                    # Добавляем изображение
                    img = Image(path, width=400, height=300, kind='proportional')
                    elements.append(img)
                    elements.append(Spacer(1, 6))
                    
                    # Добавляем подпись к изображению, если есть
                    if alt:
                        elements.append(Paragraph(alt, styles['CustomNormal']))
                        elements.append(Spacer(1, 12))
                except Exception as e:
                    # Если не удалось добавить изображение, добавляем текст с путем
                    elements.append(Paragraph(f"Изображение: {path}", styles['CustomNormal']))
                    elements.append(Spacer(1, 6))
            else:
                # Если файл не существует, добавляем текст с путем
                elements.append(Paragraph(f"Изображение не найдено: {path}", styles['CustomNormal']))
                elements.append(Spacer(1, 6))
        else:
            # Обычный текст
            elements.append(Paragraph(paragraph, styles['CustomNormal']))
            elements.append(Spacer(1, 6))
    
    # Строим документ
    doc.build(elements)

def export_to_markdown(filename, title, content):
    """Экспортирует документ в Markdown."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(content)

def create_document_directory():
    """Создает директорию для хранения экспортированных документов."""
    os.makedirs('documents', exist_ok=True)
    return 'documents'

def sanitize_filename(filename):
    """Очищает имя файла от недопустимых символов."""
    return "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip() 