import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from .config import settings

# Determine database URL based on environment
def get_database_url():
    """Get database URL based on environment"""
    is_production = os.getenv("ENVIRONMENT") == "production"

    # In production, use environment variable if set
    env_database_url = os.getenv("DATABASE_URL")
    if env_database_url:
        # Convert postgresql:// to postgresql+asyncpg:// for SQLAlchemy async
        if env_database_url.startswith("postgresql://"):
            env_database_url = env_database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if not is_production:
            print("Using DATABASE_URL from environment")
        return env_database_url

    # Check if we're using Cloud SQL
    if settings.USE_CLOUD_SQL or os.getenv("USE_CLOUD_SQL") == "true":
        # Build Cloud SQL connection string
        cloud_sql_instance = os.getenv("CLOUD_SQL_INSTANCE", settings.CLOUD_SQL_INSTANCE)
        db_user = os.getenv("POSTGRES_USER", settings.POSTGRES_USER)
        db_pass = os.getenv("DB_PASSWORD", settings.POSTGRES_PASSWORD)
        db_name = os.getenv("POSTGRES_DB", settings.POSTGRES_DB)

        if cloud_sql_instance:
            # Use Unix socket for Cloud SQL
            db_url = f"postgresql+asyncpg://{db_user}:{db_pass}@/{db_name}?host=/cloudsql/{cloud_sql_instance}"
            if not is_production:
                print("Using Cloud SQL connection")
            return db_url
        else:
            # Fall back to TCP connection
            db_host = os.getenv("POSTGRES_HOST", settings.POSTGRES_HOST)
            db_port = os.getenv("POSTGRES_PORT", str(settings.POSTGRES_PORT))
            db_url = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
            if not is_production:
                print("Using PostgreSQL TCP connection")
            return db_url

    # Default to settings DATABASE_URL (SQLite for development)
    if not is_production:
        print("Using SQLite database (development mode)")
    return settings.DATABASE_URL

# Get the actual database URL
database_url = get_database_url()

# Log connection info (mask password)
_masked = database_url
if "@" in _masked and "://" in _masked:
    _prefix = _masked.split("://")[0] + "://"
    _rest = _masked.split("://", 1)[1]
    if "@" in _rest:
        _user_pass, _host_rest = _rest.split("@", 1)
        _user = _user_pass.split(":")[0] if ":" in _user_pass else _user_pass
        _masked = f"{_prefix}{_user}:***@{_host_rest}"
print(f"Database URL: {_masked}")

# Create async engine with appropriate settings
if database_url.startswith("sqlite"):
    # SQLite specific settings
    engine = create_async_engine(
        database_url,
        echo=settings.DEBUG,
        future=True,
        connect_args={"check_same_thread": False},
    )
else:
    # PostgreSQL settings
    connect_args = {}

    # For Supabase/cloud PostgreSQL: if URL contains sslmode param, asyncpg handles it.
    # Only add explicit SSL if production and no sslmode in URL.
    if (os.getenv("ENVIRONMENT") == "production"
            and "/cloudsql/" not in database_url
            and "sslmode=" not in database_url
            and "ssl=" not in database_url):
        import ssl as _ssl
        ssl_ctx = _ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = _ssl.CERT_NONE
        connect_args["ssl"] = ssl_ctx
    
    # Only pass connect_args if it has actual configuration
    if connect_args:
        engine = create_async_engine(
            database_url,
            echo=settings.DEBUG,
            future=True,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            connect_args=connect_args,
        )
    else:
        engine = create_async_engine(
            database_url,
            echo=settings.DEBUG,
            future=True,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables and data (idempotent)"""
    # Ensure all models are registered in Base.metadata
    import app.models  # noqa: F401

    print("init_db: creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("init_db: tables created")

    # Import here to avoid circular imports
    from app.models import AIModel
    from sqlalchemy import select
    
    # Check if data already exists
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(AIModel).limit(1))
        existing_models = result.scalars().first()
        
        if not existing_models:
            print("No models found in database, initializing with seed data...")
            from app.core.seed_data import seed_database
            await seed_database(session)
            print("Database initialized successfully!")