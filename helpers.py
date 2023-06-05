import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from LCA import LCA

from config.config import *

from Start import df_vehicles,df_areas,df_income_groups


def get_fn(area, year, income_group, custom_discount_rate):
	fn = "area={0:s}_year={1:d}_income_group={2:s}".format(area, year, income_group)
	if custom_discount_rate is not None:
		# fn += "_{0:g}%".format(custom_discount_rate*100)
		fn += "_custom_discount_rate"
	return fn

def get_diff_cum_df_fn_full(area, year, income_group, custom_discount_rate):
	""" Get full filename for dataframe of cumulative cost differences for all vehicle pairs """
	diff_cum_df_fn_full = "results/"+"cumulative differences/"+get_fn(area, year, income_group, custom_discount_rate)+".csv"
	return diff_cum_df_fn_full

def run_LCA_for_all_veh_types(df_vehicles, df_areas, df_income_groups, area, year, income_group, custom_discount_rate):
	diff_cum_df = pd.DataFrame()
	
	for veh_type in veh_names_pairs_dict:
		veh_names = veh_names_pairs_dict[veh_type]
		
		#initialize LCA class object and run/read results
		lca = LCA(df_vehicles, df_areas, df_income_groups, veh_names, area, year, income_group, custom_discount_rate)
		lca.retrieve_results()
		
		#derive differences
		diff = lca.get_results(veh_names[1]).select_dtypes(include=numerics) - lca.get_results(veh_names[0]).select_dtypes(include=numerics)
		diff_cum = diff.loc["post-use", lca.total_columns]
		
		if veh_names[0].replace("ICEV", "BEV") == veh_names[1]:
			fn = veh_names[0].replace(" ICEV", "")
		elif veh_names[0]=="Toyota Corolla ICEV" and veh_names[1]=="Chevrolet Bolt BEV":
			fn = "affordable sedan"
		diff_cum_df[fn] = diff_cum
	diff_cum_df.index.name = "quantity"

	#save differences in csv file
	diff_cum_df_fn_full = get_diff_cum_df_fn_full(area, year, income_group, custom_discount_rate)
	diff_cum_df.to_csv(diff_cum_df_fn_full)
	
	return diff_cum_df

