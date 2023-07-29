import os
import streamlit as st
import pandas as pd

import helpers as h

from config.config import *

from Start import df_vehicles,df_areas,df_income_groups

st.title("Summary tables of results")

st.markdown("Shown are the **differences in costs and emissions** between an EV and an ICEV for each EPA vehicle type.\n \
+ 🟥 **<font color=#800000>**Red**</font>** values indicate **higher** costs/emissions for the EV. \n \
+ 🟩 **<font color=#00805e>**Green**</font>** values represent cost/emission **savings** for the EV.", unsafe_allow_html=True)

#settings
col0_area,col0_year,col0_inc_group = st.columns(3)
with col0_area:
	area = st.selectbox("Area (affects gas and electricity prices):", df_areas.index, index=1)
with col0_year:
	year = st.selectbox("Year (affects gas and electricity prices):", [2020,2021,2022], index=2)
with col0_inc_group:
	income_group = st.selectbox("Income group of vehicle buyer:", df_income_groups.index, index=1)
custom_discount_rate_selection = st.select_slider("Select what discount rate to use:", discount_rate_options)
custom_discount_rate = None if "default" in custom_discount_rate_selection else float(custom_discount_rate_selection[:-1])/100
# incentives = st.multiselect("Incentives:": ["$7,500 Federal EV Tax Credit"])

#read-in cumulative results data
diff_cum_df_fn_full = h.get_diff_cum_df_fn_full(area, year, income_group, custom_discount_rate)
# diff_cum_df_fn = "diff_cum_all_area={0:s}_year={1:d}_income_group={2:s}".format(area,year,income_group)
# diff_cum_df = pd.read_csv("results/"+"cumulative differences/"+diff_cum_df_fn+".csv", index_col="quantity")
if custom_discount_rate is not None or not os.path.isfile(diff_cum_df_fn_full):
	#recalculate
	h.run_LCA_for_all_veh_types(df_vehicles, df_areas, df_income_groups, area, year, income_group, custom_discount_rate)
	
diff_cum_df = pd.read_csv(diff_cum_df_fn_full, index_col="quantity")

colorcode = st.checkbox("Apply colors according to cost savings/premiums?", value=False)
if colorcode:
	import matplotlib.pyplot as plt
	from matplotlib import colors
	
	def background_gradient(s, m, M, cmap='RdYlGn', low=0, high=0):
		rng = M - m
		norm = colors.Normalize(m - (rng * low),
								M + (rng * high))
		normed = norm(s.values)
		c = [colors.rgb2hex(x) for x in plt.cm.get_cmap(cmap)(normed)]
		return ['background-color: %s' % color for color in c]

	even_range = max([abs(diff_cum_df.values.min()), abs(diff_cum_df.values.max())])
	# st.dataframe(diff_cum_df.style.background_gradient(cmap=cm, low=0, high=0, axis=0, subset=None, text_color_threshold=0.408, vmin=-even_range, vmax=even_range, gmap=None))
	st.dataframe(diff_cum_df.style.apply(	background_gradient,
											cmap="RdYlGn_r",
											m=-even_range,
											M=even_range).format(precision=0))
else:
	# st.dataframe(diff_cum_df.style.set_precision(0))
	st.dataframe(diff_cum_df.style.format(precision=0))
