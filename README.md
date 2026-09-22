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

mll.tracker.start_run()

mll.tracker.log_param("learning_rate", 0.01)
mll.tracker.log_metric("accuracy", 0.92)
mll.tracker.set_tag("model", "logistic_regression")

run = mll.tracker.complete_run()
```

Query run data:

```python
mll.query.get_run(run.id)
mll.query.get_params(run.id)
mll.query.get_metrics(run.id)
mll.query.get_tags(run.id)
```

## Features

- Start, complete, and fail experiment runs
- Log parameters, metrics, and tags
- Persist run data to a local SQLite database
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