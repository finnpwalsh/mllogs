# Usage Guide

This guide covers experiment tracking, run management, querying, and model persistence with `mllogs`.

## 1. Initialization

Create an `MLLogs` instance:

```python
from mllogs import MLLogs

mll = MLLogs()
```

By default, `mllogs` stores its SQLite database and model files in `.mllogs/`.

To configure custom storage locations:

```python
mll = MLLogs(
    db_url="sqlite:///data/mllogs.db",
    file_url="data/models",
)
```

Close the database connection resources when finished:

```python
mll.close()
```

## 2. Experiments

Experiments organize related training runs.

### Create an experiment

```python
mll.create_experiment("ridge-regression")
```

Experiment names must be unique.

### List experiments

```python
experiments = mll.experiments()
```

Returns a pandas DataFrame containing experiment IDs, names, and creation timestamps.

### Delete an experiment

```python
mll.delete_experiment("ridge-regression")
```

Deleting an experiment does not delete its runs. Existing runs remain in the database with no associated experiment.

## 3. Tracking Runs

Use the `run()` context manager to track an individual training run.

```python
with mll.run("ridge-regression") as run_id:
    mll.log_param("alpha", 0.1)
    mll.log_metric("rmse", 0.42)
    mll.set_tag("dataset", "housing")
```

Each run receives a unique ID and records:

- Start and end timestamps
- Run status (`RUNNING`, `COMPLETE`, or `FAILED`)
- Parameters, metrics, and tags
- Optional saved model

Runs are automatically marked `COMPLETE` when the context exits successfully or `FAILED` if an exception occurs.

Only one run can be active per `MLLogs` instance at a time.

### Logging parameters

Parameters describe the configuration of a training run.

```python
mll.log_param("alpha", 0.1)
mll.log_param("fit_intercept", True)
mll.log_param("solver", "auto")
```

Supported parameter values are strings, integers, floats, booleans, and `None`.

### Logging metrics

Metrics record numerical model evaluation results.

```python
mll.log_metric("rmse", 0.42)
mll.log_metric("r2", 0.91)
```

### Setting tags

Tags provide additional descriptive information.

```python
mll.set_tag("dataset", "housing")
mll.set_tag("algorithm", "ridge")
```

Logging methods require an active run.

## 4. Querying Runs

`mllogs` provides a chainable query interface built on SQLAlchemy Core, with results returned as pandas DataFrames.

### Retrieve runs

Retrieve all runs:

```python
df = mll.runs().to_df()
```

Or retrieve runs for a specific experiment:

```python
df = mll.runs("ridge-regression").to_df()
```

Parameters, metrics, and tags are flattened into columns for easier analysis.

### Filter runs

Filter runs by column values:

```python
df = (
    mll.runs("ridge-regression")
    .filter("status", "COMPLETE")
    .to_df()
)
```

### Order runs

Sort by a recorded metric:

```python
df = (
    mll.runs("ridge-regression")
    .order_by("rmse", ascending=True)
    .to_df()
)
```

### Compare runs

Combine filtering and ordering to identify promising configurations:

```python
df = (
    mll.runs("ridge-regression")
    .filter("status", "COMPLETE")
    .order_by("rmse", ascending=True)
    .to_df()
)

print(df)
```

Query results can be analyzed using standard pandas operations.

## 5. Model Persistence

Models can be saved directly to training runs.

Each run supports one saved model.

### Save a model

```python
with mll.run("ridge-regression") as run_id:
    model.fit(X_train, y_train)

    mll.log_metric("rmse", 0.42)
    mll.save_model(model)
```

Joblib is the default serializer.

Alternatively, use Pickle:

```python
mll.save_model(model, format="pickle")
```

Saved models are stored on the local filesystem, while the database records the serialization format associated with the run.

### Load a model

Load a previously saved model using its run ID:

```python
model = mll.load_model(run_id)
```

The appropriate deserializer is selected automatically.

Only load models from trusted storage. Joblib and Pickle deserialization can execute arbitrary Python code.

## 6. End-to-End Example

For a complete training workflow, see [ridge_regression](../examples/ridge_regression.py).