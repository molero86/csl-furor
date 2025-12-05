"""
Script para añadir la columna 'group' a la tabla players
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL no encontrada en .env")
    exit(1)

print(f"🔧 Conectando a la base de datos...")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Verificar si la columna ya existe
        result = conn.execute(text("""
            SELECT COUNT(*) as count
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = 'furor_db'
            AND TABLE_NAME = 'players'
            AND COLUMN_NAME = 'group'
        """))
        
        exists = result.fetchone()[0] > 0
        
        if exists:
            print("✅ La columna 'group' ya existe en la tabla players")
        else:
            print("📝 Añadiendo columna 'group' a la tabla players...")
            conn.execute(text("ALTER TABLE players ADD COLUMN `group` VARCHAR(50) NULL"))
            conn.commit()
            print("✅ Columna 'group' añadida correctamente")
            
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

print("\n🎉 Migración completada con éxito")
