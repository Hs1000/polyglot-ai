import logging
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


def create_database_if_not_exists():
    """Create the target database if it does not already exist.

    Skipped when DATABASE_URL_OVERRIDE is set (e.g. Neon, RDS) because those
    services provision the database externally and don't expose admin access.
    """
    if settings.DATABASE_URL_OVERRIDE:
        logger.info("Using external database — skipping create-if-not-exists.")
        return

    admin_url = (
        f"postgresql+psycopg://"
        f"{settings.POSTGRES_USER}:"
        f"{quote_plus(settings.POSTGRES_PASSWORD)}@"
        f"{settings.POSTGRES_HOST}:"
        f"{settings.POSTGRES_PORT}/postgres"
    )

    try:
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
        with admin_engine.connect() as connection:
            result = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname=:dbname"),
                {"dbname": settings.POSTGRES_DB},
            )
            if not result.scalar():
                connection.execute(text(f'CREATE DATABASE "{settings.POSTGRES_DB}"'))
                logger.info("Created database %s.", settings.POSTGRES_DB)
        admin_engine.dispose()
    except Exception as exc:
        logger.warning("Could not verify/create database: %s", exc)


engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()