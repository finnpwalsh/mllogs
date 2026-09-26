# mllogs

Local experiment logging for machine learning.

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

## Features

- Start, complete, and fail experiment runs
- Log parameters, metrics, and tags
- Persist run data to a local SQLite database
- Persist artifacts to local file storage
- Query saved runs and their logged data

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