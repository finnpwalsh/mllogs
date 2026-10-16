from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    JSON,
    MetaData,
    String,
    Table,
    UniqueConstraint,
)


metadata = MetaData()


experiments = Table(
    "experiments",
    metadata,
    Column("id", String, primary_key=True),
    Column("name", String, nullable=False, unique=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
)


runs = Table(
    "runs",
    metadata,
    Column("id", String, primary_key=True),
    Column(
        "experiment_id",
        String,
        ForeignKey("experiments.id", ondelete="SET NULL"),
        nullable=True,
    ),
    Column("started_at", DateTime(timezone=True), nullable=False),
    Column("status", String, nullable=False),
    Column("ended_at", DateTime(timezone=True), nullable=True),
    Column("model_format", String, nullable=True)
)


params = Table(
    "params",
    metadata,
    Column(
        "run_id",
        String,
        ForeignKey("runs.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("key", String, primary_key=True),
    Column("value", JSON, nullable=False),
)


metrics = Table(
    "metrics",
    metadata,
    Column(
        "run_id",
        String,
        ForeignKey("runs.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("key", String, primary_key=True),
    Column("value", Float, nullable=False),
)


tags = Table(
    "tags",
    metadata,
    Column(
        "run_id",
        String,
        ForeignKey("runs.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("key", String, primary_key=True),
    Column("value", String, nullable=False),
)


artifacts = Table(
    "artifacts",
    metadata,
    Column("id", String, primary_key=True),
    Column(
        "run_id",
        String,
        ForeignKey("runs.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("name", String, nullable=False),
    Column("format", String, nullable=False),
    UniqueConstraint("run_id", "name"),
)