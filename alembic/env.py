from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Importamos la configuración para leer el DATABASE_URL del .env
from app.core.config import settings

# Importamos Base y todos los modelos para que Alembic los detecte
from app.db.database import Base
from app.models import *

# Configuración de Alembic
config = context.config

# Inyectamos el DATABASE_URL desde el .env en lugar de alembic.ini
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Configuración de logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata de todos los modelos — Alembic la usa para detectar cambios en las tablas
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()