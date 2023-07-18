import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from geopy.geocoders import Nominatim
from fpdf import FPDF
import base64
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="district_locator")
st.set_page_config(page_title='Fleet Lab District Dashboard', layout='wide')

#logo
from PIL import Image
def add_logo(logo_path, width, height):
    """Read and return a resized logo"""
    logo = Image.open(logo_path)
    modified_logo = logo.resize((width, height))
    return modified_logo
my_logo = add_logo(logo_path="you!.png", width=350, height=150)
st.image(my_logo)
# logo



# writing dataframes
df = pd.read_csv('states_combined_final.csv')
df['zip_code'] = df['zip_code'].str.zfill(5)
epa_df = pd.read_csv('epalist.csv')
epa_df['nces_district_id'] = epa_df['nces_district_id'].astype(int)
df = pd.merge(df, epa_df, on='nces_district_id', how='left')

df['epa_high_priority'] = df['epa_high_priority'].fillna('Not an EPA District')
df['epa_rural_indicator'] = df['epa_rural_indicator'].fillna('No')


superintendent_df = pd.read_csv('superintendent_info_2.csv')


df['enrolled_students'] = pd.to_numeric(df['enrolled_students'], errors='coerce')
df['number_of_schools'] = pd.to_numeric(df['number_of_schools'], errors='coerce')

# Sidebar Directory    
selected_state = st.sidebar.selectbox('Select state', sorted(df['state'].unique()))
filtered_df = df[df['state'] == selected_state]


# checkbox fordistrict setting and type
st.sidebar.text("Optional:", help="Filter Districts by setting or type (City, Rural, Town)")
filter_district_setting = st.sidebar.checkbox('*Filter by District Setting*')
filter_district_setting_type = st.sidebar.checkbox('*Filter by District Setting Type*')

# EPA filtering
rural_indicator = st.sidebar.checkbox('*EPA Rural districts*')
epa_high_priority_setting = st.sidebar.checkbox('*EPA High Priority*')

if rural_indicator:
    filtered_df = filtered_df[filtered_df['epa_rural_indicator'] == 'Yes']

if epa_high_priority_setting:
    epa_high_select = st.sidebar.selectbox('Select EPA Type', filtered_df['epa_high_priority'].unique())
    filtered_df = filtered_df[filtered_df['epa_high_priority'] == epa_high_select]


# filter if checkboxes selected
if filter_district_setting:
    selected_district_setting = st.sidebar.selectbox('Select District Setting', filtered_df['district_setting'].unique())
    filtered_df = filtered_df[filtered_df['district_setting'] == selected_district_setting]
if filter_district_setting_type:
    selected_district_setting_type = st.sidebar.selectbox('Select District Setting Type', filtered_df['district_setting_type'].unique())
    filtered_df = filtered_df[filtered_df['district_setting_type'] == selected_district_setting_type]

selected_district = st.sidebar.selectbox('Select district', filtered_df['district_name'].unique())
filtered_df_district = df[df['district_name'] == selected_district]
# End of sidebar 

selected_nces_id = filtered_df_district['nces_district_id'].iloc[0]
filtered_state = filtered_df_district['state']
filtered_district_setting = filtered_df_district['district_setting']
filtered_district_setting_type = filtered_df_district['district_setting_type']
filtered_district_type = filtered_df_district['district_type']


columns_to_average = ['enrolled_students','number_of_schools','est_transportation_expenditures','est_total_miles','cost_per_student','cost_per_mile','est_miles_per_student_per_year','est_school_days_per_year','est_miles_per_student_per_day','district_size_sq_mi','district_owned_vehicles','contractor_vehicles','total_vehicles','district_miles','contractor_miles','number_per_vehicle','cost_per_vehicle','gallons_consumed','miles_per_gallon','bus_driver_salary','transport_staff_salaries','total_transport_salaries','average_distance_travelled_by_student','average_cost_per_mile','avg_number_students_transported','route_miles']
column_names = {'enrolled_students': 'Enrolled Students',     'number_of_schools': 'Number of Schools',     'est_transportation_expenditures': 'Estimated Transportation Expenditures',     'est_total_miles': 'Estimated Total Miles',     'cost_per_student': 'Cost per Student',     'cost_per_mile': 'Cost per Mile',     'est_miles_per_student_per_year': 'Estimated Miles per Student per Year',     'est_school_days_per_year': 'Estimated School Days per Year',     'est_miles_per_student_per_day': 'Estimated Miles per Student per Day',     'district_size_sq_mi': 'District Size (sq mi)',     'district_owned_vehicles': 'District Owned Vehicles',     'contractor_vehicles': 'Contractor Vehicles',     'total_vehicles': 'Total Vehicles',     'district_miles': 'District Miles',     'contractor_miles': 'Contractor Miles',     'number_per_vehicle': 'Number per Vehicle',     'cost_per_vehicle': 'Cost per Vehicle',     'gallons_consumed': 'Gallons Consumed',     'miles_per_gallon': 'Miles per Gallon',     'bus_driver_salary': 'Bus Driver Salary',     'transport_staff_salaries': 'Transport Staff Salaries',     'total_transport_salaries': 'Total Transport Salaries',     'average_distance_travelled_by_student': 'Average Distance Travelled by Student',     'average_cost_per_mile': 'Average Cost per Mile',     'avg_number_students_transported': 'Average Number of Students Transported','route_miles': 'Route Miles'}
column_options = {column_names.get(col, col): col for col in columns_to_average}

