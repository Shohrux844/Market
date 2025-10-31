from sqlalchemy import String, BigInteger, Float, DateTime, Boolean, Text
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, sessionmaker
from datetime import datetime, timedelta
from typing import Optional

engine = create_engine("postgresql+psycopg2://postgres:1@pg:5432/ortiqboyev_bot")
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    birth_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    photo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    seria_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    debt: Mapped[float] = mapped_column(Float, default=0.0)
    start_debt: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_debt: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()