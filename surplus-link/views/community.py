import mapview
import theme
import ui

theme.page_header(
    "Give back",
    "Other ways to volunteer your time or donate to fight hunger and homelessness nearby.",
    "icon_heart",
)

items = ui.fetch("/resources")
volunteer = [r for r in items if r["kind"] == "volunteer"]
donate = [r for r in items if r["kind"] == "donation"]

theme.section("Volunteer near you", "Shifts that need hands, from serving meals to packing groceries.")
mapview.explorer(ui.resource_points(volunteer), title="Volunteer spots near you", height=560)
theme.resource_cards(volunteer)

theme.section("Donate", "Give money or food to organizations feeding neighbors across Alameda County.")
theme.resource_cards(donate)
