from .models import Listing, ListingIn, Notification
from .seed import PANTRIES, SITES


class Store:
    def __init__(self):
        self.reset()

    def reset(self):
        self.sites = {s.id: s for s in SITES}
        self.pantries = {p.id: p for p in PANTRIES}
        self.listings: dict[int, Listing] = {}
        self.notifications: list[Notification] = []
        self._listing_id = 0
        self._notification_id = 0

    def add_listing(self, data: ListingIn) -> Listing:
        if data.site_id not in self.sites:
            raise KeyError(data.site_id)
        self._listing_id += 1
        listing = Listing(id=self._listing_id, **data.model_dump())
        self.listings[listing.id] = listing
        return listing

    def remaining(self, pantry_id: int) -> float:
        used = sum(
            l.quantity_lbs
            for l in self.listings.values()
            if l.status == "matched" and l.pantry_id == pantry_id
        )
        return self.pantries[pantry_id].capacity_lbs - used

    def notify(self, listing_id: int, pantry_id: int, message: str) -> Notification:
        self._notification_id += 1
        note = Notification(id=self._notification_id, listing_id=listing_id, pantry_id=pantry_id, message=message)
        self.notifications.append(note)
        return note


store = Store()
