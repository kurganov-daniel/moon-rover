import os
from urllib.parse import unquote, urlparse

import pytest
from _pytest.monkeypatch import MonkeyPatch
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope='session')
def postgres_env():
    image = os.getenv('POSTGRES_IMAGE', 'postgres:15-alpine')
    username = os.getenv('POSTGRES_USER', 'test')
    pwd = os.getenv('POSTGRES_PASSWORD', 'test')
    db = os.getenv('POSTGRES_DB', 'test')

    mp = MonkeyPatch()
    try:
        with PostgresContainer(image, username=username, password=pwd, dbname=db) as pg:
            parsed = urlparse(pg.get_connection_url())

            mp.setenv('POSTGRES_HOST', parsed.hostname or '127.0.0.1')
            mp.setenv('POSTGRES_PORT', str(parsed.port or 5432))
            mp.setenv('POSTGRES_USER', parsed.username)
            mp.setenv('POSTGRES_PASSWORD', unquote(parsed.password or pwd))
            mp.setenv('POSTGRES_DB', (parsed.path or '/').lstrip('/') or db)
            mp.setenv('ALCHEMY_ECHO', os.getenv('ALCHEMY_ECHO', 'False'))

            yield
    finally:
        mp.undo()


@pytest.fixture(scope='session')
def apply_migrations(postgres_env):
    cfg = AlembicConfig('alembic.ini')
    alembic_command.upgrade(cfg, 'head')
    yield


@pytest.fixture(scope='session')
async def test_engine(postgres_env, apply_migrations):
    from app.infrastructure.db.config import get_pg_settings

    engine = create_async_engine(
        get_pg_settings().get_database_url, pool_pre_ping=True, poolclass=NullPool
    )
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture(scope='function')
async def test_session(test_engine):
    async with test_engine.connect() as conn:
        tx = await conn.begin()
        try:
            mk = sessionmaker(
                conn, class_=AsyncSession, expire_on_commit=False, autoflush=False
            )
            async with mk() as session:
                yield session
        finally:
            await tx.rollback()


@pytest.fixture
async def async_client(test_session):
    from app.infrastructure.db.engine import get_session
    from app.main import app

    async def _get_session_override():
        return test_session

    app.dependency_overrides[get_session] = _get_session_override

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def valid_username() -> str:
    """Valid username for tests"""
    return 'admin'


@pytest.fixture
def valid_password() -> str:
    """Valid password for tests"""
    return 'moon-rover-secret'


@pytest.fixture
def invalid_username() -> str:
    """Invalid username for tests"""
    return 'invalid-user'


@pytest.fixture
def invalid_password() -> str:
    """Invalid password for tests"""
    return 'invalid-password'