def plot_waterfall_one_either(veh_type, area, year, income_group, custom_discount_rate=None, show_PV=True, save_figure=False):
	"""
	Waterfall plot for **one** vehicle type, showing **either** nominal or present value cost differences.
	"""
	
	diff_cum_df_fn_full = get_diff_cum_df_fn_full(area, year, income_group, custom_discount_rate)
	if os.path.isfile(diff_cum_df_fn_full) and custom_discount_rate is None: #read-in cumulative results data
		diff_cum_df = pd.read_csv(diff_cum_df_fn_full, index_col="quantity")
	else: #calculate cumulative results data
		diff_cum_df = run_LCA_for_all_veh_types(df_vehicles, df_areas, df_income_groups, area, year, income_group, custom_discount_rate)
	
	cols_for_waterfall_plot = ["total "+cost_type+" costs [$]" for cost_type in cost_types]
	if show_PV:
		cols_for_waterfall_plot = [col.replace("total", "total present value") for col in cols_for_waterfall_plot]
		ylabel = "<b>Cost differences (present value)</b>"
		y = list(diff_cum_df.loc[cols_for_waterfall_plot,veh_type]) + [diff_cum_df.loc["total present value costs [$]",veh_type]]
	else:
		ylabel = "<b>Cost differences (nominal)</b>"
		y = list(diff_cum_df.loc[cols_for_waterfall_plot,veh_type]) + [diff_cum_df.loc["total costs [$]",veh_type]]
	# st.write(cols_for_waterfall_plot)
	
	fig = go.Figure()
	
	#plot cost differences
	fig.add_trace(go.Waterfall(
		name = "Cost differences", orientation = "v",
		measure = [*["relative" for i in cost_types], "total"],
		x = cost_types+["total"], 
		textposition = "outside",
		text = ["<b>{0}${1:.1f}k</b>".format('+-'[i<0], abs(i/1000)) for i in y], 
		textfont_color = "black", 
		textfont_size = fsize, 
		y = y, 
		connector = {"line":{"color":"rgb(63, 63, 63)"}}, 
		decreasing = {"marker":{"color":"#00805e"}}, 
		increasing = {"marker":{"color":"Maroon"}}, 
		totals = {"marker":{"color":"#0068c9"}}, #deep sky blue"}}, 
	))

	fig.add_hline(y=0)

	ylow  = min(-21000, *(np.array(y)-5000))
	yhigh = max(21000, *(np.array(y)+5000))

	layout = dict(
		# height=600, 
		# title = "Comparable %s ICEV vs. EV"%veh_type,
		# showlegend = True, 
		hoverlabel_namelength=-1, #do not truncate the hoverlabels
		
		# yaxis_range = yaxis_ranges[airport], 
		xaxis = dict(
			title = "<b>Cost category</b>", 
			title_font_color = "black", 
			tickfont_color = "black", 
			tickfont_size = fsize, 
			title_font_size = fsize*ffactor, 
			tickmode = 'array',
			tickvals = [0,1,2,3,4,5],
			ticktext = ticktext, 
		), 
		yaxis = dict(
			range = [ylow,yhigh], 
			title = ylabel, 
			title_font_color = "black", 
			tickfont_color = "black", 
			tickfont_size = fsize, 
			title_font_size = fsize*ffactor,  
			gridcolor = "grey", 
			tickformat = "$,", 
		), 
		# hovermode='x unified', 
		# hovermode='x', 
		# legend=dict(yanchor="bottom", y=1.02, xanchor="center", x=0.5),
		# legend_orientation="h"
		margin=go.layout.Margin(
			l=20, #left margin
			r=20, #right margin
			b=20, #bottom margin
			t=20, #top margin
		), 
		yaxis_title_standoff=10, yaxis_automargin=True, 
		xaxis_title_standoff=20, xaxis_automargin=True, 
	)
	fig.update_layout(layout)
	
	
	if save_figure:
		suffix = "discounted" if show_PV else "nominal"
		if show_PV:
			suffix += " (default)" if custom_discount_rate is None else " ({0:.0f}%)".format(custom_discount_rate*100)
		fn = "waterfall_veh_type={0:s}_area={1:s}_year={2:d}_income_group={3:s}_{4:s}".format(veh_type.replace("/","-"), area, year, income_group, suffix)
		width = fsize*1150/22
		fig.write_image("plots/"+"waterfalls/one_either/"+fn+".png", width=width, height=0.65*width, scale=5)
	
	return fig


