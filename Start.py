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
	df_vehicles      = pd.read_excel("data/vehicle_types.xlsx", index_col="name")
	df_areas         = pd.read_excel("data/areas.xlsx", index_col="area")
	df_income_groups = pd.read_excel("data/income_groups.xlsx", index_col="household income group")
	
	return df_vehicles,df_areas,df_income_groups

df_vehicles,df_areas,df_income_groups = get_data()

def main():
	# application architecture
	st.sidebar.title("Vehicle total costs of ownership tool 🚗🚙🚐")
	# st.sidebar.subheader("Navigation")
	
	st.sidebar.info("**Author:** Steffen Coenen")
	
	st.sidebar.info("**Full material:** The full dataset and all code is available at the corresponding [GitHub repository](https://github.com/steffen-coe/vehicle-consumer-choice-support-tool).")

if __name__ == "__main__":
	main()

