import streamlit as st
st.set_option('deprecation.showPyplotGlobalUse', False)
import pandas as pd
import plotly.graph_objects as go

import helpers as h
from LCA import LCA

from config.config import *

import config.init
config.init.run()

from Start import df_vehicles,df_areas


st.title("Total costs of ownership of different vehicles")

st.header("Visualize costs/emissions over vehicle lifetime")

#settings
veh_names = st.multiselect("Vehicles:", df_vehicles.index, default=["Typical ICEV", "Typical BEV"]) #TODO: add country flags
area = st.selectbox("Area (affects gas and electricity prices):", df_areas.index, index=1)
year = st.selectbox("Year (affects gas and electricity prices):", [2020,2021,2022], index=2)
# incentives = st.multiselect("Incentives:": ["$7,500 Federal EV Tax Credit"])
income_group = st.selectbox("Income group of vehicle buyer:", ["low", "medium", "high"]) #this determines how much of the tax credit the buyer gets (if income is very low, then the buyer might not owe a total of $7,500 in federal taxes and thus not get the full $7,500 tax credit) and what discount rate the buyer uses

#initialize LCA class object and run/read results
lca = LCA(df_vehicles, df_areas, veh_names, area, year)
lca.retrieve_results()

#select quantity to plot and plot it
allow_for_selection_of_non_total_columns = st.checkbox("Include annual costs/emissions in list of quantities to plot?", value=False)
if allow_for_selection_of_non_total_columns:
	y_quant_list = lca.columns[2:]
	y_quant_list_default_index = 12
else:
	y_quant_list = lca.total_columns
	y_quant_list_default_index = 6
y_quant = st.selectbox("Quantity to plot:", y_quant_list, index=y_quant_list_default_index)
fig = lca.plot_results(y_quant=y_quant)
st.pyplot(fig)

#optionally show full results in tables
show_tabular_results = st.checkbox("Show tabular results?", value=False)
if show_tabular_results:
	show_non_total_columns = st.checkbox("Show annual costs/emissions in tabular results?", value=True)
	
	for veh_name in veh_names:
		st.write("**%s:**"%veh_name)
		st.write(lca.get_results(veh_name, show_non_total_columns=show_non_total_columns))

#waterfall plot of summary results
# """
st.header("Visualize cumulative differences in costs/emissions")

#settings
veh_types = [
				"Typical", 
				"Typical Car", 
				"Sedan", 
				"Car SUV", 
				"Typical Truck", 
				"Truck SUV", 
				"Minivan/Van", 
				"Pickup"
			]
veh_names_pairs = [[veh_type+" ICEV", veh_type+" BEV"] for veh_type in veh_types]
veh_names_pairs += [["Toyota Corolla ICEV", "Chevrolet Bolt BEV"]]

#select what to show the waterfall plot for
area = st.selectbox("Area (affects gas and electricity prices):", df_areas.index, index=1, key="needs unique key because same selectbox (area) as above")
year = st.selectbox("Year (affects gas and electricity pricess):", [2020,2021,2022], index=2, key="needs unique key because same selectbox (year) as above")

plot_type_long = st.selectbox("**What would you like to see?**", plot_types_dict.keys(), index=0)
plot_type = plot_types_dict[plot_type_long] #"one_either", "one_both", or "all_either"

