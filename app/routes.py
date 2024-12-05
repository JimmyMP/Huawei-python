from flask import Blueprint, render_template, request, jsonify
import requests
import os

main = Blueprint('main', __name__)
import html

def sanitize_text(text):
    if not text:
        return 'No disponible'
    return html.escape(text).replace('\n', ' ')

# Ruta para la página de inicio
@main.route('/')
def home():
    return render_template('home.html')

# Ruta para la primera página (Mapa Climático)
@main.route('/climate-map')
def climate_map():
    return render_template('index.html')

# Ruta para la segunda página (Mapa Alternativo)
@main.route('/second-map')
def second_map():
    return render_template('second_page.html')
# Ruta para tercer página (Mapa Alternativo)
@main.route('/third-map')
def third_map():
    return render_template('third_page.html')
# Endpoint para obtener datos climáticos desde la API externa
@main.route('/api/climate', methods=['GET'])
def get_climate_data():
    try:
        # Reemplaza esta URL con tu endpoint real
        api_url = "https://3y5g7n7qstgbgs5k53elapbjce0kvera.lambda-url.us-east-1.on.aws/"
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para filtrar datos climáticos
@main.route('/api/filter', methods=['POST'])
def filter_data():
    # Obtener filtros desde el cuerpo de la solicitud
    city = request.json.get('city', '').lower()
    temp_max = request.json.get('tempMax', None)
    temp_min = request.json.get('tempMin', None)
    precip_min = request.json.get('precipMin', None)
    precip_max = request.json.get('precipMax', None)

    try:
        # Obtener los datos climáticos
        api_url = "https://3y5g7n7qstgbgs5k53elapbjce0kvera.lambda-url.us-east-1.on.aws/"
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json().get('climate', [])

        # Filtrar los datos
        filtered = [
            item for item in data
            if (not city or city in item['city'].lower()) and
               (not temp_max or float(item['maxt']) <= float(temp_max)) and
               (not temp_min or float(item['mint']) >= float(temp_min)) and
               (not precip_min or float(item['precipitation']) >= float(precip_min)) and
               (not precip_max or float(item['precipitation']) <= float(precip_max))
        ]

        return jsonify(filtered)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Nuevo Endpoint para recomendaciones
@main.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    if request.method != 'POST':
        return jsonify({"error": "Método no permitido"}), 405

    # Obtener parámetros del cuerpo de la solicitud
    data = request.json
    city = data.get('city')
    maxt = data.get('maxt')
    mint = data.get('mint')
    precipitation = data.get('precipitation')
    description = data.get('description')

    # Validar parámetros requeridos
    if not city or not maxt or not mint or not precipitation:
        return jsonify({"error": "Faltan parámetros requeridos: ciudad, temperatura máxima, temperatura mínima y precipitación son obligatorios"}), 400

    # Construir el mensaje de solicitud para OpenAI
    try:
        openai_payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un experto en meteorología agrícola y análisis climático para cultivos."
                },
                {
                    "role": "user",
                    "content": f"""Proporciona recomendaciones detalladas y prácticas basadas en las condiciones climáticas reportadas para la ciudad '{city}' con los siguientes parámetros:
                                    - Temperatura máxima: '{maxt}'°C
                                    - Temperatura mínima: '{mint}'°C
                                    - Precipitación: '{precipitation}' mm
                                    
                                    Considera lo siguiente:
                                    - descripción: '{description}'
                                    - Sugerencias para optimizar el manejo de cultivos en estas condiciones.
                                    - Cultivos más adecuados para este clima.
                                    - Métodos para mitigar los riesgos climáticos, como heladas, sequías o exceso de lluvia.
                                    - Consejos prácticos para agricultores con experiencia básica.
                                    
                                    Responde en un lenguaje sencillo y directo, con un máximo de 200 palabras y 1250 caracteres."""
                }
            ],
            "max_tokens": 500,
        }

        # Llamar a la API de OpenAI
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
            },
            json=openai_payload
        )

        # Manejar errores de la API
        if response.status_code != 200:
            return jsonify({
                "error": "Error al obtener la respuesta de OpenAI",
                "details": response.json()
            }), response.status_code

        # Extraer las recomendaciones
        recommendations = response.json()["choices"][0]["message"]["content"].strip()
        return jsonify({"recommendations": recommendations}), 200

    except Exception as e:
        return jsonify({"error": "Error interno del servidor", "details": str(e)}), 500
@main.route('/api/news', methods=['GET'])
def get_news():
    try:
        api_url = "https://vgopt55vfhhpoa3yclphhhw2i40idexu.lambda-url.us-east-1.on.aws/"
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        # Validar los datos y asignar valores predeterminados
        for news in data.get('news', []):
            news['title'] = news.get('title', 'Sin título')
            news['category'] = news.get('category', 'Sin categoría')
            news['publish_date'] = news.get('publish_date', 'Fecha no disponible')

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route('/api/news-recommendations', methods=['POST'])
def news_recommendations():
    data = request.json
    title = sanitize_text(data.get('title'))
    category = sanitize_text(data.get('category'))
    publish_date = sanitize_text(data.get('publish_date'))

    if not title or not publish_date:
        return jsonify({"error": "El título y la fecha de publicación son requeridos."}), 400

    try:
        openai_payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un analista experto en noticias agrícolas, económicas y políticas para una empresa agrícola peruana."
                },
                {
                    "role": "user",
                    "content": f"""
                        Analiza la noticia:
                        Título: '{title}'
                        Categoría: '{category}'
                        Fecha: '{publish_date}'
                        Proporciona recomendaciones en 200 palabras como máximo, dandome insight de que me beneficia o perjudica esta noticia.
                    """
                },
            ],
            "max_tokens": 500,
        }

        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
            },
            json=openai_payload
        )
        recommendations = response.json()["choices"][0]["message"]["content"].strip()
        return jsonify({"recommendations": recommendations})
    except Exception as e:
        return jsonify({"error": "Error al obtener las recomendaciones", "details": str(e)}), 500
@main.route('/api/pests', methods=['GET'])
def get_pests():
    try:
        api_url = "https://wapp5fewnmgakrn5yzo2u5nsdm0auxzy.lambda-url.us-east-1.on.aws/"
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@main.route('/api/pests-recommendations', methods=['POST'])
def pests_recommendations():
    data = request.json
    pest = data.get('pest')
    region = data.get('region')
    date = data.get('date')

    if not pest or not region or not date:
        return jsonify({"error": "La plaga, la región y la fecha son requeridas."}), 400

    try:
        openai_payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un experto en agricultura y control de plagas."
                },
                {
                    "role": "user",
                    "content": f"""
                        Proporciona recomendaciones detalladas y prácticas para combatir la plaga denominada '{pest}', reportada en la región '{region}' el día '{date}'.
                        Considera métodos biológicos, químicos, y prácticas culturales.
                        Responde en 200 palabras como máximo.
                    """
                },
            ],
            "max_tokens": 500,
        }

        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
            },
            json=openai_payload
        )
        recommendations = response.json()["choices"][0]["message"]["content"].strip()
        return jsonify({"recommendations": recommendations})
    except Exception as e:
        return jsonify({"error": "Error al obtener las recomendaciones", "details": str(e)}), 500
