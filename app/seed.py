"""Sample Berkeley data. Coordinates are approximate and capacities are made up: verify before demoing."""
from .models import Pantry, Site

SITES = [
    Site(id=1, name="Crossroads Dining Hall", kind="dining", lat=37.8678, lon=-122.2559, avg_lbs=90),
    Site(id=2, name="Foothill Dining Hall", kind="dining", lat=37.8750, lon=-122.2565, avg_lbs=70),
    Site(id=3, name="Cafe 3", kind="dining", lat=37.8665, lon=-122.2606, avg_lbs=55),
    Site(id=4, name="Clark Kerr Dining", kind="dining", lat=37.8627, lon=-122.2503, avg_lbs=60),
    Site(id=5, name="Telegraph Ave Bakery (demo)", kind="restaurant", lat=37.8660, lon=-122.2585, avg_lbs=25),
    Site(id=6, name="Campus Event Catering (demo)", kind="event", lat=37.8720, lon=-122.2595, avg_lbs=45),
]

PANTRIES = [
    Pantry(id=1, name="ASUC Food Pantry", lat=37.8691, lon=-122.2603, capacity_lbs=150,
           needs=["vegetarian", "produce", "gluten-free"]),
    Pantry(id=2, name="Berkeley Food Pantry", lat=37.8795, lon=-122.2830, capacity_lbs=400,
           needs=["produce", "prepared meals", "halal", "vegan"]),
    Pantry(id=3, name="Berkeley Student Food Collective (demo)", lat=37.8664, lon=-122.2589, capacity_lbs=120,
           needs=["vegan", "vegetarian", "baked goods"]),
]
