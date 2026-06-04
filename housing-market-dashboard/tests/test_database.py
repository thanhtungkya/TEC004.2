from src.database.create_tables import create_tables


def test_create_tables_runs_without_error():
    create_tables()