col1, col2 = st.columns(2)
with col1:
	if "one" in plot_type:
		veh_type = st.selectbox("Choose vehicle type:", veh_types+["affordable sedan"], index=0)
		first_string = "Shown are the **differences in costs** between an EV and an ICEV for the EPA vehicle type *{0:s}*.".format(veh_type)
		second_string = 	"+ 🟥 <font color=#800000>**Red**</font> values indicate **higher** costs for the EV. \n \
+ 🟩 <font color=#00805e>**Green**</font> values represent cost **savings** for the EV. \n \
+ 🟦 The <font color=#0068c9>**blue**</font> bar shows the **overall** cost savings of the EV over the ICEV."
	elif "all" in plot_type:
		veh_types_to_show = st.multiselect("Choose vehicle types:", veh_types+["affordable sedan"], default=["Typical Car", "Typical Truck"])
		first_string = "Shown are the **differences in costs** between an EV and an ICEV for all EPA vehicle types."
		second_string = "+ **Positive** values indicate **higher** costs for the EV. \n \
+ **Negative** values represent cost **savings** for the EV. \n \
+ The **last** bar shows the **overall** cost savings of the EV over the ICEV."
with col2:
	if "either" in plot_type:
		show_nominal_or_PV = st.selectbox("Show nominal or discounted costs?", ["Nominal (future value)", "Discounted (present value)"], index=0)
		show_PV_dict = {"Nominal (future value)": 0, "Discounted (present value)": 1}
		show_PV = show_PV_dict[show_nominal_or_PV]

st.write(first_string)
st.markdown(second_string, unsafe_allow_html=True)

if plot_type == "one_either":
	fig_one_either = h.plot_waterfall_one_either(veh_type, area, year, show_PV, save_figure=False)
	st.plotly_chart(fig_one_either, sharing="streamlit", use_container_width=True)
elif plot_type == "one_both":
	fig_one_both = h.plot_waterfall_one_both(veh_type, area, year, save_figure=False)
	st.plotly_chart(fig_one_both, sharing="streamlit", use_container_width=True)
elif plot_type == "all_either":
	fig_all_either = h.plot_waterfall_all_either(veh_types_to_show, area, year, show_PV, save_figure=False)
	st.plotly_chart(fig_all_either, sharing="streamlit", use_container_width=True)






def write(data):
	# df, df_key = data
	
	
	# st.write("Have fun exploring the data! 💡")
	
	#select vehicles
	"""
	EV = st.multiselect("Electric vehicles:", ["Tesla Model S (2022)", "Tesla Model 3", "Nissan Leaf", "Chevrolet Bolt"], default=["Tesla Model S (2022)", "Nissan Leaf"])
	ICEV_models = st.multiselect("Conventional vehicles:", ["Toyota Corolla", "Honda Civic"], default=["Toyota Corolla"])
	
	#choose location
	country = st.selectbox("Country:", ["Germany", "EU-28", "China", "United States"]) #TODO: add country flags
	subregion = st.selectbox("Subregion (e.g. state):", ["WA", "CA", "OR", "NY"]) #TODO: list to depend on selected country
	
	#year of purchase, vehicle lifetime mileage, annual mileage, ...
	
	# fac = st.selectbox("Airport:", df.index.levels[1].to_list())
	# aggregation = st.radio("Aggregate data by:", agg_options, index=agg_options.index("Month"))
	"""
	
	
	
	"""
	if category == "costs":
		print(costs)
		
		for i in range(int(len(names)/2)): #TODO: show these results in a dataframe
			icev_type = names[[idx for idx, s in enumerate(names) if "ICEV" in s][i]]
			bev_type  = names[[idx for idx, s in enumerate(names) if "BEV" in s][i]]
			
			print("\n{0:s} vs. {1:s}:".format(icev_type, bev_type))
			
			print("\tWithout CPS:")
			print("\t- purchase price premium of EV:     ${0:5.0f}".format(costs.loc[bev_type, "prod"]-costs.loc[icev_type, "prod"]))
			print("\t- 100% of total fuel savings of EV: ${0:5.0f}".format(costs.loc[icev_type, "use"]-costs.loc[bev_type, "use"]))
			print("\t-  {1:.0f}% of total fuel savings of EV: ${0:5.0f}".format(valuation_ratio*(costs.loc[icev_type, "use"]-costs.loc[bev_type, "use"]), 100*valuation_ratio))
			print("\t- annual fuel savings of EV:        ${0:5.0f}".format(costs.loc[icev_type, "avg. annual use"]-costs.loc[bev_type, "avg. annual use"]))
			
		
		# costs.loc[bev_type, "prod"]-costs.loc[icev_type, "prod"] < 0.50*(costs.loc[icev_type, "use"]-costs.loc[bev_type, "use"])
		
		
	# """


