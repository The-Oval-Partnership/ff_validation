'''This is the front end script'''
import os
import folium
import pandas as pd
import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap

BASE_DIR = os.curdir
st.title("Footflow Input Validation \n")
st.divider()

st.markdown(
    """
    - **Bus demand**
        - We are using frequency metrics as a proxy for relative demand at bus stops. The frequency of buses at each bus stop is aggregated to weekly, daily, and hourly level.
        - This data looks robust in urban areas but please tell us if you see accuracy issues in more rural areas.
    """
)
st.markdown(
    """
    - **Education demand**
        - This dataset represents the number of pupils at pre-school, primary, and secondary schools.
        - Some of the data is derived directly from Ofsted records, and the estimate for the remaining schools is derived from their estimated gross floor area.
        - Potential issues that we are currently working to understand the impact of include:
            - (a) schools with more than one site in close proximity
            - (b) schools located in mixed-use buildings.
        - Please tell us if you see relevant examples. This data does not include further education, which generates footfall at different times of the day and is thus grouped with other employment categories in our data.
    """
)
st.markdown(
    """
    - **Rail demand**
        - This is based on published annual station entry/exit data. To reduce the effect of volatile year-on-year results, we have applied a 5-year rolling average method with more weight assigned to the most recent years (and pandemic years excluded).
        - We would appreciate your feedback on whether the resulting metric provides a reasonable estimate of relative rail demand.
    """
)
st.markdown(
    """
    - **Residential demand**
        - This dataset represents our estimate of the sum of the population in each building (buildings from OS Localmap).
        - For ease of interpretation we have visualised the data normalised by the ground floor area of the buildings so that higher density housing appears darker in the colour scale.
        - The data is factored to 2022 mid year population estimates but uses 2024 address listings.
        - If you know of areas of recent housing completions (or clearance) in your authority area, please sense-check the estimates in these areas.
        - The method may result in some cases in small numbers of residents being allocated to non-residential buildings. Please tell us if you see examples that appear to be mis-allocating large numbers of residents.
        - We are also aware of issues with different classifications for multi-occupancy buildings such as student residences. Please flag any examples that look incorrect.
        - Due to the data size of this demand, it may take about 45 seconds to load.
    """
)
st.divider()

local_authorites = [
    "Barking and Dagenham",
    "Bolton",
    "Buckinghamshire (North & Central)",
    "Buckinghamshire (South, East & West)",
    "Charnwood",
    "Cheshire West and Chester",
    "City of London",
    "Ealing",
    "Eastleigh",
    "Hackney",
    "York",
    ]

demands = [
    'Bus demand',
    'Education demand',
    'Rail demand',
    'Residential demand'
    ]

demands_dict = {
    "Bus demand": "bus_demands.gpkg",
    "Education demand": "education_demand.gpkg",
    "Residential demand": "localmap_with_residential_demands.gpkg",
    "Rail demand" : "rail_demands.gpkg"
}

la_to_view = st.selectbox("Select Local Authority", local_authorites)
demand_to_view = st.selectbox("Select Demand to View", demands)
demand_to_read = demands_dict[demand_to_view]
path = os.path.join(BASE_DIR, la_to_view, demand_to_read)

if os.path.exists(path) and demand_to_view == "Bus demand":
    boundary = gpd.read_file(os.path.join(BASE_DIR, la_to_view, "boundary.gpkg"))
    gdf = gpd.read_file(path)
    m = leafmap.Map(center=(51.5074, 0.1278), zoom=10)
    m.add_basemap("OpenStreetMap")
    m.add_gdf(boundary, layer_name="boundary", color="Red", info_mode="on_click")
    for _, row in gdf.iterrows():
        folium.CircleMarker(
            location = [row.stop_lat, row.stop_lon],
            radius= row["weekly_demand"] / 40, # scaling the radius
            color = "Blue",
            fill = True,
            fill_color = "Blue",
            fill_opacity = 0.85,
            stroke = False,
            popup= folium.Popup(f"Stop Name: {row.stop_name} \
                <br> Weekly Demand: {row.weekly_demand} \
              <br> Daily Demand: {row.daily_demand} <br> Hourly Demand: \
                  {row.hourly_demand}", max_width=300)
        ).add_to(m)
    m.to_streamlit(width=700, height=600)

elif os.path.exists(path) and demand_to_view == "Residential demand":
    quantiles = [0.0, 0.01, 0.03131349379808141, 0.05138331924456558]
    boundary = gpd.read_file(os.path.join(BASE_DIR, la_to_view, "boundary.gpkg"))
    gdf = gpd.read_file(path, engine='pyogrio')
    m = leafmap.Map(center=(51.5074, 0.1278), zoom=10)
    m.add_basemap("OpenStreetMap")
    m.add_gdf(boundary, layer_name="boundary", fill="red", info_mode="on_click")
    m.add_data(gdf, column="residents per m2 ",
               scheme="UserDefined",
               cmap="Blues",
               classification_kwds={"bins": quantiles[1:]},
               legend_title="residents per m2 ",
               layer_name="Residential Demand",
               info_mode="on_click")
    m.to_streamlit(width=700, height=600)

elif os.path.exists(path):
    boundary = gpd.read_file(os.path.join(BASE_DIR, la_to_view, "boundary.gpkg"))
    gdf = gpd.read_file(path)
    m = leafmap.Map(center=(51.5074, 0.1278), zoom=10)
    m.add_basemap("OpenStreetMap")
    m.add_gdf(boundary, layer_name="boundary", fill_color="red", info_mode="on_click")
    m.add_gdf(gdf, layer_name=demand_to_read, zoom_to_layer=True, info_mode="on_click")
    m.to_streamlit(width=700, height=600)
else:
    st.write("No data found for the selected Local Authority and Demand")
st.divider()

st.markdown("Do send us your feedback to improve the input data.")