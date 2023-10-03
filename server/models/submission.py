from __future__ import annotations

from sqlalchemy import LargeBinary, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .errors import Errors
from .team import Team


class Submission(Base):
    __tablename__: str = 'submission'
    submission_id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    team_id_uuid: Mapped[int] = mapped_column(Integer(), ForeignKey("team.team_id_uuid"))
    error_id: Mapped[int] = mapped_column(Integer(), ForeignKey("errors.error_id"))
    submission_time: Mapped[str] = mapped_column(DateTime(), nullable=False)
    file_txt: Mapped[str] = mapped_column(LargeBinary(), nullable=False)

    team: Mapped[Team] = relationship(back_populates="submissions")
    error: Mapped[Errors] = relationship(back_populates='submission')
