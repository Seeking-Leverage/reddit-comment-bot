from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from bot.settings import settings


class Base(DeclarativeBase):
    pass


class CommentRecord(Base):
    __tablename__ = "comment_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[str] = mapped_column(String(64), index=True)
    reddit_username: Mapped[str] = mapped_column(String(64))
    post_id: Mapped[str] = mapped_column(String(32), index=True)
    comment_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    parent_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    subreddit: Mapped[str] = mapped_column(String(64))
    generated_text: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class Database:
    def __init__(self, path=None):
        db_path = path or settings.database_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)

    def has_engaged_post(self, client_id: str, post_id: str) -> bool:
        with Session(self.engine) as session:
            stmt = select(CommentRecord).where(
                CommentRecord.client_id == client_id,
                CommentRecord.post_id == post_id,
                CommentRecord.status.in_(["posted", "dry_run"]),
            )
            return session.scalars(stmt).first() is not None

    def count_comments_today(self, client_id: str) -> int:
        today = datetime.now(timezone.utc).date()
        with Session(self.engine) as session:
            records = session.scalars(
                select(CommentRecord).where(
                    CommentRecord.client_id == client_id,
                    CommentRecord.status == "posted",
                )
            ).all()
            return sum(1 for r in records if r.created_at.date() == today)

    def last_comment_at(self, client_id: str) -> Optional[datetime]:
        with Session(self.engine) as session:
            records = session.scalars(
                select(CommentRecord)
                .where(
                    CommentRecord.client_id == client_id,
                    CommentRecord.status == "posted",
                )
                .order_by(CommentRecord.created_at.desc())
            ).all()
            return records[0].created_at if records else None

    def record_comment(
        self,
        *,
        client_id: str,
        reddit_username: str,
        post_id: str,
        subreddit: str,
        generated_text: str,
        status: str,
        comment_id: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> CommentRecord:
        with Session(self.engine) as session:
            record = CommentRecord(
                client_id=client_id,
                reddit_username=reddit_username,
                post_id=post_id,
                comment_id=comment_id,
                parent_id=parent_id,
                subreddit=subreddit,
                generated_text=generated_text,
                status=status,
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return record