import streamlit as st
st.set_option('deprecation.showPyplotGlobalUse', False)
import pandas as pd
import numpy as np
import plotly.graph_objects as go

import helpers as h
from LCA import LCA

from config.config import *

import config.init
config.init.run()

from Start import df_vehicles,df_areas,df_income_groups


st.title("Total costs of ownership of different vehicles")

st.header("Visualize costs/emissions over vehicle lifetime")

#settings
veh_names = st.multiselect("Vehicles:", df_vehicles.index, default=["Typical ICEV", "Typical BEV"]) #TODO: add country flags
col0_area,col0_year,col0_inc_group = st.columns(3)
with col0_area:
	area = st.selectbox("Area (affects gas and electricity prices):", df_areas.index, index=1)
with col0_year:
	year = st.selectbox("Year (affects gas and electricity prices):", [2020,2021,2022], index=2)
with col0_inc_group:
	income_group = st.selectbox("Income group of vehicle buyer:", df_income_groups.index, index=1)
custom_discount_rate_selection = st.select_slider("Select what discount rate to use:", discount_rate_options)
custom_discount_rate = None if "default" in custom_discount_rate_selection else np.float(custom_discount_rate_selection[:-1])/100
# incentives = st.multiselect("Incentives:": ["$7,500 Federal EV Tax Credit"])

#initialize LCA class object and run/read results
# lca = LCA(df_vehicles, df_areas, df_income_groups, veh_names, area, year, income_group)
#slider to specify discount rate
#think about mechanism to store results with custom discoutn rates, probably just in a separate file with a suffix "_custom_discount_rate" without specifying what it is, rather calculate new every time (need to make sure that when custom_discount_rate is not None that results are calculated new and not read from existing file)
lca = LCA(df_vehicles, df_areas, df_income_groups, veh_names, area, year, income_group, custom_discount_rate)
lca.retrieve_results()

#select quantity to plot and plot it
allow_for_selection_of_non_total_columns = st.checkbox("Include annual costs/emissions in list of quantities to plot", value=False)
if allow_for_selection_of_non_total_columns:
	y_quant_list = lca.columns[2:]
else:
	y_quant_list = lca.total_columns
# y_quant_list_default_index = y_quant_list.index("total costs [$]")
y_quant_list_default_index = y_quant_list.index("total present value costs [$]")
y_quant = st.selectbox("Quantity to plot:", y_quant_list, index=y_quant_list_default_index)
fig = lca.plot_results(y_quant=y_quant)
col01, col02 = st.columns([1.5,1])
with col01:
	st.pyplot(fig)

#optionally show full results in tables
show_tabular_results = st.checkbox("Show tabular results", value=False)
if show_tabular_results:
	show_non_total_columns = st.checkbox("Show annual costs/emissions in tabular results", value=True)
	
	for veh_name in veh_names:
		st.write("**%s:**"%veh_name)
		st.write(lca.get_results(veh_name, show_non_total_columns=show_non_total_columns))



#waterfall plot of summary results
st.header("Visualize cumulative differences in costs/emissions")

#select what to show the waterfall plot for
col1_area,col1_year,col1_inc_group = st.columns(3)
with col1_area:
	area = st.selectbox("Area (affects gas and electricity prices):", df_areas.index, index=1, key="needs unique key because same selectbox (area) as above")
with col1_year:
	year = st.selectbox("Year (affects gas and electricity prices):", [2020,2021,2022], index=2, key="needs unique key because same selectbox (year) as above")
with col1_inc_group:
	income_group = st.selectbox("Income group of vehicle buyer:", df_income_groups.index, index=1, key="needs unique key because same selectbox (income group) as above")

plot_type_long = st.selectbox("**What would you like to see?**", plot_types_dict.keys(), index=0)
plot_type = plot_types_dict[plot_type_long] #"one_either", "one_both", or "all_either"

#say what will be shown in the waterfall plot
show_slider = False
col1, col2 = st.columns(2)
with col1:
	if "one" in plot_type:
		# veh_type = st.selectbox("Choose vehicle type:", veh_types+["affordable sedan"], index=0)
		veh_type = st.selectbox("Choose vehicle type:", veh_names_pairs_dict.keys(), index=0)
		first_string = "Shown are the **differences in costs** between an EV and an ICEV for the EPA vehicle type *{0:s}*.".format(veh_type)
		second_string = 	"+ 🟥 <font color=#800000>**Red**</font> values indicate **higher** costs for the EV. \n \
+ 🟩 <font color=#00805e>**Green**</font> values represent cost **savings** for the EV. \n \
+ 🟦 The <font color=#0068c9>**blue**</font> bar shows the **overall** cost savings of the EV over the ICEV."
	elif "all" in plot_type:
		veh_types_to_show = st.multiselect("Choose vehicle types:", veh_names_pairs_dict.keys(), default=["Typical Car", "Typical Truck"])
		first_string = "Shown are the **differences in costs** between an EV and an ICEV for all EPA vehicle types."
		second_string = "+ **Positive** values indicate **higher** costs for the EV. \n \
+ **Negative** values represent cost **savings** for the EV. \n \
+ The **last** bar shows the **overall** cost savings of the EV over the ICEV."
with col2:
	if "either" in plot_type:
		show_nominal_or_PV = st.selectbox("Show nominal or discounted costs?", ["Nominal (future value)", "Discounted (present value)"], index=1)
		show_PV_dict = {"Nominal (future value)": 0, "Discounted (present value)": 1}
		show_PV = show_PV_dict[show_nominal_or_PV]
		if show_PV:
			show_slider = True
	elif "both" in plot_type:
		show_slider = True
if show_slider: #only show slider to customize discount rate when needed (either when only discounted values are shown or when both nominal and discounted values are shown)
	custom_discount_rate_selection = st.select_slider("Select what discount rate to use:", discount_rate_options, key="needs unique key because same selectbox (discount rate) as above")
	custom_discount_rate = None if "default" in custom_discount_rate_selection else float(custom_discount_rate_selection[:-1])/100
st.write(first_string)
st.markdown(second_string, unsafe_allow_html=True)

#plot the waterfall plot
if plot_type == "one_either":
	fig_one_either = h.plot_waterfall_one_either(veh_type, area, year, income_group, custom_discount_rate, show_PV, save_figure=False)
	fig = fig_one_either
elif plot_type == "one_both":
	fig_one_both = h.plot_waterfall_one_both(veh_type, area, year, income_group, custom_discount_rate, save_figure=False)
	fig = fig_one_both
elif plot_type == "all_either":
	fig_all_either = h.plot_waterfall_all_either(veh_types_to_show, area, year, income_group, custom_discount_rate, show_PV, save_figure=False)
	fig = fig_all_either

st.plotly_chart(fig, sharing="streamlit", use_container_width=True, height=0.6)



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


