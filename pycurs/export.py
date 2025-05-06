import os
import markdown
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

class DocumentExporter:
    def __init__(self, db):
        self.db = db
        self.export_dir = "exports"
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
    
    def export_to_html(self, section_id, filename=None):
        """Экспорт документации в HTML формат"""
        section = self.db.get_section(section_id)
        if not section:
            return False
        
        title = section[1]
        content = self.db.get_document_content(section_id)
        
        if not filename:
            filename = f"{title.replace(' ', '_')}.html"
        
        filepath = os.path.join(self.export_dir, filename)
        
        # Преобразуем Markdown в HTML
        html_content = markdown.markdown(content)
        
        # Создаем HTML документ
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #333; }}
        h2 {{ color: #444; margin-top: 30px; }}
        h3 {{ color: #555; }}
        pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; }}
        code {{ font-family: Consolas, monospace; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    {html_content}
</body>
</html>
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return filepath
    
    def export_to_pdf(self, section_id, filename=None):
        """Экспорт документации в PDF формат"""
        section = self.db.get_section(section_id)
        if not section:
            return False
        
        title = section[1]
        content = self.db.get_document_content(section_id)
        
        if not filename:
            filename = f"{title.replace(' ', '_')}.pdf"
        
        filepath = os.path.join(self.export_dir, filename)
        
        # Создаем PDF документ
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Создаем стили
        title_style = styles['Heading1']
        normal_style = styles['Normal']
        
        # Создаем элементы документа
        elements = []
        
        # Добавляем заголовок
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.25*inch))
        
        # Разбиваем содержимое на абзацы и добавляем их в документ
        paragraphs = content.split('\n\n')
        for p in paragraphs:
            if p.startswith('# '):
                elements.append(Paragraph(p[2:], styles['Heading1']))
            elif p.startswith('## '):
                elements.append(Paragraph(p[3:], styles['Heading2']))
            elif p.startswith('### '):
                elements.append(Paragraph(p[4:], styles['Heading3']))
            else:
                elements.append(Paragraph(p, normal_style))
            elements.append(Spacer(1, 0.1*inch))
        
        # Создаем PDF
        doc.build(elements)
        
        return filepath
    
    def export_to_markdown(self, section_id, filename=None):
        """Экспорт документации в Markdown формат"""
        section = self.db.get_section(section_id)
        if not section:
            return False
        
        title = section[1]
        content = self.db.get_document_content(section_id)
        
        if not filename:
            filename = f"{title.replace(' ', '_')}.md"
        
        filepath = os.path.join(self.export_dir, filename)
        
        # Создаем Markdown документ
        markdown_content = f"# {title}\n\n{content}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return filepath
    
    def export_glossary(self, format='html', filename=None):
        """Экспорт глоссария в выбранный формат"""
        terms = self.db.get_glossary_terms()
        
        if not terms:
            return False
        
        if not filename:
            filename = f"glossary.{format}"
        
        filepath = os.path.join(self.export_dir, filename)
        
        if format == 'html':
            # Создаем HTML документ
            html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Глоссарий</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        h1 { color: #333; }
        dt { font-weight: bold; margin-top: 15px; }
        dd { margin-left: 20px; }
    </style>
</head>
<body>
    <h1>Глоссарий</h1>
    <dl>
"""
            
            for term_id, term, definition in terms:
                html += f"        <dt>{term}</dt>\n"
                html += f"        <dd>{definition}</dd>\n"
            
            html += """    </dl>
</body>
</html>
"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
        
        elif format == 'pdf':
            # Создаем PDF документ
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # Создаем стили
            title_style = styles['Heading1']
            term_style = ParagraphStyle(
                'TermStyle',
                parent=styles['Heading3'],
                spaceAfter=6
            )
            definition_style = styles['Normal']
            
            # Создаем элементы документа
            elements = []
            
            # Добавляем заголовок
            elements.append(Paragraph("Глоссарий", title_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Добавляем термины и определения
            for term_id, term, definition in terms:
                elements.append(Paragraph(term, term_style))
                elements.append(Paragraph(definition, definition_style))
                elements.append(Spacer(1, 0.1*inch))
            
            # Создаем PDF
            doc.build(elements)
        
        elif format == 'md':
            # Создаем Markdown документ
            markdown_content = "# Глоссарий\n\n"
            
            for term_id, term, definition in terms:
                markdown_content += f"**{term}**\n: {definition}\n\n"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
        
        return filepath
    
    def export_faq(self, format='html', filename=None):
        """Экспорт FAQ в выбранный формат"""
        faqs = self.db.get_faqs()
        
        if not faqs:
            return False
        
        if not filename:
            filename = f"faq.{format}"
        
        filepath = os.path.join(self.export_dir, filename)
        
        if format == 'html':
            # Создаем HTML документ
            html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Часто задаваемые вопросы (FAQ)</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        h1 { color: #333; }
        h2 { color: #444; margin-top: 30px; }
        .question { font-weight: bold; margin-top: 20px; color: #0066cc; }
        .answer { margin-left: 20px; }
    </style>
</head>
<body>
    <h1>Часто задаваемые вопросы (FAQ)</h1>
"""
            
            for faq_id, question, answer in faqs:
                html += f'    <div class="question">{question}</div>\n'
                html += f'    <div class="answer">{answer}</div>\n'
            
            html += """</body>
</html>
"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
        
        elif format == 'pdf':
            # Создаем PDF документ
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # Создаем стили
            title_style = styles['Heading1']
            question_style = ParagraphStyle(
                'QuestionStyle',
                parent=styles['Heading3'],
                textColor=colors.blue,
                spaceAfter=6
            )
            answer_style = styles['Normal']
            
            # Создаем элементы документа
            elements = []
            
            # Добавляем заголовок
            elements.append(Paragraph("Часто задаваемые вопросы (FAQ)", title_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Добавляем вопросы и ответы
            for faq_id, question, answer in faqs:
                elements.append(Paragraph(question, question_style))
                elements.append(Paragraph(answer, answer_style))
                elements.append(Spacer(1, 0.2*inch))
            
            # Создаем PDF
            doc.build(elements)
        
        elif format == 'md':
            # Создаем Markdown документ
            markdown_content = "# Часто задаваемые вопросы (FAQ)\n\n"
            
            for faq_id, question, answer in faqs:
                markdown_content += f"## {question}\n\n{answer}\n\n"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
        
        return filepath
    
    def export_full_documentation(self, format='html', filename=None):
        """Экспорт всей документации в выбранный формат"""
        if not filename:
            filename = f"full_documentation.{format}"
        
        filepath = os.path.join(self.export_dir, filename)
        
        # Получаем все разделы верхнего уровня
        sections = self.db.get_sections()
        
        if not sections:
            return False
        
        if format == 'html':
            # Создаем HTML документ
            html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Полная документация</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        h1 { color: #333; }
        h2 { color: #444; margin-top: 30px; border-bottom: 1px solid #ddd; padding-bottom: 10px; }
        h3 { color: #555; }
        pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; }
        code { font-family: Consolas, monospace; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .toc { background-color: #f9f9f9; padding: 20px; border-radius: 5px; margin-bottom: 30px; }
        .toc ul { list-style-type: none; }
        .toc li { margin: 5px 0; }
        .toc a { text-decoration: none; color: #0066cc; }
        .toc a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Полная документация</h1>
    
    <div class="toc">
        <h2>Содержание</h2>
        <ul>
"""
            
            # Добавляем оглавление
            for section_id, section_title in sections:
                html += f'            <li><a href="#section-{section_id}">{section_title}</a></li>\n'
            
            # Добавляем ссылки на глоссарий и FAQ
            html += '            <li><a href="#glossary">Глоссарий</a></li>\n'
            html += '            <li><a href="#faq">Часто задаваемые вопросы (FAQ)</a></li>\n'
            
            html += """        </ul>
    </div>
"""
            
            # Добавляем содержимое разделов
            for section_id, section_title in sections:
                html += f'    <h2 id="section-{section_id}">{section_title}</h2>\n'
                
                content = self.db.get_document_content(section_id)
                html_content = markdown.markdown(content)
                html += f'    {html_content}\n\n'
                
                # Получаем подразделы
                subsections = self.db.get_sections(section_id)
                for subsection_id, subsection_title in subsections:
                    html += f'    <h3 id="section-{subsection_id}">{subsection_title}</h3>\n'
                    
                    subcontent = self.db.get_document_content(subsection_id)
                    subhtml_content = markdown.markdown(subcontent)
                    html += f'    {subhtml_content}\n\n'
            
            # Добавляем глоссарий
            html += '    <h2 id="glossary">Глоссарий</h2>\n'
            html += '    <dl>\n'
            
            terms = self.db.get_glossary_terms()
            for term_id, term, definition in terms:
                html += f'        <dt>{term}</dt>\n'
                html += f'        <dd>{definition}</dd>\n'
            
            html += '    </dl>\n\n'
            
            # Добавляем FAQ
            html += '    <h2 id="faq">Часто задаваемые вопросы (FAQ)</h2>\n'
            
            faqs = self.db.get_faqs()
            for faq_id, question, answer in faqs:
                html += f'    <div class="question"><strong>{question}</strong></div>\n'
                html += f'    <div class="answer">{answer}</div>\n'
            
            html += """</body>
</html>
"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
        
        elif format == 'pdf':
            # Создаем PDF документ
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # Создаем стили
            title_style = styles['Heading1']
            section_style = styles['Heading2']
            subsection_style = styles['Heading3']
            normal_style = styles['Normal']
            
            # Создаем элементы документа
            elements = []
            
            # Добавляем заголовок
            elements.append(Paragraph("Полная документация", title_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Добавляем содержимое разделов
            for section_id, section_title in sections:
                elements.append(Paragraph(section_title, section_style))
                
                content = self.db.get_document_content(section_id)
                paragraphs = content.split('\n\n')
                for p in paragraphs:
                    elements.append(Paragraph(p, normal_style))
                    elements.append(Spacer(1, 0.1*inch))
                
                # Получаем подразделы
                subsections = self.db.get_sections(section_id)
                for subsection_id, subsection_title in subsections:
                    elements.append(Paragraph(subsection_title, subsection_style))
                    
                    subcontent = self.db.get_document_content(subsection_id)
                    subparagraphs = subcontent.split('\n\n')
                    for p in subparagraphs:
                        elements.append(Paragraph(p, normal_style))
                        elements.append(Spacer(1, 0.1*inch))
            
            # Добавляем глоссарий
            elements.append(Paragraph("Глоссарий", section_style))
            
            terms = self.db.get_glossary_terms()
            for term_id, term, definition in terms:
                elements.append(Paragraph(f"<b>{term}</b>", normal_style))
                elements.append(Paragraph(definition, normal_style))
                elements.append(Spacer(1, 0.1*inch))
            
            # Добавляем FAQ
            elements.append(Paragraph("Часто задаваемые вопросы (FAQ)", section_style))
            
            faqs = self.db.get_faqs()
            for faq_id, question, answer in faqs:
                elements.append(Paragraph(f"<b>{question}</b>", normal_style))
                elements.append(Paragraph(answer, normal_style))
                elements.append(Spacer(1, 0.2*inch))
            
            # Создаем PDF
            doc.build(elements)
        
        elif format == 'md':
            # Создаем Markdown документ
            markdown_content = "# Полная документация\n\n"
            
            # Добавляем оглавление
            markdown_content += "## Содержание\n\n"
            
            for section_id, section_title in sections:
                markdown_content += f"- [{section_title}](#section-{section_id})\n"
            
            markdown_content += "- [Глоссарий](#glossary)\n"
            markdown_content += "- [Часто задаваемые вопросы (FAQ)](#faq)\n\n"
            
            # Добавляем содержимое разделов
            for section_id, section_title in sections:
                markdown_content += f"## <a id='section-{section_id}'></a>{section_title}\n\n"
                
                content = self.db.get_document_content(section_id)
                markdown_content += f"{content}\n\n"
                
                # Получаем подразделы
                subsections = self.db.get_sections(section_id)
                for subsection_id, subsection_title in subsections:
                    markdown_content += f"### <a id='section-{subsection_id}'></a>{subsection_title}\n\n"
                    
                    subcontent = self.db.get_document_content(subsection_id)
                    markdown_content += f"{subcontent}\n\n"
            
            # Добавляем глоссарий
            markdown_content += "## <a id='glossary'></a>Глоссарий\n\n"
            
            terms = self.db.get_glossary_terms()
            for term_id, term, definition in terms:
                markdown_content += f"**{term}**\n: {definition}\n\n"
            
            # Добавляем FAQ
            markdown_content += "## <a id='faq'></a>Часто задаваемые вопросы (FAQ)\n\n"
            
            faqs = self.db.get_faqs()
            for faq_id, question, answer in faqs:
                markdown_content += f"### {question}\n\n{answer}\n\n"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
        
        return filepath 