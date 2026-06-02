from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Conexión MongoDB Atlas
try:

    client = MongoClient(
        os.getenv("MONGODB_URI", "mongodb+srv://luisatomas:123@lab-1.spstu5x.mongodb.net/?retryWrites=true&w=majority&appName=lab-1")
    )

    db = client["UniversidadDB"]
    coleccion = db["MonitoreoAulas"]

    print("Conectado exitosamente a MongoDB Atlas")

except Exception as e:

    print(f"Error de conexión: {e}")

# ==========================
# SERVIR FRONTEND
# ==========================

@app.route('/')
def index():
    return send_file('index.html')

# ==========================
# RECIBIR DATOS DEL SENSOR
# ==========================

@app.route('/sensor', methods=['POST'])
def recibir():

    try:

        datos = request.json

        datos['fecha_registro'] = datetime.now()

        id_insertado = coleccion.insert_one(datos).inserted_id

        print(
            f"Dato guardado de {datos.get('aula', 'Desconocida')}: "
            f"T={datos.get('temperatura')}°C, "
            f"H={datos.get('humedad')}%"
        )

        return jsonify({
            "mensaje": "Guardado",
            "id": str(id_insertado)
        }), 201

    except Exception as e:

        print(f"Error al procesar datos: {e}")

        return jsonify({
            "error": str(e)
        }), 400

# ==========================
# ENVIAR ÚLTIMO DATO AL FRONTEND
# ==========================

@app.route('/datos', methods=['GET'])
def enviar_datos():

    ultimo_dato = coleccion.find_one(
        sort=[('fecha_registro', -1)]
    )

    if ultimo_dato:

        ultimo_dato['_id'] = str(ultimo_dato['_id'])

        return jsonify(ultimo_dato), 200

    return jsonify({
        "error": "No hay datos"
    }), 404

# ==========================
# SALONES DISPONIBLES

@app.route('/salones', methods=['GET'])
def obtener_salones():
    try:
        salones = coleccion.distinct("aula")
        salones = [s for s in salones if s is not None]
        salones.sort()
        return jsonify(salones), 200
    except Exception as e:
        print(f"Error al obtener salones: {e}")
        return jsonify({
            "error": str(e)
        }), 400

# ==========================
# REGISTROS POR SALÓN

@app.route('/salon/<aula>', methods=['GET'])
def obtener_salon(aula):
    try:
        registros = list(coleccion.find(
            {"aula": aula},
            sort=[('fecha_registro', -1)]
        ).limit(50))

        for registro in registros:
            registro['_id'] = str(registro['_id'])
            if isinstance(registro.get('fecha_registro'), datetime):
                registro['fecha_registro'] = registro['fecha_registro'].isoformat()

        return jsonify(registros), 200
    except Exception as e:
        print(f"Error al obtener registros del salón {aula}: {e}")
        return jsonify({
            "error": str(e)
        }), 400

# ==========================
# PROMEDIOS DE TEMPERATURA Y HUMEDAD
# ==========================

@app.route('/promedio', methods=['GET'])
def obtener_promedio():
    try:
        # Agregar documentos y calcular promedio global
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "temp_promedio": {"$avg": "$temperatura"},
                    "hum_promedio": {"$avg": "$humedad"},
                    "total_registros": {"$sum": 1}
                }
            }
        ]
        
        resultado = list(coleccion.aggregate(pipeline))
        
        if resultado:
            datos = resultado[0]
            return jsonify({
                "temperatura_promedio": round(datos["temp_promedio"], 2),
                "humedad_promedio": round(datos["hum_promedio"], 2),
                "total_registros": datos["total_registros"]
            }), 200
        
        return jsonify({
            "error": "No hay datos para calcular promedio"
        }), 404
        
    except Exception as e:
        print(f"Error al calcular promedio: {e}")
        return jsonify({
            "error": str(e)
        }), 400

@app.route('/salon/<aula>/promedio', methods=['GET'])
def obtener_promedio_salon(aula):
    try:
        pipeline = [
            {"$match": {"aula": aula}},
            {
                "$group": {
                    "_id": None,
                    "temp_promedio": {"$avg": "$temperatura"},
                    "hum_promedio": {"$avg": "$humedad"},
                    "total_registros": {"$sum": 1}
                }
            }
        ]
        
        resultado = list(coleccion.aggregate(pipeline))
        
        if resultado:
            datos = resultado[0]
            return jsonify({
                "temperatura_promedio": round(datos["temp_promedio"], 2),
                "humedad_promedio": round(datos["hum_promedio"], 2),
                "total_registros": datos["total_registros"]
            }), 200
        
        return jsonify({
            "error": "No hay datos para calcular promedio en este salón"
        }), 404
        
    except Exception as e:
        print(f"Error al calcular promedio del salón {aula}: {e}")
        return jsonify({
            "error": str(e)
        }), 400

# ==========================
# MÁXIMAS TEMPERATURA Y HUMEDAD
# ==========================

@app.route('/maximos', methods=['GET'])
def obtener_maximos():
    try:
        # Agregar documentos y encontrar máximos globales
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "temp_maxima": {"$max": "$temperatura"},
                    "hum_maxima": {"$max": "$humedad"}
                }
            }
        ]
        
        resultado = list(coleccion.aggregate(pipeline))
        
        if resultado:
            datos = resultado[0]
            return jsonify({
                "temperatura_maxima": round(datos["temp_maxima"], 2),
                "humedad_maxima": round(datos["hum_maxima"], 2)
            }), 200
        
        return jsonify({
            "error": "No hay datos para calcular máximos"
        }), 404
        
    except Exception as e:
        print(f"Error al calcular máximos: {e}")
        return jsonify({
            "error": str(e)
        }), 400

@app.route('/salon/<aula>/maximos', methods=['GET'])
def obtener_maximos_salon(aula):
    try:
        pipeline = [
            {"$match": {"aula": aula}},
            {
                "$group": {
                    "_id": None,
                    "temp_maxima": {"$max": "$temperatura"},
                    "hum_maxima": {"$max": "$humedad"}
                }
            }
        ]
        
        resultado = list(coleccion.aggregate(pipeline))
        
        if resultado:
            datos = resultado[0]
            return jsonify({
                "temperatura_maxima": round(datos["temp_maxima"], 2),
                "humedad_maxima": round(datos["hum_maxima"], 2)
            }), 200
        
        return jsonify({
            "error": "No hay datos para calcular máximos en este salón"
        }), 404
        
    except Exception as e:
        print(f"Error al calcular máximos del salón {aula}: {e}")
        return jsonify({
            "error": str(e)
        }), 400

# ==========================
# INICIAR SERVIDOR
# ==========================

if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=int(os.getenv("PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", False)
    )