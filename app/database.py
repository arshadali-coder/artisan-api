from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# SQLite compatibility settings
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_migrations():
    """Auto-migrate SQLite database columns if missing."""
    if not settings.DATABASE_URL.startswith("sqlite"):
        return

    with engine.connect() as conn:
        # Check users table
        try:
            result = conn.execute(text("PRAGMA table_info(users)")).fetchall()
            existing_user_cols = {row[1] for row in result}
            if existing_user_cols:
                user_cols_to_add = [
                    ("email", "VARCHAR(100)"),
                    ("hashed_password", "VARCHAR(255)"),
                    ("cover_image_url", "TEXT"),
                    ("sub_craft", "VARCHAR(100)"),
                    ("rating", "FLOAT DEFAULT 4.9"),
                    ("total_products", "INTEGER DEFAULT 24"),
                    ("total_sales", "INTEGER DEFAULT 150"),
                ]
                for col_name, col_type in user_cols_to_add:
                    if col_name not in existing_user_cols:
                        conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                conn.commit()
        except Exception as e:
            print(f"Users migration info: {e}")

        # Check products table
        try:
            result = conn.execute(text("PRAGMA table_info(products)")).fetchall()
            existing_prod_cols = {row[1] for row in result}
            if existing_prod_cols:
                prod_cols_to_add = [
                    ("sold_count", "INTEGER DEFAULT 14"),
                    ("market_benchmark", "VARCHAR(255) DEFAULT 'Similar items sell for ₹550 - ₹700'"),
                ]
                for col_name, col_type in prod_cols_to_add:
                    if col_name not in existing_prod_cols:
                        conn.execute(text(f"ALTER TABLE products ADD COLUMN {col_name} {col_type}"))
                conn.commit()
        except Exception as e:
            print(f"Products migration info: {e}")

