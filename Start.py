import streamlit as st
import pandas as pd


st.set_page_config(
		page_title="Life Cycle Assessment of Different Vehicles",
		page_icon="🚗",
		layout="wide",
		initial_sidebar_state="expanded",
	)

#####

@st.cache_data()
def get_data():
	df_vehicles = pd.read_excel("data/vehicle_types.xlsx", index_col="name")
	df_areas    = pd.read_excel("data/areas.xlsx", index_col="area")
	
	return df_vehicles,df_areas

df_vehicles,df_areas = get_data()

def main():
	# application architecture
	st.sidebar.title("Vehicle total costs of ownership tool 🚗🚙🚐")
	st.sidebar.subheader("Navigation")
	
	st.sidebar.info("**Author:** Steffen Coenen")
	
	st.sidebar.info("**Full material:** The full dataset and all code is available at the corresponding [GitHub repository](link to GitHub repo).")

if __name__ == "__main__":
	main()

