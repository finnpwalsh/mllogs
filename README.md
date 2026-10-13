# mllogs

Local experiment tracking and model registry for machine learning.


## Why `mllogs`?

`mllogs` is built for developers who want structured experiment tracking without running a separate tracking server or external service. It provides a simple local workflow for tracking experiments, runs, parameters, metrics, artifacts, and model versions using SQLite and the filesystem.

Use it when your training code has outgrown ad hoc dictionaries, folders, and filenames, but you do not need the infrastructure of a larger ML platform.


## Contents

- [Installation](#installation)
- [Quickstart](#quickstart)
- [Usage](#usage) 
  - [Query experiments and runs](#query-experiments-and-runs)
  - [Load saved artifacts](#load-saved-artifacts)
  - [Register and version models](#register-and-version-models)
  - [Assign model aliases](#assign-model-aliases)
  - [Load registered models](#load-registered-models)
- [Configure local storage](#configure-local-storage)
- [Features](#features)
- [Development](#development)
- [License](#license)


## Installation

```bash
pip install mllogs
```


## Quickstart

Track multiple model configurations and compare their results.

```python
from mllogs import MLLogs
from sklearn.datasets import load_diabetes
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

# Prepare data
X, y = load_diabetes(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create experiment
mll = MLLogs()
experiment = mll.create_experiment("ridge-tuning")

best_mse = float("inf")
best_model_ref = None

# Track different configurations
for alpha in [0.1, 1.0, 10.0]:
    mll.start_run(experiment.name)

    model = Ridge(alpha=alpha)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)

    mll.log_param("alpha", alpha)
    mll.log_metric("mse", mse)

    mll.save_artifact("predictions", predictions, "npy")
    model_ref = mll.save_artifact("model", model, "joblib")

    mll.complete_run()

    if mse < best_mse:
        best_mse = mse
        best_model_ref = model_ref
```

Each configuration creates a separate run within the same experiment, preserving its parameters, metrics, and trained model.


## Usage

### Query experiments and runs

Retrieve experiments and inspect previously recorded runs.

```python
mll.query.list_experiments()
runs = mll.query.list_runs(experiment.name)

run = runs[0]
mll.query.get_run(run.id)
mll.query.get_params(run.id)
mll.query.get_metrics(run.id)
mll.query.get_tags(run.id)
```

### Load saved artifacts

Load a previously trained model from its associated run.

```python
mll.query.list_artifacts(run.id)

predictions = mll.query.load_artifact(run.id, "predictions")
model = mll.query.load_artifact(run.id, "model")
```

#### Supported artifact formats

`mllogs` supports saving and loading artifacts in the following formats:

| Format | Common use cases |
| ------ | ---------------- |
| JSON (`.json`) | Dictionaries, configurations, metadata |
| CSV (`.csv`) | Predictions, tabular data |
| Parquet (`.parquet`) | DataFrames, larger datasets |
| Pickle (`.pkl`) | Serialized Python objects, models |
| NumPy (`.npy`) | Arrays, embeddings |
| Joblib (`.joblib`) | Trained models, Python objects |

Specify the format when saving an artifact:

```python
mll.save_artifact("predictions", predictions, "npy")
mll.save_artifact("model", model, "joblib")
```

Artifacts are associated with individual runs and can be loaded via `mll.query.load_artifact()`.

**Note:** Only load Pickle or Joblib from trusted sources, since deserialization can execute arbitrary code.

### Register and version models

Register the best-performing model and create its first version.

```python
mll.registry.create_version("diabetes-ridge", best_model_ref)
```

`create_version` automatically registers the model if it does not already exist. Subsequent versions can reference new model artifacts without overwriting previous versions.

Retrieve the latest or a specific model version:

```python
latest = mll.registry.get_latest_version("diabetes-ridge")

version = mll.registry.get_version(
    model_name="diabetes-ridge",
    version=1,
)
```

### Assign model aliases

Assign a stable alias such as `champion` to a model version.

```python
mll.registry.set_alias(version, "champion")
```

Aliases can be reassinged as new model versions are created, allowing application code to refer to a role such as `champion` instead of a fixed number.

Retrieve an alias or resolve it to its associated model version:

```python
alias = mll.registry.get_alias("diabetes-ridge", "champion")

champion = mll.registry.get_version_by_alias("diabetes-ridge", "champion")
```

Aliases are scoped to individual registered models, so different models can independently use aliases such as `champion`, `staging`, or `candidate`.

### Load registered models

Load a registered model directly without manually retrieving its version or associated artifact.

By default, `load_model()` loads the latest version:

```python
model = mll.registry.load_model("diabetes-ridge")
```

Load a specific version:

```python
model = mll.registry.load_model("diabetes-ridge", version=1)
```

Or load a model by its alias:

```python
model = mll.registry.load_model("diabetes-ridge", alias="champion")
```

`load_model()` resolves the requested model version, retrieves its associated artifact, and returns the deserialized Python object.

The `version` and `alias` arguments are mutually exclusive. If neither is provided, the latest version is loaded.


## Configure local storage

By default, `mllogs` stores its SQLite database and artifacts in the `.mllogs` directory.

Specify a custom storage directory when initializing `MLLogs`:

```python
mll = MLLogs(storage_dir="./experiments")
```

The database and artifacts will be stored together:

```
experiments/
    mllogs.db
    artifacts/
```


## Features

- Create experiments to organize related machine learning runs
- Start, complete, and fail runs
- Log parameters, metrics, and tags
- Persist run metadata to a local SQLite database
- Save and load artifacts in multiple formats using local file storage
- Query experiments, runs, and logged data
- Register models and create versioned references to persisted model artifacts
- Assign and reassign aliases to model versions
- Load registered models by latest version, specific version, or alias
- Configure the local storage directory


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