# Create columns
col1, col2 = st.columns(2)

# If a district has been selected
if not filtered_df_district.empty:
    # First side of page
    with col1:
        with st.expander("District Information"):
            st.subheader(f"{filtered_df_district['district_name'].iloc[0]}")
            st.text(f"District Setting: {filtered_df_district['district_setting'].iloc[0]}")
            st.text(f"District Setting Type: {filtered_df_district['district_setting_type'].iloc[0]}")
            st.text(f"District Type : {filtered_df_district['district_type'].iloc[0]}")
            st.text(f"County: {filtered_df_district['county'].iloc[0]}")
            st.text(f"EPA Rural: {filtered_df_district['epa_rural_indicator'].iloc[0]}")
            st.text(f"EPA High Priority: {filtered_df_district['epa_high_priority'].iloc[0]}")

         # Display superintendent information
        selected_superintendent_info = superintendent_df[superintendent_df['nces_district_id'] == selected_nces_id]
        if not selected_superintendent_info.empty:
            with st.expander('Superintendent Information'):
                st.text(f"Name: {selected_superintendent_info['name'].iloc[0]}")
                st.text(f"Phone: {selected_superintendent_info['phone'].iloc[0]}")
                st.text(f"Email: {selected_superintendent_info['email'].iloc[0]}")
        selected_avg_columns = st.multiselect('Select columns to calculate average', list(column_options.keys()))
        selected_columns_mapped = [column_options[col] for col in selected_avg_columns]
        if selected_district and selected_columns_mapped:
            for column in selected_columns_mapped:
                district_type = filtered_df_district['district_type'].iloc[0]
                district_setting = filtered_df_district['district_setting'].iloc[0]
                district_setting_type = filtered_df_district['district_setting_type'].iloc[0]
                district_state = filtered_df_district['state'].iloc[0]
                same_type_df = df[(df['district_type'] == district_type) & (df['district_setting_type'] == district_setting_type) & (df['state'] == district_state) & (df['district_setting'] == district_setting)]
                same_type_avg = same_type_df[column].mean()
                selected_district_avg = filtered_df_district[column].mean()
                avg_df = pd.DataFrame({
                    'Type': [filtered_df_district['district_name'].iloc[0], 
                            f"Average of {filtered_df_district['district_setting_type'].iloc[0]} {filtered_df_district['district_setting'].iloc[0]} Districts in {filtered_df_district['state'].iloc[0]} "],
                    'Average': [selected_district_avg, same_type_avg]
                })
                st.subheader(f'{column_names.get(column)}',help="Same Type District: Average of All Districts With Same State, District Setting and Type")

                # Bar Charts

                y_titles = {
                            'enrolled_students': 'Number of Students',
                            'number_of_schools': 'Number of Schools',
                            'est_transportation_expenditures': 'Dollars',
                            'est_total_miles': 'Miles',
                            'cost_per_student': 'Dollars',
                            'cost_per_mile': 'Dollars',
                            'est_miles_per_student_per_year': 'Miles',
                            'est_school_days_per_year': 'School Days',
                            'est_miles_per_student_per_day': 'Miles',
                            'district_size_sq_mi': 'Square Miles',
                            'district_owned_vehicles': 'Number of Vehicles',
                            'contractor_vehicles': 'Number of Vehicles',
                            'total_vehicles': 'Number of Vehicles',
                            'district_miles': 'Miles',
                            'contractor_miles': 'Miles',
                            'number_per_vehicle': 'Number per Vehicle',
                            'cost_per_vehicle': 'Dollars',
                            'gallons_consumed': 'Gallons',
                            'miles_per_gallon': 'Miles per Gallon',
                            'bus_driver_salary': 'Dollars',
                            'transport_staff_salaries': 'Dollars',
                            'total_transport_salaries': 'Dollars',
                            'average_distance_travelled_by_student': 'Miles',
                            'average_cost_per_mile': 'Dollars',
                            'avg_number_students_transported': 'Number of Students',
                            'route_miles': 'Miles'
                        }
                labels_order = [selected_district_avg,same_type_avg]
                chart = alt.Chart(avg_df).mark_bar().encode(
                    x=alt.X('Type', axis=alt.Axis(labelAngle=0, labelLimit=1000), sort=labels_order),
                    y=alt.Y('Average', title=y_titles.get(column)),
                    color=alt.Color('Type', legend=None), 
                    tooltip=['Type', 'Average']
                ).interactive().properties(
                    width=800,  
                    height=400   
                ).configure_axis(
                    labelFontSize=14,
                    titleFontSize=17)
                chart.encoding.x.title = 'Districts'
                st.altair_chart(chart)

