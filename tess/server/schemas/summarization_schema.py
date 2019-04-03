SUMMARIZATION_SCHEMA = {
    "type": "object",
    "properties": {
        "task": {
            "type": "string",
            "enum": ["summarization"]
        },
        "method": {
            "type": "string",
            "enum": ["extractive", "abstractive"],
            "default": "extractive"
        },
        "algorithm": {
            "type": "string",
            "enum": ["summarunner", "pgn", "fastabsrl"]
        },
        "text": {
            "type": "string"
        }
    },
    "required": ["task", "method", "algorithm", "text"]
}

SUMMARIZATION_ALGORITHMS = {
    'abstractive': {'pgn', 'fastabsrl'},
    'extractive': {'summarunner'}
}
