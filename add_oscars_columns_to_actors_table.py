from sqlalchemy import create_engine, inspect, Column, Integer, text
from sqlalchemy.ext.declarative import declarative_base

# Replace this with your actual database URL
DATABASE_URL = 'sqlite:///movies.db'  # or your PostgreSQL/MySQL URL

engine = create_engine(DATABASE_URL)
Base = declarative_base()

def upgrade():
    # Create an inspector
    inspector = inspect(engine)

    # Check if the columns already exist
    existing_columns = [col['name'] for col in inspector.get_columns('actors')]

    if 'oscars_wins' not in existing_columns:
        add_column(engine, 'actors', Column('oscars_wins', Integer, nullable=False,default=0))
    if 'oscars_nominations' not in existing_columns:
        add_column(engine, 'actors', Column('oscars_nominations', Integer, nullable=False,default=0))

def add_column(engine, table_name, column):
    column_name = column.compile(dialect=engine.dialect)
    column_type = column.type.compile(engine.dialect)
    with engine.connect() as conn:
        conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}'))
        conn.commit()

if __name__ == "__main__":
    upgrade()
    print("Columns added successfully.")
