"""Apply additive PostgreSQL columns needed by the data-driven MVP."""
from sqlalchemy import inspect, text

from .database import engine, init_db


ADDITIVE_COLUMNS = {
    "works": {
        "district": "VARCHAR(100)",
        "block": "VARCHAR(100)",
        "village": "VARCHAR(150)",
        "ward": "VARCHAR(100)",
        "sanctioned_amount": "DOUBLE PRECISION",
        "expenditure_amount": "DOUBLE PRECISION",
        "implementing_agency": "VARCHAR(255)",
        "source_dataset": "VARCHAR(255)",
        "source_record_id": "VARCHAR(255)",
        "sanction_date": "TIMESTAMP",
    },
    "grievances": {
        "sla_deadline": "TIMESTAMP",
        "escalation_history": "JSON",
    },
}


def migrate() -> None:
    init_db()
    inspector = inspect(engine)
    with engine.begin() as connection:
        for table, columns in ADDITIVE_COLUMNS.items():
            existing = {column["name"] for column in inspector.get_columns(table)}
            for name, definition in columns.items():
                if name not in existing:
                    connection.execute(text(f'ALTER TABLE "{table}" ADD COLUMN "{name}" {definition}'))


if __name__ == "__main__":
    migrate()
    print("Schema migration complete")
