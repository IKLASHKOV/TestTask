from sqlalchemy import create_engine, Column, Integer, String, Float, asc, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from settings import USER_LOGIN, USER_PASSWORD, DB_HOST,DB_NAME



DATABASE_URL = f"mysql+pymysql://{USER_LOGIN}:{USER_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    price = Column(Float)
    category = Column(String(255))


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    price: float
    category: str