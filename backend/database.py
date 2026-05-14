from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./what_to_eat.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations():
    with engine.connect() as conn:
        for ddl in [
            "ALTER TABLE places ADD COLUMN notes TEXT",
            "ALTER TABLE places ADD COLUMN shop_images TEXT",
            "ALTER TABLE places ADD COLUMN menu_images TEXT",
            "ALTER TABLE places ADD COLUMN country TEXT",
        ]:
            try:
                conn.execute(text(ddl))
                conn.commit()
            except Exception:
                pass  # column already exists
