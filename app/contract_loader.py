import subprocess
from docx import Document

def load_word(path: str) -> str:
    if path.lower().endswith(".docx"):
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)

    if path.lower().endswith(".doc"):
        result = subprocess.run(
            ["antiword", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout

    raise ValueError("Formato não suportado")
