# VerticaPy Cell 01
# Initialize environment and import required libraries
%reset -f
from IPython import display
display.clear_output(wait=True)

import verticapy as vp
import plotly.graph_objects as go
import pandas as pd
import math

# Establish database connection
vp.connect("MyVerticaConnection")
----------------------------------------

# VerticaPy Cell 02
# Query to fetch fire event data including location, wind, and temperature
fire_events_query = """
SELECT 
    fire_location_id,
    event_id,
    event_time,
    fire_latitude,
    fire_longitude,
    wind_direction,
    wind_speed_m_per_sec,
    sensor_temp_degrees_celsius
FROM fire_events
WHERE event_id = 1
ORDER BY event_time;
"""

# Complex query to get fire truck positions and calculate safe zones based on wind direction
trucks_query = """
WITH fire_events_safe_zone AS (
    -- Calculate suggested safe positions based on wind direction using trigonometry
    SELECT
        *,
        CASE
            WHEN wind_direction = 1 THEN fire_latitude - 0.00045
            WHEN wind_direction = 2 THEN fire_latitude - 0.00045 * COS(RADIANS(45))
            WHEN wind_direction = 3 THEN fire_latitude
            WHEN wind_direction = 4 THEN fire_latitude + 0.00045 * COS(RADIANS(45))
            WHEN wind_direction = 5 THEN fire_latitude + 0.00045
            WHEN wind_direction = 6 THEN fire_latitude + 0.00045 * COS(RADIANS(45))
            WHEN wind_direction = 7 THEN fire_latitude
            WHEN wind_direction = 8 THEN fire_latitude - 0.00045 * COS(RADIANS(45))
        END as suggested_latitude,
        CASE
            WHEN wind_direction = 1 THEN fire_longitude
            WHEN wind_direction = 2 THEN fire_longitude - 0.00045 * SIN(RADIANS(45))
            WHEN wind_direction = 3 THEN fire_longitude - 0.00045
            WHEN wind_direction = 4 THEN fire_longitude - 0.00045 * SIN(RADIANS(45))
            WHEN wind_direction = 5 THEN fire_longitude
            WHEN wind_direction = 6 THEN fire_longitude + 0.00045 * SIN(RADIANS(45))
            WHEN wind_direction = 7 THEN fire_longitude + 0.00045
            WHEN wind_direction = 8 THEN fire_longitude + 0.00045 * SIN(RADIANS(45))
        END as suggested_longitude
    FROM fire_events
),
fire_truck_distance_from_safe_zone AS (
    -- Calculate distances between trucks and their suggested safe positions
    SELECT
        ft.fire_truck_id, ft.event_id, ft.litres_of_water, ft.litres_of_fuel, 
        ft.fire_truck_name, ft.latitude, ft.longitude,
        fesz.suggested_latitude, fesz.suggested_longitude,
        ST_Distance(
            ST_GeographyFromText('POINT(' || ft.longitude || ' ' || ft.latitude || ')'),
            ST_GeographyFromText('POINT(' || fesz.suggested_longitude || ' ' || fesz.suggested_latitude || ')')
        ) as distance_in_meters_to_safe_zone
    FROM fire_trucks_location ft
    CROSS JOIN fire_events_safe_zone fesz
    WHERE ft.event_id = fesz.event_id and ft.valid
),
all_fire_trucks AS (
    -- Get minimum distances for each truck
    SELECT  
        min(distance_in_meters_to_safe_zone) as distance_in_meters_to_safe_zone,
        fire_truck_id,
        event_id
    FROM fire_truck_distance_from_safe_zone
    group by 2,3
)
SELECT 
    aft.event_id, 
    aft.fire_truck_id, 
    ftd.litres_of_water, 
    ftd.litres_of_fuel, 
    ftd.fire_truck_name, 
    ftd.latitude,
    ftd.longitude, 
    aft.distance_in_meters_to_safe_zone, 
    ftd.suggested_latitude, 
    ftd.suggested_longitude
FROM all_fire_trucks aft, fire_truck_distance_from_safe_zone ftd
WHERE aft.fire_truck_id = ftd.fire_truck_id
AND aft.event_id = ftd.event_id
AND aft.distance_in_meters_to_safe_zone = ftd.distance_in_meters_to_safe_zone
ORDER BY 1,2,8;
"""

# Helper function to calculate wind direction arrow endpoints
def calculate_wind_endpoint(lat, lon, direction, speed):
    """Calculate endpoint for wind direction arrow - reduced to 10% length"""
    angle = math.radians(angle_map[direction])
    scale = 0.00005 * speed  
    dlat = scale * math.cos(angle)
    dlon = scale * math.sin(angle)
    return lat + dlat, lon + dlon

