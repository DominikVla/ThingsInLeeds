# ThingsInLeeds
An AI-powered natural-language venue search for Leeds.

## Run locally

1. Start MySQL and import `database/schema.sql`, then `database/seed.sql`.
2. Install dependencies: `pip install -r requirements.txt`
3. Start Ollama and pull the configured model: `ollama pull llama3.2:3b`
4. Run the app: `uvicorn app.main:app --reload`
5. Open `http://127.0.0.1:8000`

Configure `DATABASE_URL`, `READ_ONLY_DATABASE_URL`, `OLLAMA_URL`, and `OLLAMA_MODEL` as environment variables.

## Read-only database copy

The application never sends database requests to `DATABASE_URL`. It uses
`READ_ONLY_DATABASE_URL` and blocks every SQL statement except read statements
at the SQLAlchemy engine level.

Create or refresh the copy after changing the main database:

```powershell
.\database\create_read_only_copy.ps1 -DropExisting
```

The script defaults to copying `things_in_leeds` into
`things_in_leeds_read_only`. Override names with `-SourceDatabase` and
`-ReadOnlyDatabase`. If `READ_ONLY_DATABASE_URL` is not set, the app derives the
`_read_only` database name from `DATABASE_URL`.

For MySQL, use a dedicated least-privilege read-only user and grant it only
`SELECT` on the copy, for example:

```sql
CREATE USER 'things_readonly'@'%' IDENTIFIED BY '<strong-password>'; 
GRANT SELECT ON things_in_leeds_read_only.* TO 'things_readonly'@'%';
FLUSH PRIVILEGES;
```

Then set `READ_ONLY_DATABASE_URL` to a URL containing that user.

## ML pipeline

- Generate training examples: `python ml_pipeline/dataset_generator.py`
- Fine-tune with QLoRA: `pip install -r requirements-ml.txt` then `python ml_pipeline/finetune_qlora.py`
- Evaluate: `python ml_pipeline/evaluate.py --dataset ml_pipeline/test_dataset.jsonl`
