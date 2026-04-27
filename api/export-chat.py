    # CHANGED: _process — detect consecutive images and render as grid
    def _process(self, doc, content):
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]

            # NEW: detect group of consecutive images (separated by blank lines or adjacent)
            img_match = re.search(r'!\[([^\]]*)\]\(([^\)]+)\)', line)
            if img_match:
                # Collect all consecutive images (allowing blank lines between)
                image_group = []
                j = i
                while j < len(lines):
                    ln = lines[j]
                    m = re.search(r'!\[([^\]]*)\]\(([^\)]+)\)', ln)
                    if m:
                        image_group.append({'alt': m.group(1), 'src': m.group(2)})
                        j += 1
                    elif ln.strip() == '':
                        # blank line — peek ahead to see if next non-blank is also image
                        k = j + 1
                        while k < len(lines) and lines[k].strip() == '':
                            k += 1
                        if k < len(lines) and re.search(r'!\[([^\]]*)\]\(([^\)]+)\)', lines[k]):
                            j = k  # continue collecting
                        else:
                            break
                    else:
                        break

                if len(image_group) == 1:
                    self._img(doc, image_group[0]['src'], image_group[0]['alt'])
                else:
                    self._image_grid(doc, image_group)
                i = j
                continue

            if line.strip().startswith('```'):
                code = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code.append(lines[i])
                    i += 1
                self._code(doc, '\n'.join(code))
                i += 1
                continue

            if '|' in line and line.strip().startswith('|'):
                tlines = []
                while i < len(lines) and '|' in lines[i]:
                    if not re.match(r'^\s*\|[\s\-:|]+\|\s*$', lines[i]):
                        tlines.append(lines[i])
                    i += 1
                if tlines:
                    self._table_with_math(doc, tlines)
                continue

            bm = re.match(r'^\s*\$\$(.+?)\$\$\s*$', line)
            if bm:
                add_block_formula(doc, bm.group(1).strip())
                i += 1
                continue

            if line.strip() == '$$':
                fl = []
                i += 1
                while i < len(lines) and lines[i].strip() != '$$':
                    fl.append(lines[i])
                    i += 1
                latex = ' '.join(fl).strip()
                if latex:
                    add_block_formula(doc, latex)
                i += 1
                continue

            if line.strip():
                self._text_math(doc, line)
            else:
                doc.add_paragraph()
            i += 1

    # NEW: render multiple images as a 2-column grid (table)
    def _image_grid(self, doc, images):
        """Render images in a 2-column grid (table without borders)"""
        import urllib.request, base64

        cols = 2
        rows = (len(images) + cols - 1) // cols

        table = doc.add_table(rows=rows, cols=cols)
        table.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Remove borders from all cells
        tbl = table._element
        tblPr = tbl.find(qn('w:tblPr'))
        if tblPr is None:
            tblPr = OxmlElement('w:tblPr')
            tbl.insert(0, tblPr)
        tblBorders = OxmlElement('w:tblBorders')
        for border in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
            b = OxmlElement(f'w:{border}')
            b.set(qn('w:val'), 'nil')
            tblBorders.append(b)
        tblPr.append(tblBorders)

        # Image width: half of 5 inches minus small gap
        img_width = Inches(2.8)

        for idx, img_info in enumerate(images):
            row = idx // cols
            col = idx % cols
            cell = table.rows[row].cells[col]
            # Clear default paragraph
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

            src = img_info['src']
            alt = img_info['alt']

            try:
                if src.startswith('data:image'):
                    b64 = src.split('base64,')[1]
                    stream = io.BytesIO(base64.b64decode(b64))
                else:
                    req = urllib.request.Request(src, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        stream = io.BytesIO(resp.read())
                p.add_run().add_picture(stream, width=img_width)
            except Exception as e:
                print(f'Grid image error: {e}')
                r = p.add_run(f'[Image: {alt}]')
                r.italic = True

        # Add spacing after grid
        doc.add_paragraph()