# Helper function to determine resource level indicators (water/fuel)
def get_lines(value, max_value):
    """Get number of lines based on resource level"""
    ratio = value / max_value
    if ratio < 1/3:
        return 1
    elif ratio < 2/3:
        return 2
    else:
        return 3

# Helper function to create dashed lines for movement indicators
def create_dashed_line(start_lat, start_lon, end_lat, end_lon, num_points=20):
    """Create points for a dashed line effect"""
    lats = []
    lons = []
    for i in range(num_points):
        if i % 2 == 0:
            t = i / (num_points - 1)
            lats.extend([
                start_lat + (end_lat - start_lat) * t,
                start_lat + (end_lat - start_lat) * (t + 1/num_points)
            ])
            lons.extend([
                start_lon + (end_lon - start_lon) * t,
                start_lon + (end_lon - start_lon) * (t + 1/num_points)
            ])
    return lats, lons

# Load and prepare data from Vertica database
try:
    fire_events_df = vp.vDataFrame(fire_events_query).to_pandas()
    trucks_df = vp.vDataFrame(trucks_query).to_pandas()
    print("Data loaded successfully")
except Exception as e:
    print(f"Error loading data: {e}")
    raise

# Define mapping dictionaries for wind directions
direction_map = {1: "N", 2: "NE", 3: "E", 4: "SE", 5: "S", 6: "SW", 7: "W", 8: "NW"}
angle_map = {1: 0, 2: 45, 3: 90, 4: 135, 5: 180, 6: 225, 7: 270, 8: 315}
---------------------------------------------------------------------------------------------

