import google.generativeai as genai

class AgenteJuridico:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        genai.configure(api_key="AIzaSyAjKdh8hxRov5_FsAyOLwrcLs9GZfIwPUQ")
        self.model_gemini = genai.GenerativeModel('gemini-2.5-flash')

    def analisar_gemini(self, texto: str) -> str:
        prompt_final = self.system_prompt.format(texto_do_contrato=texto)
        try:
            response = self.model_gemini.generate_content(prompt_final)
            return response.text
        except Exception as e:
            return f"❌ Erro Gemini: {str(e)}"
