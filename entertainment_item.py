class EntertainmentItem:
    def __init__(self, item_id=None, title="", item_type="", genre=None,
                 release_date=None, rating=None, year=None, source=None,
                 status="plan to watch", date_added=None, notes=None):
        self.item_id = item_id
        self.title = title
        self.item_type = item_type
        self.genre = genre
        self.release_date = release_date
        self.rating = rating
        self.year = year
        self.source = source
        self.status = status
        self.date_added = date_added
        self.notes = notes

    @classmethod
    def from_row(cls, row):
        return cls(
            item_id=row["item_id"],
            title=row["title"],
            item_type=row["type"],
            genre=row["genre"],
            release_date=row["release_date"],
            rating=row["rating"],
            year=row["year"],
            source=row["source"],
            status=row["status"],
            date_added=row["date_added"],
            notes=row["notes"],
        )

    def display(self):
        return f"{self.title} ({self.item_type}) | genre={self.genre} | status={self.status}"