# VerticaPy Cell 03
# Create interactive map visualization using Plotly
try:
    fig = go.Figure()

    # Add fire locations with temperature indicators
    fig.add_trace(go.Scattermapbox(
        lat=fire_events_df['fire_latitude'],
        lon=fire_events_df['fire_longitude'],
        mode='markers',
        marker=dict(
            size=28,  
            color=fire_events_df['sensor_temp_degrees_celsius'],
            colorscale=[[0, 'yellow'], [1, 'red']],
            colorbar=dict(
                title='Temperature °C',
                thickness=10,
                len=0.6,
                x=1.01
            ),
            opacity=0.8
        ),
        text=[f"{temp}°C" for temp in fire_events_df['sensor_temp_degrees_celsius']],
        hovertemplate="Fire location temperature: %{text}<extra></extra>",
        hoverlabel=dict(bgcolor='orange'),
        name="Fire Locations"
    ))

    # Add wind direction indicators
    for _, row in fire_events_df.iterrows():
        end_lat, end_lon = calculate_wind_endpoint(
            row['fire_latitude'], 
            row['fire_longitude'],
            row['wind_direction'],
            row['wind_speed_m_per_sec']
        )
        
        fig.add_trace(go.Scattermapbox(
            lat=[row['fire_latitude'], end_lat],
            lon=[row['fire_longitude'], end_lon],
            mode='lines',
            line=dict(
                width=2,
                color='blue'
            ),
            hoverinfo='text',
            text=[
                f"Fire location temperature: {row['sensor_temp_degrees_celsius']}°C<br>"
                f"Lat: {row['fire_latitude']:.6f}<br>"
                f"Lon: {row['fire_longitude']:.6f}", 
                f"Wind Speed: {row['wind_speed_m_per_sec']} m/s<br>"
                f"Direction: {direction_map[row['wind_direction']]}"
            ],
            hoverlabel=dict(
                bgcolor=['orange', 'blue']
            ),
            showlegend=False
        ))

    # Add detailed fire truck visualizations
    for _, row in trucks_df.iterrows():
        truck_lat, truck_lon = row['latitude'], row['longitude']
        lat_offset = 0.000028  
        lon_offset = 0.000168  

        # Add truck body (dark red rectangle)
        fig.add_trace(go.Scattermapbox(
            lat=[truck_lat-lat_offset, truck_lat+lat_offset, truck_lat+lat_offset, truck_lat-lat_offset, truck_lat-lat_offset],
            lon=[truck_lon-lon_offset, truck_lon-lon_offset, truck_lon+lon_offset, truck_lon+lon_offset, truck_lon-lon_offset],
            mode='lines',
            line=dict(color='darkred', width=2),
            fill='toself',
            fillcolor='darkred',
            hoverinfo='skip',
            showlegend=False
        ))

        # Add truck cabin
        cabin_height = 0.7 * lat_offset
        cabin_width = 0.7 * lon_offset
        fig.add_trace(go.Scattermapbox(
            lat=[truck_lat+lat_offset, truck_lat+lat_offset+cabin_height, truck_lat+lat_offset+cabin_height, truck_lat+lat_offset],
            lon=[truck_lon-lon_offset, truck_lon-lon_offset+cabin_width, truck_lon-lon_offset+cabin_width, truck_lon-lon_offset+cabin_width],
            mode='lines',
            line=dict(color='darkred', width=2),
            fill='toself',
            fillcolor='darkred',
            hoverinfo='skip',
            showlegend=False
        ))

        # Add water level indicators
        water_lines = get_lines(row['litres_of_water'], 5678)
        for i in range(3):
            y_offset = -0.4*lat_offset + i*0.4*lat_offset
            color = 'blue' if i < water_lines else 'rgb(80,0,0)'
            fig.add_trace(go.Scattermapbox(
                lat=[truck_lat+y_offset, truck_lat+y_offset],
                lon=[truck_lon-0.8*lon_offset, truck_lon-0.1*lon_offset],
                mode='lines',
                line=dict(color=color, width=4),
                hoverinfo='skip',
                showlegend=False
            ))

        # Add fuel level indicators
        fuel_lines = get_lines(row['litres_of_fuel'], 3785)
        for i in range(3):
            y_offset = -0.4*lat_offset + i*0.4*lat_offset
            color = 'yellow' if i < fuel_lines else 'rgb(80,0,0)'
            fig.add_trace(go.Scattermapbox(
                lat=[truck_lat+y_offset, truck_lat+y_offset],
                lon=[truck_lon+0.1*lon_offset, truck_lon+0.8*lon_offset],
                mode='lines',
                line=dict(color=color, width=4),
                hoverinfo='text',
                text=f"{row['fire_truck_name']}<br>"
                     f"Water: {row['litres_of_water']}L<br>"
                     f"Fuel: {row['litres_of_fuel']}L",
                showlegend=False
            ))

        # Add truck wheels
        wheel_radius = 0.000014
        wheel_color = 'dimgray'

        # Left wheel
        fig.add_trace(go.Scattermapbox(
            lat=[truck_lat-lat_offset-wheel_radius*math.cos(t) for t in range(0, 180)],
            lon=[truck_lon-0.7*lon_offset+wheel_radius*math.sin(t) for t in range(0, 180)],
            mode='lines',
            line=dict(color=wheel_color, width=2),
            fill='toself',
            fillcolor=wheel_color,
            hoverinfo='skip',
            showlegend=False
        ))

        # Right wheel
        fig.add_trace(go.Scattermapbox(
            lat=[truck_lat-lat_offset-wheel_radius*math.cos(t) for t in range(0, 180)],
            lon=[truck_lon+0.7*lon_offset+wheel_radius*math.sin(t) for t in range(0, 180)],
            mode='lines',
            line=dict(color=wheel_color, width=2),
            fill='toself',
            fillcolor=wheel_color,
            hoverinfo='skip',
            showlegend=False
        ))

        # Add movement indicators for trucks within range
        if 50 < row['distance_in_meters_to_safe_zone'] < 1500:
            dash_lats, dash_lons = create_dashed_line(
                row['latitude'], row['longitude'],
                row['suggested_latitude'], row['suggested_longitude']
            )
            
            fig.add_trace(go.Scattermapbox(
                lat=dash_lats,
                lon=dash_lons,
                mode='lines',
                line=dict(
                    width=1,
                    color='black'
                ),
                hoverinfo='text',
                text=f"Suggested safe zone<br>Distance: {row['distance_in_meters_to_safe_zone']:.0f}m",
                showlegend=False
            ))

    # Calculate and set map boundaries
    all_lats = pd.concat([fire_events_df['fire_latitude'], trucks_df['latitude']])
    all_lons = pd.concat([fire_events_df['fire_longitude'], trucks_df['longitude']])
    
    center_lat = all_lats.mean()
    center_lon = all_lons.mean()
    
    # Configure map layout and display settings
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=center_lat, lon=center_lon),
            zoom=14
        ),
        showlegend=True,
        legend=dict

        # Configure map layout and display settings
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=center_lat, lon=center_lon),
            zoom=14
        ),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255, 255, 255, 0.8)"
        ),
        title_text="Fire Incident Monitoring System",
        height=900,
        width=None,
        margin=dict(l=0, r=0, t=30, b=0),
        autosize=True
    )

    # Configure and display interactive map with custom controls
    fig.show(config={
        'scrollZoom': True,
        'displayModeBar': True,
        'modeBarButtonsToAdd': ['drawrect', 'eraseshape'],
        'responsive': True,
        'showTips': True,
        'modeBarButtonsToRemove': [],
        'toImageButtonOptions': {'format': 'png'},
        'displaylogo': False
    })

except Exception as e:
    print(f"Error: {e}")
    print("Error details:", e.__class__.__name__)