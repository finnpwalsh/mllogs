# Architecture

`mllogs` is a local-first experiment tracking library built around SQLAlchemy Core, SQLite, and filesystem-based model persistence.

The architecture separates experiment management, querying, database storage, and model serialization without requiring a tracking server.

## Overview

```text
MLLogs
├── Query / RunsQuery
│   └── SQLAlchemy Core
├── Database
│   └── SQLite
└── Model Persistence
    ├── LocalFileStore
    └── Serializers
        ├── Joblib
        └── Pickle
```

### MLLogs

`MLLogs` is the primary public interface.

It manages experiments and run lifecycles, logs parameters, metrics, and tags, and coordinates model saving and loading.

Runs are managed through a context manager that automatically records completion or failure.

### Query and RunsQuery

The query layer provides a chainable interface for retrieving experiment results.

- `Query` handles general SQL filtering, ordering, and execution.
- `RunsQuery` extends querying with run-specific behavior, including flattening parameters, metrics, and tags into pandas DataFrames.

Queries use SQLAlchemy Core and execute against the configured database.

### Database

`Database` manages the SQLAlchemy engine, initializes the schema, and handles database-specific configuration.

SQLite is the default backend, with foreign-key enforcement enabled.

SQLAlchemy Core is used for database operations rather than the ORM. Tables are defined using `Table`, `Column`, and `MetaData`, and queries are constructed with SQL expressions.

## Database Schema

```text
experiments
    │
    └── runs
          ├── params
          ├── metrics
          └── tags
```

| Table         | Purpose                                               |
| ------------- | ----------------------------------------------------- |
| `experiments` | Experiment names and creation timestamps              |
| `runs`        | Run identifiers, timestamps, status, and model format |
| `params`      | Run configuration values                              |
| `metrics`     | Numerical evaluation results                          |
| `tags`        | Descriptive run metadata                              |

Runs reference experiments through a nullable foreign key. Deleting an experiment preserves its runs by setting their `experiment_id` to `NULL`.

Parameters, metrics, and tags reference runs with cascading deletion.

Each run can optionally have one saved model. Its serialization format is recorded in the `runs` table.

## Model Persistence

Models are stored separately from the database.

```text
.mllogs/
├── mllogs.db
└── models/
    ├── <run_id>.joblib
    └── <run_id>.pickle
```

Model persistence involves three components:

- **MLLogs:** Associates saved models with runs and records their serialization format.
- **LocalFileStore:** Reads and writes serialized bytes on the filesystem.
- **Serializers:** Convert Python objects to and from bytes using Joblib or Pickle.

Model filenames are derived from the run ID and serialization format. This avoids storing redundant file paths in the database.

The database stores metadata, not serialized model objects.

## Design Principles

**Local-first:** Experiment tracking and model persistence work without a separate server or external service.

**Minimal public API:** Users interact with experiments, runs, queries, and saved models without managing database connections or internal storage objects.

**Separation of concerns:** Database operations, file storage, serialization, and querying remain independent components.

**Structured storage:** Experiment metadata is stored in relational tables rather than individual JSON files.

**Flexible analysis:** SQLAlchemy Core handles querying, while pandas provides a familiar interface for analyzing experiment results.

## Limitations

- Only one run can be active per `MLLogs` instance.
- Each run supports at most one saved model.
- Local filesystem storage is the only implemented file backend.
- Database schema migrations are not currently managed automatically.
- Joblib and Pickle deserialization should only be used with trusted model files.
- Model champion promotion and retrieval are not included in v0.11.0.