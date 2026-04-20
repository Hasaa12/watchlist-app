from dataclasses import dataclass


@dataclass
class EntertainmentItem:
    item_id: int
    title: str
    type: str
    genre: str | None = None
    status: str | None = None
    date_added: str | None = None
    notes: str | None = None
    release_date: str | None = None
    rating: float | None = None
    year: int | None = None
    source: str | None = None

    @classmethod
    def from_row(cls, row):
        keys = set(row.keys())
        return cls(
            item_id=row["item_id"],
            title=row["title"],
            type=row["type"],
            genre=row["genre"] if "genre" in keys else None,
            status=row["status"] if "status" in keys else None,
            date_added=row["date_added"] if "date_added" in keys else None,
            notes=row["notes"] if "notes" in keys else None,
            release_date=row["release_date"] if "release_date" in keys else None,
            rating=row["rating"] if "rating" in keys else None,
            year=row["year"] if "year" in keys else None,
            source=row["source"] if "source" in keys else None,
        )

    def __str__(self):
        return f"{self.title} ({self.type}) | genre={self.genre} | status={self.status}"