def plot_waterfall_one_both(veh_type, area, year, income_group, custom_discount_rate=None, save_figure=False):
	"""
	Waterfall plot for **one** vehicle type, showing **both** nominal and present value cost differences.
	"""
	
	diff_cum_df_fn_full = get_diff_cum_df_fn_full(area, year, income_group, custom_discount_rate)
	if os.path.isfile(diff_cum_df_fn_full) and custom_discount_rate is None: #read-in cumulative results data
		diff_cum_df = pd.read_csv(diff_cum_df_fn_full, index_col="quantity")
	else: #calculate cumulative results data
		diff_cum_df = run_LCA_for_all_veh_types(df_vehicles, df_areas, df_income_groups, area, year, income_group, custom_discount_rate)
	
	fig = go.Figure()
	
	#plot nominal (undiscounted) cost differences
	cols_for_waterfall_plot = ["total "+cost_type+" costs [$]" for cost_type in cost_types]
	y = list(diff_cum_df.loc[cols_for_waterfall_plot,veh_type]) + [diff_cum_df.loc["total costs [$]",veh_type]]
	# st.write(cols_for_waterfall_plot)
	fig.add_trace(go.Waterfall(
		name = "Nominal (undiscounted)", orientation = "v",
		measure = [*["relative" for i in cost_types], "total"],
		x = cost_types+["total"], 
		textposition = "outside",
		text = ["<b>{0}${1:.1f}k</b>".format('+-'[i<0], abs(i/1000)) for i in y], 
		textfont_color = "black", 
		textfont_size = fsize, 
		y = y, 
		connector = {"line":{"color":"rgb(63, 63, 63)"}}, 
		decreasing = {"marker":{"color":"#00805e"}}, 
		increasing = {"marker":{"color":"#800000"}}, 
		totals = {"marker":{"color":"#0068c9"}}, #deep sky blue"}}, 
	))
	
	#plot present value (discounted) cost differences
	cols_for_waterfall_plot = ["total present value "+cost_type+" costs [$]" for cost_type in cost_types]
	y = list(diff_cum_df.loc[cols_for_waterfall_plot,veh_type]) + [diff_cum_df.loc["total present value costs [$]",veh_type]]
	# st.write(cols_for_waterfall_plot)
	fig.add_trace(go.Waterfall(
		name = "Present value (discounted)", orientation = "v", 
		measure = [*["relative" for i in cost_types], "total"], 
		x = cost_types+["total"], 
		textposition = "outside", 
		text = ["<b>{0}${1:.1f}k</b>".format('+-'[i<0], abs(i/1000)) for i in y], 
		textfont_color = "black", 
		textfont_size = fsize, 
		y = y, 
		connector = {"line":{"color":"rgb(63, 63, 63)"}}, 
		decreasing = {"marker":{"color":"#41bf9e"}}, 
		increasing = {"marker":{"color":"#c95555"}}, 
		totals = {"marker":{"color":"#55a0e6"}}, #deep sky blue"}}, 
	))

	fig.add_hline(y=0)

	ylabel = "<b>Cost differences</b>"
	ylow  = min(-21000, *(np.array(y)-5000))
	yhigh = max(21000, *(np.array(y)+5000))

	layout = dict(
		waterfallgroupgap = 0.15, 
		# height=600, 
		# title = "Comparable %s ICEV vs. EV"%veh_type,
		# showlegend = True, 
		hoverlabel_namelength=-1, #do not truncate the hoverlabels
		
		# yaxis_range = yaxis_ranges[airport], 
		xaxis = dict(
			title = "<b>Cost category</b>", 
			title_font_color = "black", 
			tickfont_color = "black", 
			tickfont_size = fsize, 
			title_font_size = fsize*ffactor, 
			tickmode = 'array',
			tickvals = [0,1,2,3,4,5],
			ticktext = ticktext, 
		), 
		yaxis = dict(
			range = [ylow,yhigh], 
			title = ylabel, 
			title_font_color = "black", 
			tickfont_color = "black", 
			tickfont_size = fsize, 
			title_font_size = fsize*ffactor,  
			gridcolor = "grey", 
			tickformat = "$,", 
		), 
		# hovermode='x unified', 
		# hovermode='x', 
		legend=dict(yanchor="bottom", y=1.02, xanchor="center", x=0.5),
		legend_orientation="h", 
		margin=go.layout.Margin(
			l=20, #left margin
			r=20, #right margin
			b=20, #bottom margin
			t=20, #top margin
		), 
		yaxis_title_standoff=10, yaxis_automargin=True, 
		xaxis_title_standoff=20, xaxis_automargin=True, 
	)
	fig.update_layout(layout)
	
	if save_figure:
		fn = "waterfalls_veh_type={0:s}_area={1:s}_year={2:d}_income_group={3:s}".format(veh_type.replace("/","-"), area, year, income_group)
		fn += " (discount rate=default)" if custom_discount_rate is None else " (discount rate={0:.0f}%)".format(custom_discount_rate*100)
		width = fsize*1150/22
		fig.write_image("plots/"+"waterfalls/one_both/"+fn+".png", width=width, height=0.65*width, scale=5)
	
	return fig


