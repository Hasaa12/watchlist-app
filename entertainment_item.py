class EntertainmentItem:
    def __init__(self, title, item_type, genre, category, status, date_added):
        self.title = title
        self.item_type = item_type
        self.genre = genre
        self.category = category
        self.status = status
        self.date_added = date_added

    def load_from_row(self, row):
        self.title = row[0]
        self.item_type = row[1]
        self.genre = row[2]
        self.category = row[3]
        self.status = row[4]
        self.date_added = row[5]

    def display(self):
        return self.title + " (" + self.item_type + ") | genre=" + self.genre + " | status=" + self.status