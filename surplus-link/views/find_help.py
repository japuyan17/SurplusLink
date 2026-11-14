import mapview
import theme
import ui

theme.page_header(
    "Find food & shelter",
    "Food banks, pantries, and shelters in and around Berkeley. Hours change, so call ahead.",
    "icon_pickup",
)
theme.render(
    '<div class="sl-quote"><b>Need help right now?</b> Dial <a href="tel:211">211</a> to reach local food, '
    "housing, and emergency services, any time.</div>"
)

items = [r for r in ui.fetch("/resources") if r["kind"] in ("food_bank", "shelter")]
theme.section("Map", "Search an address or use your location to see what's closest, then tap for directions.")
mapview.explorer(ui.resource_points(items), title="Food banks and shelters near you")

theme.section("All locations")
theme.resource_cards(items)
