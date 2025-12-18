from sqlalchemy import inspect


def test_migrations_applied_and_loans_table_exists(db_session):
    insp = inspect(db_session.get_bind())
    assert insp.has_table("loans") is True
