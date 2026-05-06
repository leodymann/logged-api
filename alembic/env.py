from logging.config import fileConfig

from sqlalchemy import engine_from_config, inspect, pool
from alembic import context

from backend.core.config import settings
from backend.core.database import Base
from backend.core.models import AuthEvent, LoginCode, User  # noqa: F401


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


def get_url() -> str:
    return str(settings.DATABASE_URL)


def run_migrations_offline() -> None:
    url = get_url()

    print("DATABASE_URL OFFLINE:", url)
    print("TABELAS METADATA OFFLINE:", list(target_metadata.tables.keys()))

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)

    if configuration is None:
        raise RuntimeError("Alembic configuration section not found.")

    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.begin() as connection:
        inspector = inspect(connection)

        print("DATABASE_URL ONLINE:", get_url())
        print("TABELAS NO BANCO:", inspector.get_table_names())
        print("TABELAS NO METADATA:", list(target_metadata.tables.keys()))

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()