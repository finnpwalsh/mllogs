# mllogs

Lightweight experiment tracking and model registry for machine learning.

## Installation

```bash
pip install mllogs
```

## Usage

Track a run:

```python
from mllogs import MLLogs

mll = MLLogs()

mll.start_run()

mll.log_param("learning_rate", 0.01)
mll.log_metric("accuracy", 0.92)
mll.set_tag("model", "logistic_regression")
mll.save_artifact("model", model, "joblib")

run = mll.complete_run()
```

Query run data:

```python
mll.query.get_run(run.id)
mll.query.get_params(run.id)
mll.query.get_metrics(run.id)
mll.query.get_tags(run.id)
```

Load saved artifacts:

```python
mll.query.list_artifacts(run.id)
model = mll.query.load_artifact(run.id, "model")
```

Register and version persisted model artifacts:

```python
model_ref = mll.save_artifact("model", model, "joblib")
mll.registry.create_version("credit-risk", model_ref)

latest = mll.registry.get_latest_version("credit-risk")
```

`create_version` automatically registers the model if it does not alreadt exist.

You can also register a model explicitly:

```python 
mll.registry.register_model("credit-risk")
```

And load a specific model version:
```
python
version = mll.registry.get_version(
    model_name="credit-risk",
    version=1,
)

Model version reference persisted artifacts, while artifact storage and model registration remain separate parts of the ML lifecycle.
```

## Features

- Start, complete, and fail experiment runs
- Log parameters, metrics, and tags
- Persist run data to a local SQLite database
- Persist artifacts to local file storage
- Query saved runs and their logged data
- Register models and create versioned references to persisted model artifacts

## Development

Install from source with development dependencies:

```bash
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

## License

MIT