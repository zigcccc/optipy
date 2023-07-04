import pytest
from typing import Annotated

import sqlalchemy as sa
from fastapi import Header
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from sqlalchemy.orm import sessionmaker

from todoist.config.settings import Settings
from todoist.api.deps import get_auth_token_sub, get_db
from todoist.db.base import Base

from main import app

settings = Settings(_env_file=".env.test")
engine = sa.create_engine(settings.SQLALCHEMY_DATABASE_URI)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Set up the database once
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


# These two event listeners are only needed for sqlite for proper
# SAVEPOINT / nested transaction support. Other databases like postgres
# don't need them.
# From: https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#serializable-isolation-savepoints-transactional-ddl
@sa.event.listens_for(engine, "connect")
def do_connect(dbapi_connection, connection_record):
    # disable pysqlite's emitting of the BEGIN statement entirely.
    # also stops it from emitting COMMIT before any DDL.
    dbapi_connection.isolation_level = None


@sa.event.listens_for(engine, "begin")
def do_begin(conn):
    # emit our own BEGIN
    conn.exec_driver_sql("BEGIN")


# This fixture creates a nested transaction, recreates it when the
# application code calls session.commit and rolls it back at the end.
# Based on: https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
@pytest.fixture()
def session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Begin a nested transaction (using SAVEPOINT).
    nested = connection.begin_nested()

    # If the application code calls session.commit, it will end the nested
    # transaction. Need to start a new one when that happens.
    @sa.event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    # Rollback the overall transaction, restoring the state before the test ran.
    session.close()
    transaction.rollback()
    connection.close()


# A fixture for the fastapi test client which depends on the
# previous session fixture. Instead of creating a new session in the
# dependency override, it uses the one provided by the session fixture.
@pytest.fixture()
def client(session):
    def override_get_db():
        yield session

    def override_get_auth_token_sub(x_user: Annotated[str | None, Header()] = "user_a"):
        if x_user == "user_a":
            return "mock_sub_user_a@clients"

        if x_user == "user_b":
            return "mock_sub_user_b@clients"

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_auth_token_sub] = override_get_auth_token_sub

    add_pagination(app)

    yield TestClient(app)

    del app.dependency_overrides[get_db]
    del app.dependency_overrides[get_auth_token_sub]
