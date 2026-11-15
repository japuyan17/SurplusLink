import streamlit as st

import theme

theme.page_header(
    "About SurplusLink",
    "A free, community-minded way to move surplus food to the people who need it.",
    "icon_heart",
)

theme.section("Why we built it")
st.markdown(
    "Food is wasted every day, and neighbors go hungry every day, often within a few miles of each other. "
    "The USDA estimates that **30 to 40 percent** of the US food supply goes to waste. At the same time, "
    "**48 million people** lived in food-insecure households in 2024, including more than 14 million children."
)
theme.render(
    '<div class="sl-quote">The problem is rarely a shortage of food. It is getting extra food to the right '
    "place before it spoils.</div>"
)

theme.section("Who it's for")
theme.feature_cards([
    ("icon_post", "Food donors",
     "Dining halls, restaurants, caterers, and event hosts with extra prepared or packaged food. Post it in under a minute.",
     "#F28C38"),
    ("icon_pickup", "Neighbors and pantries",
     "Anyone looking for a meal, and the food pantries that serve them. See what's available, where, and for how long.",
     "#2E86AB"),
    ("icon_heart", "Volunteers and givers",
     "People who want to help beyond one meal: find shelters, food banks, volunteer shifts, and ways to give nearby.",
     "#8E5EA2"),
])

theme.section("How matching works", "Every open listing is paired with the pantry where it will do the most good.")
theme.feature_cards([
    ("icon_pickup", "Distance", "Closer pantries score higher, and a pantry is skipped if the trip would miss the pickup deadline.", "#2E86AB"),
    ("icon_post", "Urgency", "Food that needs to move soon gets priority, so the most perishable items are handled first.", "#E4572E"),
    ("icon_match", "Fit and capacity", "Dietary needs are matched, and pantries are never sent more than they can store.", "#2F7D5B"),
])

theme.band(
    "Built for UN Sustainable Development Goal 2: Zero Hunger",
    "SurplusLink was created for the GM#11 hackathon. Our goal is simple: end hunger by making sure good food "
    "is eaten by people, not thrown away.",
)

theme.section("About this demo", "We want to be upfront about what is real and what is sample data.")
st.markdown(
    "- Donor sites and pantries are sample Berkeley locations, and their map pins are approximate.\n"
    "- The Find food & shelter and Give back pages list real organizations. Hours and availability change, so "
    "call ahead before you go.\n"
    "- Surplus forecasts come from a model trained on synthetic data.\n"
    "- Accounts and listings are stored in memory and reset when the server restarts."
)

theme.section("Sources")
st.markdown(
    "- [USDA: Food Loss and Waste FAQs](https://www.usda.gov/foodwaste/faqs)\n"
    "- [Feeding America: statement on the USDA's 2024 food security report]"
    "(https://www.feedingamerica.org/about-us/press-room/feeding-america-statement-usda-2024-food-security-report)\n"
    "- [United Nations: Sustainable Development Goal 2, Zero Hunger](https://sdgs.un.org/goals/goal2)"
)