def plot_waterfall_all_either(veh_types_to_show, area, year, income_group, custom_discount_rate=None, show_PV=True, save_figure=False):
	"""
	Waterfall plot for **all** vehicle types, showing **either** nominal or present value cost differences.
	"""
	
	diff_cum_df_fn_full = get_diff_cum_df_fn_full(area, year, income_group, custom_discount_rate)
	if os.path.isfile(diff_cum_df_fn_full) and custom_discount_rate is None: #read-in cumulative results data
		diff_cum_df = pd.read_csv(diff_cum_df_fn_full, index_col="quantity")
	else: #calculate cumulative results data
		diff_cum_df = run_LCA_for_all_veh_types(df_vehicles, df_areas, df_income_groups, area, year, income_group, custom_discount_rate)
	
	#settings regarding whether or not to plot nominal or present value
	if show_PV:
		ylabel = "<b>Cost differences (present value)</b>"
		cols_for_waterfall_plot = ["total present value "+cost_type+" costs [$]" for cost_type in cost_types]
	else:
		ylabel = "<b>Cost differences (nominal)</b>"
		cols_for_waterfall_plot = ["total "+cost_type+" costs [$]" for cost_type in cost_types]
	
	#order veh_types_to_show according to veh_types
	veh_types_to_show = sorted(veh_types_to_show, key=(list(veh_names_pairs_dict.keys())).index)
	
	fig = go.Figure()
	
	for veh_type in veh_types_to_show:
		y = list(diff_cum_df.loc[cols_for_waterfall_plot,veh_type])
		y += [diff_cum_df.loc["total present value costs [$]",veh_type]] if show_PV else [diff_cum_df.loc["total costs [$]",veh_type]]
		# import streamlit as st
		# st.write(y)
		# l
		color = veh_types_colors[veh_type]
		
		#plot cost differences
		fig.add_trace(go.Waterfall(
			name = veh_type, orientation = "v",
			measure = [*["relative" for i in cost_types], "total"],
			x = cost_types+["total"], 
			textposition = "outside",
			text = ["<b>{0}${1:.1f}k</b>".format('+-'[i<0], abs(i/1000)) for i in y], 
			textfont_color = "black", 
			textfont_size = fsize, 
			y = y, 
			connector = {"line":{"color":"rgb(63, 63, 63)", "width":0.5}}, 
			# decreasing = {"marker":{"color":"#00805e"}}, 
			# increasing = {"marker":{"color":"#800000"}}, 
			# totals = {"marker":{"color":"#0068c9"}}, #deep sky blue"}}, 
			decreasing = {"marker":{"color":color}}, 
			increasing = {"marker":{"color":color}}, 
			totals = {"marker":{"color":color}}, #deep sky blue"}}, 
		))

	fig.add_hline(y=0)
	
	if show_PV:
		all_y = [list(diff_cum_df.loc[cols_for_waterfall_plot,veh_type]) + [diff_cum_df.loc["total present value costs [$]",veh_type]] for veh_type in veh_types_to_show]
	else:
		all_y = [list(diff_cum_df.loc[cols_for_waterfall_plot,veh_type]) + [diff_cum_df.loc["total costs [$]",veh_type]] for veh_type in veh_types_to_show]
	all_y = [item for sublist in all_y for item in sublist] #flatten the list
	ylow  = min(-21000, *(np.array(all_y)-5000))
	yhigh = max(21000, *(np.array(all_y)+5000))

	layout = dict(
		waterfallgroupgap = 0.1, 
		# height=600, 
		# title = "Comparable %s ICEV vs. EV"%veh_type,
		# showlegend = True, 
		hoverlabel_namelength=-1, #do not truncate the hoverlabels
		
		# yaxis_range = yaxis_ranges[airport], 
		xaxis = dict(
			title = "<b>Cost category</b>", 
			title_font_color = "black", 
			tickfont_color = "black", 
			tickfont_size = fsize, 
			title_font_size = fsize*ffactor, 
			tickmode = 'array',
			tickvals = [0,1,2,3,4,5],
			ticktext = ticktext, 
		), 
		yaxis = dict(
			range = [ylow,yhigh], 
			title = ylabel, 
			title_font_color = "black", 
			tickfont_color = "black", 
			tickfont_size = fsize, 
			title_font_size = fsize*ffactor,  
			gridcolor = "grey", 
			tickformat = "$,", 
		), 
		# hovermode='x unified', 
		# hovermode='x', 
		legend=dict(yanchor="bottom", y=1.02, xanchor="center", x=0.5),
		legend_orientation="h", 
		margin=go.layout.Margin(
			l=20, #left margin
			r=20, #right margin
			b=20, #bottom margin
			t=20, #top margin
		), 
		yaxis_title_standoff=10, yaxis_automargin=True, 
		xaxis_title_standoff=20, xaxis_automargin=True, 
	)
	fig.update_layout(layout)
	
	if save_figure:
		#veh_types_to_show intentionally left out of the filename to not blow it up
		suffix = "discounted" if show_PV else "nominal"
		if show_PV:
			suffix += " (default)" if custom_discount_rate is None else " ({0:.0f}%)".format(custom_discount_rate*100)
		fn = "waterfall_area={0:s}_year={1:d}_income_group={2:s}_{3:s}".format(area, year, income_group, suffix)
		width = fsize*1150/22
		fig.write_image("plots/"+"waterfalls/all_either/"+fn+".png", width=width, height=0.65*width, scale=5)
	
	return fig
