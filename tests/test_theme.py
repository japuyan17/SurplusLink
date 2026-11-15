import theme
import ui


def test_maps_links_prefer_address():
    html = theme.maps_links("Pantry", 37.1, -122.1, "1600 Sacramento St, Berkeley, CA")
    assert "daddr=1600%20Sacramento%20St%2C%20Berkeley%2C%20CA" in html
    assert "destination=1600%20Sacramento%20St" in html
    assert "37.1" not in html


def test_maps_links_fall_back_to_coordinates():
    html = theme.maps_links("Cafe", 37.8665, -122.2606)
    assert "daddr=37.8665,-122.2606" in html and "destination=37.8665,-122.2606" in html


def test_maps_links_escape_quotes_in_names():
    html = theme.maps_links('A "quoted" name', 1, 2)
    assert 'A "quoted"' not in html and "A%20%22quoted%22%20name" in html


def test_resource_points_only_include_real_addresses():
    base = dict(id=1, name="X", kind="volunteer", address="Online", lat=1.0, lon=2.0, description="d",
                how_to_help="", contact="", url="", nav_address="")
    physical = {**base, "id": 2, "address": "2012 Berkeley Way, Berkeley, CA", "nav_address": "2012 Berkeley Way, Berkeley, CA"}
    points = ui.resource_points([base, physical])
    assert [p["id"] for p in points] == ["r2"]
    assert points[0]["kind_label"] == "Volunteer" and points[0]["color"].startswith("#")


def test_kind_style_unknown_kind_has_fallback():
    assert theme.kind_style("mystery")[0] == "Place"
