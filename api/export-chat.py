def _fmt(self, para, text):
    """Форматирование текста с поддержкой **bold**, *italic*, `code`, ***bold+italic***"""
    
    # Паттерн для разбора форматирования (порядок важен!)
    pattern = re.compile(
        r'(\*\*\*(.+?)\*\*\*)'      # group 1,2: ***bold+italic***
        r'|(\*\*(.+?)\*\*)'          # group 3,4: **bold**
        r'|(\*(.+?)\*)'              # group 5,6: *italic*
        r'|(`([^`]+?)`)'             # group 7,8: `code`
        r'|(~~(.+?)~~)'              # group 9,10: ~~strikethrough~~
    )
    
    pos = 0
    for m in pattern.finditer(text):
        # Текст до совпадения
        before = text[pos:m.start()]
        if before:
            para.add_run(before)
        
        if m.group(2):       # ***bold+italic***
            r = para.add_run(m.group(2))
            r.bold = True
            r.italic = True
        elif m.group(4):     # **bold**
            r = para.add_run(m.group(4))
            r.bold = True
        elif m.group(6):     # *italic*
            r = para.add_run(m.group(6))
            r.italic = True
        elif m.group(8):     # `code`
            r = para.add_run(m.group(8))
            r.font.name = 'Courier New'
            r.font.size = Pt(10)
        elif m.group(10):    # ~~strikethrough~~
            r = para.add_run(m.group(10))
            r.font.strike = True
        
        pos = m.end()
    
    # Оставшийся текст
    remaining = text[pos:]
    if remaining:
        para.add_run(remaining)

def _text_math(self, doc, text):
    """Обработка строки с inline формулами и форматированием"""
    
    # Проверяем заголовки Markdown
    heading_match = re.match(r'^(#{1,6})\s+(.+)$', text.strip())
    if heading_match:
        level = len(heading_match.group(1))
        heading_text = heading_match.group(2)
        doc.add_heading(heading_text, level=min(level, 6))
        return
    
    # Разделяем на части по inline-формулам $...$
    parts = re.split(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', text)
    
    if len(parts) <= 1:
        # Нет формул — просто форматированный текст
        p = doc.add_paragraph()
        self._fmt(p, text)
        return
    
    p = doc.add_paragraph()
    for idx, part in enumerate(parts):
        if idx % 2 == 0:
            if part:
                self._fmt(p, part)
        else:
            insert_math(p, part.strip())
