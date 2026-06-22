from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class NpClassDeviation(Base):
    """NP class deviation percentages from Spruenge %NP sheet."""
    __tablename__ = "np_class_deviations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pg1_code: Mapped[str] = mapped_column(String(20), index=True)
    dgr: Mapped[str | None] = mapped_column(String(20), nullable=True)
    deviation_gold: Mapped[float | None] = mapped_column(Float, nullable=True)
    deviation_silver: Mapped[float | None] = mapped_column(Float, nullable=True)
    deviation_bronze: Mapped[float | None] = mapped_column(Float, nullable=True)


class DiscountGroup(Base):
    """Customer discount groups from MAX-Discount sheet."""
    __tablename__ = "discount_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    discount_group_code: Mapped[str] = mapped_column(String(20), index=True)
    ch3_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ch3_description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    max_basic_discount: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_add_discount: Mapped[float | None] = mapped_column(Float, nullable=True)


class EuTargetIncrease(Base):
    """EU target price increase by PG1/PG2."""
    __tablename__ = "eu_target_increases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pg_key: Mapped[str] = mapped_column(String(20), index=True)
    pg_level: Mapped[str] = mapped_column(String(5))  # 'PG1' or 'PG2'
    pg_text: Mapped[str | None] = mapped_column(String(200), nullable=True)
    sales_org: Mapped[str | None] = mapped_column(String(10), nullable=True)
    pcr: Mapped[float | None] = mapped_column(Float, nullable=True)
    par_04_2026: Mapped[float | None] = mapped_column(Float, nullable=True)
