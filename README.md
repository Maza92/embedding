# Automated Audio Response System

Este sistema permite hacer coincidir consultas de texto con archivos de audio utilizando técnicas de Procesamiento de Lenguaje Natural (NLP).

## Estructura del Proyecto

El proyecto ha sido reorganizado en una estructura modular para facilitar el mantenimiento y futuras modificaciones:

```
sistem-audios/
├── app/                    # Paquete principal de la aplicación
│   ├── config/             # Configuración de la aplicación
│   │   ├── __init__.py
│   │   └── settings.py     # Variables de configuración
│   ├── models/             # Modelos de datos
│   │   ├── __init__.py
│   │   ├── enums.py        # Enumeraciones y tipos
│   │   └── schemas.py      # Esquemas Pydantic
│   ├── routes/             # Rutas de la API
│   │   ├── __init__.py
│   │   └── api.py          # Endpoints de la API
│   ├── services/           # Servicios de la aplicación
│   │   ├── __init__.py
│   │   └── audio_matcher.py # Lógica principal del matcher
│   ├── __init__.py
│   └── main.py             # Aplicación FastAPI
├── audios/                 # Archivos de audio
├── audio_base.json         # Base de datos de audio
├── main.py                 # Punto de entrada de la aplicación
├── requirements.txt        # Dependencias del proyecto
└── .env                    # Variables de entorno (opcional)
```

## Instalación

1. Clonar el repositorio
2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python main.py
```

La API estará disponible en `http://localhost:8000`

## Métodos de Matching

El sistema implementa cuatro métodos diferentes para hacer coincidir consultas de texto con archivos de audio:

### 1. Individual (`individual`)

Compara la consulta con cada descripción individual de cada audio y selecciona la mejor coincidencia.

- **Ventajas**: Alta precisión cuando hay descripciones específicas que coinciden exactamente con la consulta.
- **Desventajas**: Puede perder coincidencias si la consulta usa sinónimos o frases diferentes.
- **Uso recomendado**: Cuando las descripciones son muy específicas y variadas.

### 2. Combinado (`combined`)

Combina todas las descripciones de cada audio en un solo texto y compara la consulta con este texto combinado.

- **Ventajas**: Captura el contexto general de un audio.
- **Desventajas**: Puede diluir la relevancia de coincidencias específicas.
- **Uso recomendado**: Cuando las descripciones se complementan entre sí para formar un contexto más amplio.

### 3. Híbrido (`hybrid`)

Combina los resultados de los métodos individual y combinado con pesos de 70% y 30% respectivamente.

- **Ventajas**: Equilibra la precisión del método individual con el contexto del método combinado.
- **Desventajas**: Puede ser menos preciso que el método individual en casos muy específicos.
- **Uso recomendado**: Para uso general, ofrece un buen equilibrio entre precisión y contexto.

### 4. Máximo (`max`)

Selecciona el mejor resultado entre los métodos individual y combinado.

- **Ventajas**: Aprovecha lo mejor de ambos métodos.
- **Desventajas**: Puede ser menos predecible en términos de qué método se utilizará.
- **Uso recomendado**: Cuando se necesita la máxima confianza posible en la coincidencia.

## Endpoints Principales

- `GET /`: Información básica de la API
- `POST /api/process`: Procesa una consulta de texto y devuelve el audio más apropiado
  - Parámetros:
    - `text`: Texto de la consulta
    - `method`: Método de matching a utilizar (individual, combined, hybrid, max)
- `GET /api/health`: Verificación de salud del servicio
- `GET /api/stats`: Estadísticas del sistema
- `POST /api/admin/add-audio`: Añade un nuevo audio
- `POST /api/admin/update-threshold`: Actualiza el umbral de similitud

## Configuración

Las configuraciones se pueden modificar en `app/config/settings.py` o a través de variables de entorno:

- `SIMILARITY_THRESHOLD`: Umbral de similitud (predeterminado: 0.7)
- `MAX_AUDIO_DESCRIPTIONS`: Número máximo de descripciones por audio (predeterminado: 100)
- `DEBUG_MODE`: Modo de depuración (predeterminado: false)
- `PORT`: Puerto del servidor (predeterminado: 8000)

## Respuesta de la API

La respuesta de la API incluye:

```json
{
  "response": "nombre_del_audio.ogg",
  "confidence": 0.85,
  "method": "hybrid",
  "message": "Match encontrado con confianza 0.85 usando método hybrid",
  "status": "success"
}
```

En modo de depuración, también se incluyen detalles adicionales como las puntuaciones de todas las coincidencias.
