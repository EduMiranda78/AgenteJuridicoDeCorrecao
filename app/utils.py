import os
import subprocess
from docx import Document


def extract_text_from_doc(file):
    filename = file.filename.lower()
    temp_path = f"/tmp/{file.filename}"

    with open(temp_path, "wb") as f:
        f.write(file.file.read())

    try:
        if filename.endswith(".docx"):
            doc = Document(temp_path)
            texto = "\n".join(p.text for p in doc.paragraphs)
            return texto.strip()

        if filename.endswith(".doc"):
            result = subprocess.run(
                ["antiword", temp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(result.stderr)

            return result.stdout.strip()

        raise ValueError("Formato de arquivo não suportado")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
