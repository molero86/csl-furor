"""
Script para añadir preguntas de Fase 4 a la base de datos.
Ejecutar: python -m scripts.add_phase4_questions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Question

def add_phase4_questions():
    db = SessionLocal()
    try:
        # Verificar si ya existen preguntas de fase 4
        existing = db.query(Question).filter(Question.phase == 4).first()
        if existing:
            print("⚠️ Ya existen preguntas de fase 4 en la base de datos")
            return
        
        # Crear pregunta genérica para la Fase 4
        questions = [
            Question(
                phase=4,
                order=1,
                text="Canta la canción",
                type="performance"
            )
        ]
        
        for q in questions:
            db.add(q)
        
        db.commit()
        print(f"✅ Se añadieron {len(questions)} pregunta(s) de Fase 4")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_phase4_questions()
