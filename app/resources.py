"""Local food banks, shelters, and ways to help. Names, addresses, and hours come from the linked pages;
coordinates are approximate. Hours change, so verify before the demo."""
import re

from .models import Resource

_HOPE = "2012 Berkeley Way, Berkeley, CA"
_ACCFB = "7900 Edgewater Dr, Oakland, CA 94621"

RESOURCES = [
    Resource(
        id=1, name="Berkeley Food Pantry", kind="food_bank",
        address="1600 Sacramento St, Berkeley, CA 94702", lat=37.8800, lon=-122.2830,
        description="Monthly emergency grocery bags for people in Albany and Berkeley. Mon, Wed, Fri 2-4 pm.",
        how_to_help="Call ahead to confirm hours before visiting.",
        contact="(510) 525-2280", url="https://www.foodpantries.org/li/berkeley-food-pantry",
    ),
    Resource(
        id=2, name="Berkeley Food Network Pantry", kind="food_bank",
        address="1925 Ninth St, Berkeley, CA 94710", lat=37.8728, lon=-122.2975,
        description="Groceries for Alameda County residents. Tue and Thu 11 am-6 pm, one visit per week.",
        how_to_help="Volunteers help run the pantry; call to ask about openings.",
        contact="(510) 616-5383", url="https://www.foodpantries.org/li/ca_94710_berkeley-food-network",
    ),
    Resource(
        id=3, name="Alameda County Community Food Bank", kind="food_bank",
        address=_ACCFB, lat=37.7490, lon=-122.2040,
        description="Regional food bank that supplies partner pantries across Alameda County.",
        how_to_help="Volunteer, donate, or organize a food drive.",
        contact="volunteer@accfb.org", url="https://www.accfb.org",
    ),
    Resource(
        id=4, name="Hope Center (Insight Housing)", kind="shelter",
        address=_HOPE, lat=37.8735, lon=-122.2705,
        description="32-bed homeless shelter, 12 transitional beds for homeless veterans, 53 supportive housing "
                    "apartments, and a community kitchen with mental health and job training services.",
        how_to_help="Volunteer at the community meal (see Give back).",
        url="https://berkeleyca.gov/your-government/our-work/capital-projects/berkeley-food-and-housing-project-bfhp-hope-center",
    ),
    Resource(
        id=5, name="Dorothy Day House of Berkeley", kind="shelter",
        address="1931 Center St, Berkeley, CA", lat=37.8704, lon=-122.2706,
        description="Volunteer-run group serving daily breakfast to Men's Shelter residents and drop-in guests, "
                    "coordinating nightly Men's Shelter dinners, and running a foul-weather shelter on rainy nights.",
        how_to_help="Entirely volunteer-powered. Call to ask about volunteering.",
        contact="(510) 466-5553",
        url="https://www.idealist.org/en/nonprofit/c9e088cc3a0d49c5941622a201aba4bb-dorothy-day-house-of-berkeley-berkeley",
    ),
    Resource(
        id=6, name="Community Meal at the Hope Center", kind="volunteer",
        address=_HOPE, lat=37.8735, lon=-122.2705,
        description="Serve the community meal, pack lunches for the women's shelter and respite program, and help clean up.",
        how_to_help="Recurring 2-hour shifts (weekdays 2:30-4:30 pm, weekends 11:30 am-1:30 pm). Orientation and forms required.",
        url="https://www.idealist.org/en/volunteer-opportunity/ec513f15576644d3a11d18390e1dd30d-community-meal-at-the-hope-center-insight-housing-berkeley",
    ),
    Resource(
        id=7, name="Consider the Homeless Mobile Soup Kitchen", kind="volunteer",
        address="Central Berkeley (meet-up spot given at sign-up)", lat=37.8716, lon=-122.2727,
        description="Ride in a van and hand out hot soup, bread, and supplies to about 80 neighbors per outing.",
        how_to_help="Thursday or Sunday evenings, about 4:45-9:45 pm. Training, background check, and orientation required.",
        url="https://www.idealist.org/en/volunteer-opportunity/c047fcfb02b145b98657a725b78aaf54-be-the-change-help-a-mobile-soup-kitchen-reach-homeless-neighbors-in-berkeley-consider-the-homeless-berkeley",
    ),
    Resource(
        id=8, name="Volunteer with the Alameda County Community Food Bank", kind="volunteer",
        address=_ACCFB, lat=37.7490, lon=-122.2040,
        description="Sort and pack food, load delivery trucks, and help with weekly distributions at partner pantries.",
        how_to_help="Email volunteer@accfb.org to ask about current openings. Shifts are a few hours.",
        contact="volunteer@accfb.org", url="https://www.accfb.org/get-involved/volunteer-draft/individual-volunteers",
    ),
    Resource(
        id=9, name="Give to the Alameda County Community Food Bank", kind="donation",
        address="Online", lat=37.7490, lon=-122.2040,
        description="Fund meals for neighbors across Alameda County.",
        how_to_help="Donate online.", url="https://donate.accfb.org/give",
    ),
    Resource(
        id=10, name="Host a Food Drive", kind="donation",
        address="Your dorm, club, or workplace", lat=37.8719, lon=-122.2585,
        description="Collect non-perishable food for the Alameda County Community Food Bank.",
        how_to_help="Read the food drive FAQ for guidelines before you start.", url="https://www.accfb.org/food-drive-faq/",
    ),
]

for _r in RESOURCES:
    if re.match(r"^\d", _r.address):
        _r.nav_address = _r.address
