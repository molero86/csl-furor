from sqlalchemy import text
from backend.database import engine

if __name__ == '__main__':
    print('Altering answers.text to TEXT...')
    with engine.begin() as conn:
        conn.execute(text('ALTER TABLE answers MODIFY COLUMN text TEXT NULL;'))
    print('Done.')
