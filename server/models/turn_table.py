from sqlalchemy import LargeBinary, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class TurnTable(Base):
    __tablename__: str = 'turn_table'
    turn_id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    turn_number: Mapped[int] = mapped_column(Integer())
    run_id: Mapped[int] = mapped_column(Integer(), ForeignKey('run.run_id', ondelete='CASCADE'))
    turn_data: Mapped[str] = mapped_column(LargeBinary(), nullable=False)

    run: Mapped['Run'] = relationship(back_populates='turn_tables', passive_deletes=True)