# Second side of page
with col2:
    # Show map
        zip_code = filtered_df_district['zip_code'].iloc[0]
        location = geolocator.geocode({'postalcode': zip_code, 'country': 'United States'}, timeout=10)

        if location is not None:
            data = pd.DataFrame({
                'lat': [location.latitude],
                'lon': [location.longitude]
            })
            st.map(data,zoom=11)
        else:
            st.warning(f"Please select a District.")

# PDF generator 
def create_download_link(val, filename):
    b64 = base64.b64encode(val)
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'
def export_as_pdf(district_info, avg_df):
    # new pdf file
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size = 15)
    pdf.cell(200, 10, txt = "District Information", ln = True, align = 'C')
    for key, value in district_info.items():
        pdf.cell(200, 10, txt = f"{key}: {value}", ln=True)
    pdf.cell(200, 10, txt = "Averages", ln = True, align = 'C')
    for index, row in avg_df.iterrows():
        pdf.cell(200, 10, txt = f"{row['Type']}: {row['Average']}", ln=True)
    return pdf.output(dest="S").encode("latin-1")

# download button 
if st.button("Export as PDF"):
    district_info = {  # Data to be added
        "District": filtered_df_district['district_name'].iloc[0],
        "County": filtered_df_district['county'].iloc[0],
        "NCES District ID": filtered_df_district['nces_district_id'].astype(int).iloc[0],
        "State": filtered_df_district['state'].iloc[0],
        "Zip Code": filtered_df_district['zip_code'].iloc[0],
        "Zip Plus Four": filtered_df_district['zip_plus_four'].astype(int).iloc[0]
    }

    pdf = export_as_pdf(district_info, avg_df)
    html = create_download_link(pdf, "district_report")
    st.markdown(html, unsafe_allow_html=True)



# # Map the district information to zip codes
# district_zip_data = filtered_df[['district_name', 'zip_code']]

# # Create a map centered on the United States
# m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)

# # Add markers for each district's zip code
# for idx, row in district_zip_data.iterrows():
#     district_name = row['district_name']
#     zip_code = row['zip_code']
#     tooltip = f"District: {district_name}"
#     folium.Marker(location=[zip_code], popup=district_name, tooltip=tooltip).add_to(m)

# # Display the map
# st.subheader('District Map')
# st.map(m)

# zip_code = filtered_df_district['zip_code'].iloc[0]
# location = geolocator.geocode({'postalcode': zip_code, 'country': 'United States'})

# if location is not None:
#     data = pd.DataFrame({
#         'lat': [location.latitude],
#         'lon': [location.longitude]
#         })
#     st.map(data,zoom=7)
# else:
#     st.warning(f"Please select a District.")

# from geopy.geocoders import Nominatim

# geolocator = Nominatim(user_agent="geoapiExercises")
# import time

# def geolocate(zip_code):
#     location = geolocator.geocode(zip_code)
#     time.sleep(5)  # This adds a 1 second delay before the next request
#     if location:
#         return location.latitude, location.longitude

# # Assuming df is your dataframe and it has a column 'zip_code'
# df['lat'], df['lon'] = zip(*df['zip_code'].apply(geolocate))

# import pydeck as pdk

# # Assuming df is your dataframe and now it has columns 'lat', 'lon', and 'district_name'

# # Create a pydeck chart
# layer = pdk.Layer(
#     "ScatterplotLayer",
#     df,
#     pickable=True,
#     opacity=0.8,
#     stroked=True,
#     filled=True,
#     radius_scale=100,
#     radius_min_pixels=10,
#     radius_max_pixels=100,
#     line_width_min_pixels=1,
#     get_position=["lon", "lat"],
#     get_radius=100,
#     get_fill_color=[255, 140, 0],
#     get_line_color=[0, 0, 0],
# )

# # Set the viewport location
# view_state = pdk.ViewState(latitude=37.7749, longitude=-122.4194, zoom=6, bearing=0, pitch=0)

# # Render
# tooltip={
#             "html": "<b>District:</b> {district_name}",
#             "style": {"backgroundColor": "steelblue", "color": "white"},
#         }

# r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)
# st.pydeck_chart(r)

