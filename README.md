# Automated Audio Response System

This system allows matching text queries with audio files using Natural Language Processing (NLP) techniques.

## Project Structure

The project has been reorganized into a modular structure to facilitate maintenance and future modifications:

```
sistem-audios/
├── app/                    # Main application package
│   ├── config/             # Application configuration
│   │   ├── __init__.py
│   │   └── settings.py     # Configuration variables
│   ├── models/             # Data models
│   │   ├── __init__.py
│   │   ├── enums.py        # Enumerations and types
│   │   └── schemas.py      # Pydantic schemas
│   ├── routes/             # API routes
│   │   ├── __init__.py
│   │   └── api.py          # API endpoints
│   ├── services/           # Application services
│   │   ├── __init__.py
│   │   └── audio_matcher.py # Main matcher logic
│   ├── __init__.py
│   └── main.py             # FastAPI application
├── audios/                 # Audio files
├── audio_base.json         # Audio database
├── main.py                 # Application entry point
├── requirements.txt        # Project dependencies
└── .env                    # Environment variables (optional)
```

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Execution

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Matching Methods

The system implements four different methods for matching text queries with audio files:

### 1. Individual (`individual`)

Compares the query with each individual description of each audio and selects the best match.

- **Advantages**: High precision when there are specific descriptions that exactly match the query.
- **Disadvantages**: May miss matches if the query uses synonyms or different phrases.
- **Recommended use**: When descriptions are very specific and varied.

### 2. Combined (`combined`)

Combines all descriptions of each audio into a single text and compares the query with this combined text.

- **Advantages**: Captures the general context of an audio.
- **Disadvantages**: May dilute the relevance of specific matches.
- **Recommended use**: When descriptions complement each other to form a broader context.

### 3. Hybrid (`hybrid`)

Combines the results of the individual and combined methods with weights of 70% and 30% respectively.

- **Advantages**: Balances the precision of the individual method with the context of the combined method.
- **Disadvantages**: May be less precise than the individual method in very specific cases.
- **Recommended use**: For general use, offers a good balance between precision and context.

### 4. Maximum (`max`)

Selects the best result between the individual and combined methods.

- **Advantages**: Takes advantage of the best of both methods.
- **Disadvantages**: May be less predictable in terms of which method will be used.
- **Recommended use**: When maximum confidence in the match is needed.

## Main Endpoints

- `GET /`: Basic API information
- `POST /api/process`: Processes a text query and returns the most appropriate audio
  - Parameters:
    - `text`: Query text
    - `method`: Matching method to use (individual, combined, hybrid, max)
- `GET /api/health`: Service health check
- `GET /api/stats`: System statistics
- `POST /api/admin/add-audio`: Adds a new audio
- `POST /api/admin/update-threshold`: Updates the similarity threshold

## Configuration

Configurations can be modified in `app/config/settings.py` or through environment variables:

- `SIMILARITY_THRESHOLD`: Similarity threshold (default: 0.7)
- `MAX_AUDIO_DESCRIPTIONS`: Maximum number of descriptions per audio (default: 5)
- `DEBUG_MODE`: Debug mode (default: false)
- `PORT`: Server port (default: 8000)

## API Response

The API response includes:

```json
{
  "response": "audio_name.ogg",
  "confidence": 0.85,
  "method": "hybrid",
  "message": "Match found with confidence 0.85 using hybrid method",
  "status": "success"
}
```

In debug mode, additional details such as scores for all matches are also included.
