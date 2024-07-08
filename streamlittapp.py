'''This is the front end script'''
import os
import folium
import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap

BASE_DIR = os.curdir
st.title("Footflow Input Validation \n")


st.markdown("- Bus demand - This is a proxy demand for the number of buses at each bus\
    stop aggregated to weekly, daily, and hourly level.\n  ")
st.markdown("- Education demand - The number of students for preschool,\
    primary, secondary . The figures are from 2 sources (ofsted and gross floor area estimation) \n")
st.markdown("- Residential demand - This is the number of residents in each building. These estimates\
    have been derived with our methodology and visualised with localmap.\n")
st.markdown("- Rail demand - This is annual number of passengers entering and exiting the station averaged\
    for the last 5 years (Pandemic year excluded).\n")

local_authorites = [
    "Barking and Dagenham",
    "Bolton",
    "Buckinghamshire",
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
    'Residential demand',
    'Rail demand'
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
    m.add_basemap(basemap="CartoDB.Positron")
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
    m.to_streamlit(width=800, height=600)

elif os.path.exists(path) and demand_to_view == "Residential demand":
    #quantiles = [0.0, 0.0, 0.03131349379808141, 0.05138331924456558]
    boundary = gpd.read_file(os.path.join(BASE_DIR, la_to_view, "boundary.gpkg"))
    gdf = gpd.read_file(path)
    # labels = [
    #         f"{quantiles[0]} - {quantiles[1]}", #0 - 25th percentile
    #         f"{quantiles[1]} - {quantiles[2]}", #25th - 50th percentile
    #         f"{quantiles[2]} - {quantiles[3]}", #50th - 75th percentile
    #         f"{quantiles[3]} - {max(gdf['residents per m2 '])}" #75th - 100th percentile
    # ]
    m = leafmap.Map(center=(51.5074, 0.1278), zoom=10)
    m.add_basemap(basemap="CartoDB.Positron")
    m.add_basemap("OpenStreetMap")
    m.add_gdf(boundary, layer_name="boundary", fill="red", info_mode="on_click")
    m.add_data(gdf, column="residents per m2 ",
               scheme="Quantiles",
               cmap="Blues", 
               #classification_kwds={"bins": quantiles},
               legend_title="residents per m2 ",
               layer_name="Residential Demand",
               info_mode="on_click",
               k=3)
    m.to_streamlit(width=800, height=600)

elif os.path.exists(path):
    boundary = gpd.read_file(os.path.join(BASE_DIR, la_to_view, "boundary.gpkg"))
    gdf = gpd.read_file(path)
    m = leafmap.Map(center=(51.5074, 0.1278), zoom=10)
    m.add_basemap(basemap="CartoDB.Positron")
    m.add_basemap("OpenStreetMap")
    m.add_gdf(boundary, layer_name="boundary", fill_color="red", info_mode="on_click")
    m.add_gdf(gdf, layer_name=demand_to_read, zoom_to_layer=True, info_mode="on_click")
    m.to_streamlit(width=800, height=600)
else:
    st.write("No data found for the selected Local Authority and Demand")

st.markdown("We are aware of the limitation of data and methodology used to estimate the demands,\
    and we are working to improve with your feedback.")