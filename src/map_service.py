"""Map service generating interactive Folium maps for destinations, attractions, and multi-city itineraries.
"""

from typing import Any, Dict, List, Optional
import folium
from folium.plugins import MarkerCluster

from src.data_loader import get_attractions_for_destination, get_destination_by_id


CATEGORY_COLORS = {
    "Historic Monument": "red",
    "Nature & Water": "blue",
    "Parks & Wildlife": "green",
    "Shopping & Culinary": "orange",
    "Heritage & Culture": "purple",
}


def create_destination_map(
    destination_id: str,
    zoom_start: int = 12
) -> Optional[folium.Map]:
    """Generate an interactive Folium map centered on a destination with its key attractions pinned."""
    dest = get_destination_by_id(destination_id)
    if not dest:
        return None

    lat = dest.get("latitude")
    lon = dest.get("longitude")
    if lat is None or lon is None or not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
        return None

    dest_name = dest.get("destination_name", "Destination")
    fmap = folium.Map(
        location=[lat, lon],
        zoom_start=zoom_start,
        tiles="OpenStreetMap"
    )

    # Primary Destination Center Marker
    popup_html = f"""
    <div style="font-family: sans-serif; min-width: 180px;">
        <h4 style="margin: 0 0 5px 0; color: #0d9488;">{dest_name}</h4>
        <p style="margin: 2px 0; font-size: 12px; color: #475569;"><b>Region:</b> {dest.get('region')}, {dest.get('country')}</p>
        <p style="margin: 2px 0; font-size: 12px; color: #475569;"><b>Type:</b> {dest.get('destination_type')}</p>
        <p style="margin: 2px 0; font-size: 12px; color: #0f172a;"><b>Est. Daily:</b> INR {dest.get('estimated_daily_budget_inr', 0):,.0f}</p>
    </div>
    """
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"{dest_name} (City Center)",
        icon=folium.Icon(color="darkblue", icon="star", prefix="fa")
    ).add_to(fmap)

    # Add Attractions
    attractions = get_attractions_for_destination(destination_id)
    offset_step = 0.008

    for idx, a in enumerate(attractions):
        cat = a.get("category", "Heritage & Culture")
        pin_color = CATEGORY_COLORS.get(cat, "cadetblue")
        # Approximate offset positioning around center for distinct pins
        angle = (idx * (360.0 / max(1, len(attractions)))) * (3.14159 / 180.0)
        dist = offset_step * (1.0 + (idx % 2) * 0.5)
        a_lat = lat + dist * 0.7 * (1 if idx % 2 == 0 else -1)
        a_lon = lon + dist * (1 if idx % 3 == 0 else -1)

        a_popup = f"""
        <div style="font-family: sans-serif; min-width: 160px;">
            <b style="color: #0f172a;">{a.get('attraction_name')}</b>
            <div style="font-size: 11px; color: #64748b; margin-top: 2px;">{cat}</div>
            <div style="font-size: 11px; margin-top: 4px;">Est. Duration: {a.get('typical_duration_hours')} hrs</div>
            <div style="font-size: 11px; color: #0d9488; font-weight: bold;">Ticket: INR {a.get('estimated_ticket_inr', 0):,.0f}</div>
        </div>
        """
        folium.Marker(
            location=[a_lat, a_lon],
            popup=folium.Popup(a_popup, max_width=220),
            tooltip=a.get("attraction_name"),
            icon=folium.Icon(color=pin_color, icon="info-sign")
        ).add_to(fmap)

    return fmap


def create_multi_destination_map(
    destinations: List[Dict[str, Any]],
    center_coords: Optional[List[float]] = None,
    zoom_start: int = 4
) -> folium.Map:
    """Render a clustered map showing multiple destinations simultaneously."""
    if center_coords and len(center_coords) == 2:
        start_loc = center_coords
    else:
        # Default center on India / Eurasia
        start_loc = [22.0, 78.0]

    fmap = folium.Map(location=start_loc, zoom_start=zoom_start, tiles="OpenStreetMap")
    marker_cluster = MarkerCluster().add_to(fmap)

    for d in destinations:
        lat = d.get("latitude")
        lon = d.get("longitude")
        if lat is None or lon is None or not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            continue

        d_name = d.get("destination_name", "Destination")
        is_dom = d.get("is_domestic", False)
        icon_color = "green" if is_dom else "blue"

        popup_html = f"""
        <div style="font-family: sans-serif; min-width: 170px;">
            <h4 style="margin: 0; color: #0d9488;">{d_name}</h4>
            <div style="font-size: 11px; color: #475569;">{d.get('country')} ({d.get('region')})</div>
            <div style="font-size: 11px; margin-top: 4px;">{d.get('destination_type')}</div>
            <div style="font-size: 11px; font-weight: bold; color: #0f172a; margin-top: 2px;">
                INR {d.get('estimated_daily_budget_inr', 0):,.0f}/day
            </div>
        </div>
        """
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"{d_name}, {d.get('country')}",
            icon=folium.Icon(color=icon_color, icon="plane" if not is_dom else "home", prefix="fa")
        ).add_to(marker_cluster)

    return fmap
