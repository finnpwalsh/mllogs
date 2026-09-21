# mllogs

Local experiment logging for machine learning.

## Installation

```bash
pip install mllogs
```

## Usage

```python
from mllogs import MLLogsClient

client = MLLogsClient()

client.start_run(
    name="baseline",
    run_type="training",
)

client.log_param("learning_rate", 0.01)
client.log_metric("accuracy", 0.92)
client.set_tag("model", "logistic_regression")

run = client.end_run()

client.list_runs()
```

Retrieve or delete a saved run:

```python
client.get_run(run.id)
client.delete_run(run.id)
```

## Features

- Start and end experiment runs
- Log parameters, metrics, and tags
- Persist completed runs to a local SQLite database
- Load, list, and delete saved runs

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