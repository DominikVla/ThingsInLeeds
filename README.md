# ThingsInLeeds
An AI-powered natural-language venue search for Leeds.

## Run locally

1. Start MySQL and import `database/schema.sql`, then `database/seed.sql`.
2. Install dependencies: `pip install -r requirements.txt`
3. Start Ollama and pull the configured model: `ollama pull llama3.2:3b`
4. Run the app: `uvicorn app.main:app --reload`
5. Open `http://127.0.0.1:8000`

Configure `DATABASE_URL`, `OLLAMA_URL`, and `OLLAMA_MODEL` as environment variables.

## ML pipeline

- Generate training examples: `python ml_pipeline/dataset_generator.py`
- Fine-tune with QLoRA: `pip install -r requirements-ml.txt` then `python ml_pipeline/finetune_qlora.py`
- Evaluate: `python ml_pipeline/evaluate.py --dataset ml_pipeline/test_dataset.jsonl`
