PAGE_HEIGHT = 842
LINE_HEIGHT = 12
TOP_MARGIN = 800
LINES_PER_PAGE = 60


def escape_pdf_text(line: str) -> bytes:
    escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return escaped.encode("cp1252")


def build_page_stream(lines: list[str]) -> bytes:
    commands = [b"BT", b"/F1 10 Tf", f"{LINE_HEIGHT} TL".encode(), f"50 {TOP_MARGIN} Td".encode()]
    for line in lines:
        commands.append(b"(" + escape_pdf_text(line) + b") Tj T*")
    commands.append(b"ET")
    return b"\n".join(commands)


def build_text_pdf(lines: list[str]) -> bytes:
    pages = [lines[start:start + LINES_PER_PAGE] for start in range(0, len(lines), LINES_PER_PAGE)] or [[]]
    font_id = 3
    first_page_id = 4
    page_ids = [first_page_id + index * 2 for index in range(len(pages))]
    objects = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: b"<< /Type /Pages /Kids [" + b" ".join(f"{page_id} 0 R".encode() for page_id in page_ids)
        + f"] /Count {len(pages)} >>".encode(),
        font_id: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    }
    for page_id, page_lines in zip(page_ids, pages):
        stream = build_page_stream(page_lines)
        objects[page_id] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 {PAGE_HEIGHT}] "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {page_id + 1} 0 R >>"
        ).encode()
        objects[page_id + 1] = f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream"
    output = bytearray(b"%PDF-1.4\n")
    offsets = {}
    for object_id in sorted(objects):
        offsets[object_id] = len(output)
        output.extend(f"{object_id} 0 obj\n".encode() + objects[object_id] + b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for object_id in sorted(objects):
        output.extend(f"{offsets[object_id]:010d} 00000 n \n".encode())
    output.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode())
    return bytes(output)


PATIENT_LEAFLET_LINES = [
    "DIPIRONA MONOIDRATADA",
    "II - INFORMAÇÕES AO PACIENTE",
    "1. PARA QUE ESTE MEDICAMENTO É",
    "INDICADO?",
    "Este medicamento é indicado como analgésico e antitérmico.",
    "2. COMO ESTE MEDICAMENTO FUNCIONA?",
    "A dipirona age no alívio da dor e da febre.",
    "3. QUANDO NÃO DEVO USAR ESTE MEDICAMENTO?",
    "Não use se tiver alergia à dipirona.",
    "4. O QUE DEVO SABER ANTES DE USAR ESTE MEDICAMENTO?",
    "Informe ao seu médico se estiver grávida.",
    "5. ONDE, COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO?",
    "Conservar em temperatura ambiente (entre 15 e 30 °C).",
    "6. COMO DEVO USAR ESTE MEDICAMENTO?",
    "Adultos: 1 comprimido até 4 vezes ao dia.",
    "7. O QUE DEVO FAZER QUANDO EU ME ESQUECER DE USAR ESTE MEDICAMENTO?",
    "Tome assim que lembrar.",
    "8. QUAIS OS MALES QUE ESTE MEDICAMENTO PODE ME CAUSAR?",
    "Reações alérgicas na pele.",
    "9. O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR DO QUE A INDICADA DESTE MEDICAMENTO?",
    "Procure socorro médico imediatamente.",
    "III - DIZERES LEGAIS",
    "Reg. MS 1.0043.0001",
]

PROFESSIONAL_LEAFLET_LINES = [
    "DIPIRONA MONOIDRATADA",
    "INFORMAÇÕES AO PROFISSIONAL DE SAÚDE",
    "1. INDICAÇÕES",
    "Analgésico e antitérmico.",
    "2. RESULTADOS DE EFICÁCIA",
    "Estudos clínicos demonstraram eficácia analgésica em adultos e crianças acima de três meses.",
    "3. CARACTERÍSTICAS FARMACOLÓGICAS",
    "A dipirona é um derivado pirazolônico com propriedades analgésicas, antipiréticas e espasmolíticas.",
    "8. POSOLOGIA E MODO DE USAR",
    "Adultos e adolescentes acima de 15 anos: 500 a 1000 mg até 4 vezes ao dia.",
]
