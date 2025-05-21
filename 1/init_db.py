from app.database import SessionLocal, engine
from app.models import Base
from app.crud import create_user
from app.schemas import UserCreate
import traceback

def init_db():

    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        admin = UserCreate(
            username="admin",
            password="admin123",
            role="admin"
        )
        create_user(db, admin)
        print("Адміністратора створено успішно!")
        
        user = UserCreate(
            username="user",
            password="user123",
            role="user"
        )
        create_user(db, user)
        print("Користувача створено успішно!")
        
    except Exception as e:
        print(f"Помилка при створенні користувачів: {str(e)}")
        print("Деталі помилки:")
        print(traceback.format_exc())
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 