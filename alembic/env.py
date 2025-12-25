import os
import sys
from urllib.parse import urlparse
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from app.core.base import Base
    from app.core.settings import settings
    print("[INFO] Imports successful")
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    sys.exit(1)

db_url = str(settings.SQLALCHEMY_DATABASE_URI)
print(f"[DEBUG] Database URL: {db_url}")


# URL ni tekshirish
parsed = urlparse(db_url)
if not all([parsed.scheme, parsed.hostname]):
    print("[ERROR] Invalid database URL")
    sys.exit(1)
config = context.config
config.set_main_option("sqlalchemy.url", str(settings.SQLALCHEMY_DATABASE_URI))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
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
