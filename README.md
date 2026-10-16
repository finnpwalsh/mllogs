# mllogs

Lightweight experiment tracking and model persistence for machine learning.

`mllogs` helps developers track experiments, compare training runs, and save trained models without running a tracking server or external service.

Built with SQLite, SQLAlchemy Core, and pandas.

## Installation

Requires Python 3.11 or later.

```bash
pip install mllogs
```

## Quickstart

```python
from mllogs import MLLogs

mll = MLLogs()

mll.create_experiment("ridge-regression")

with mll.run("ridge-regression") as run_id:
    model.fit(X_train, y_train)

    mll.log_param("alpha", 0.1)
    mll.log_metric("rmse", 0.42)
    mll.save_model(model)

# Compare runs
df = mll.runs("ridge-regression").to_df()

# Load a saved model
model = mll.load_model(run_id)

mll.close()
```

## Features

- **Experiment tracking** — Organize training runs and log parameters, metrics, and tags.
- **Flexible querying** — Filter, sort, and compare runs using pandas DataFrames.
- **Model persistence** — Save and load trained models using Joblib or Pickle.
- **Local-first storage** — Store experiment metadata in SQLite and models on the local filesystem.

## Configuration

By default, `mllogs` stores its database and models in `.mllogs/`.

```text
.mllogs/
├── mllogs.db
└── models/
    └── <run_id>.joblib
```

Custom storage locations can be specified:

```python
mll = MLLogs(
    db_url="sqlite:///data/mllogs.db",
    file_url="data/models",
)
```

## License

MIT License.