from .models import Listing, ListingIn, Notification, User, UserIn
from .seed import PANTRIES, SITES


class Store:
    def __init__(self):
        self.reset()

    def reset(self):
        self.sites = {s.id: s for s in SITES}
        self.pantries = {p.id: p for p in PANTRIES}
        self.listings: dict[int, Listing] = {}
        self.notifications: list[Notification] = []
        self.users: dict[int, User] = {}
        self._listing_id = self._notification_id = self._user_id = 0

    def add_user(self, data: UserIn, password_hash: str) -> User:
        if self.user_by_email(data.email):
            raise ValueError("email taken")
        self._user_id += 1
        user = User(
            id=self._user_id,
            name=data.name.strip(),
            email=data.email.strip().lower(),
            role=data.role,
            site_id=data.site_id if data.role == "donor" else None,
            password_hash=password_hash,
        )
        self.users[user.id] = user
        return user

    def user_by_email(self, email: str) -> User | None:
        email = email.strip().lower()
        return next((u for u in self.users.values() if u.email == email), None)

    def add_listing(self, data: ListingIn, donor_id: int | None = None) -> Listing:
        if data.site_id not in self.sites:
            raise KeyError(data.site_id)
        self._listing_id += 1
        listing = Listing(id=self._listing_id, donor_id=donor_id, **data.model_dump())
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
