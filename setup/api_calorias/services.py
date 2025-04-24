import google.generativeai as genai
import json
from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

NUTRITION_CONTEXT = (
    "Você é um assistente de nutrição. O usuário vai inserir o nome de um alimento seguido de um número, "
    "que representa a quantidade em gramas. Sua tarefa é retornar um objeto JSON com os seguintes campos: "
    "'food', 'grams', 'calories', 'proteins_g', 'carbohydrates_g' e 'fats_g'. "
    "Baseie sua resposta proporcionalmente na quantidade informada. Sempre responda em inglês e retorne apenas o JSON."
)

def analyze_text_input(text_input):
    model = genai.GenerativeModel('gemini-2.0-flash')
    chat = model.start_chat(history=[{"role": "user", "parts": [NUTRITION_CONTEXT]}])
    response = chat.send_message(text_input)
    
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        # Tentar extrair JSON da resposta se não for puro
        start = response.text.find('{')
        end = response.text.rfind('}') + 1
        json_str = response.text[start:end]
        return json.loads(json_str)

def analyze_audio_input(audio_file):
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    prompt = (
        "Este é um áudio onde uma pessoa descreve alimentos e as quantidades consumidas em gramas. "
        "Interprete o áudio e retorne uma lista JSON com os alimentos e suas quantidades da seguinte forma:"
         "que representa a quantidade em gramas. Sua tarefa é retornar um objeto JSON com os seguintes campos: "
        "'food', 'grams', 'calories', 'proteins_g', 'carbohydrates_g' e 'fats_g'. "
        "Baseie sua resposta proporcionalmente na quantidade informada. Sempre responda em inglês e retorne apenas o JSON."
        "Se não fornecer as gramas transcreva apenas os alimentos e retorne uma lista JSON."
    )
    
    response = model.generate_content([
        prompt,
        {
            "mime_type": "audio/mpeg",
            "data": audio_file.read()
        }
    ])
    
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        start = response.text.find('[')
        end = response.text.rfind(']') + 1
        json_str = response.text[start:end]
        return json.loads(json_str)

def analyze_image_input(image_file):
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    
    prompt = (
        "Este é uma imagem onde uma pessoa tirou uma foto de alimentos. "
        "Interprete a imagem e retorne uma lista JSON com os alimentos da seguinte forma:"
        "que representa a quantidade em gramas. Sua tarefa é retornar um objeto JSON com os seguintes campos: "
        "'food', 'grams', 'calories', 'proteins_g', 'carbohydrates_g' e 'fats_g'. "
        "Baseie sua resposta proporcionalmente na quantidade informada. Sempre responda em inglês e retorne apenas o JSON."
        "Se não fornecer as gramas transcreva apenas os alimentos e retorne uma lista JSON."

    )
    
    response = model.generate_content([
        {
            "mime_type": image_file.content_type,
            "data": image_file.read()
        },
        prompt
    ])
    
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        start = response.text.find('[')
        end = response.text.rfind(']') + 1
        json_str = response.text[start:end]
        return json.loads(json_str)