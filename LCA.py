import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import streamlit as st

import utils as u
from config.config import *

class LCA:
	def __init__(self, df_vehicles, df_areas, df_income_groups, veh_names, area, year, income_group):
		self.df_vehicles = df_vehicles
		self.df_areas = df_areas
		self.df_income_groups = df_income_groups
		self.veh_names = veh_names
		self.area = area
		self.year = year
		self.income_group = income_group
		
		#old way: get annual mileage and lifetime mileage from first selected vehicle (and determine lifetime from that)
		# veh_name0 = self.veh_names[0] #use first vehicle in selection to set annual and lifetime mileage
		# self.annual_mileage = int(self.df_vehicles.loc[veh_name0, "annual_mileage [mi]"])
		# self.lifetime_mileage = int(self.df_vehicles.loc[veh_name0, "lifetime_mileage [mi]"])
		# self.lifetime = self.lifetime_mileage / self.annual_mileage #in years
		
		#now: get annual mileage and lifetime from income group (and determine lifetime mileage from that)
		annual_mileage_col = "average annual mileage per vehicle (U.S.) [mi]" #could in theory depend on area AND income group
		self.annual_mileage = self.df_income_groups.loc[self.income_group, annual_mileage_col]
		self.lifetime = self.df_income_groups.loc[self.income_group, "average vehicle age [years]"]
		self.lifetime_mileage = self.annual_mileage * self. lifetime
		
		self.lifetime = round(self.lifetime, 2)
		self.lifetime_range = list(range(int(np.floor(self.lifetime))+1))
		if int(self.lifetime) != self.lifetime: #if lifetime is an even number, we do not need to add another element to self.lifetime_range
			self.lifetime_range += [self.lifetime]
		# print(self.annual_mileage,self.lifetime,self.lifetime_mileage)
		
		# filename = "{0:s}_{1:s}_area={2:s}_{3:d}_cps={4:s}.png".format(str(df.loc[veh_name, "regulatory_class"]), category, area, year)
		
		self.times = ["pre-purchase", *self.lifetime_range, "post-use"]
		self.columns = [
							"time [yr]", "time (for plotting) [yr]", #only needed for calculations, the actual time is in the index
							"mileage [mi]", "total mileage [mi]", 
							"purchase costs [$]", "total purchase costs [$]", 
							"incentives costs [$]", "total incentives costs [$]", 
							"operations costs [$]", "total operations costs [$]", 
							"insurance costs [$]", "total insurance costs [$]", 
							"maintenance costs [$]", "total maintenance costs [$]", 
							"costs [$]", "total costs [$]", 
							"future costs [$]", "total future costs [$]", #everything but purchase costs
							"present value purchase costs [$]", "total present value purchase costs [$]", 
							"present value incentives costs [$]", "total present value incentives costs [$]", 
							"present value operations costs [$]", "total present value operations costs [$]", 
							"present value insurance costs [$]", "total present value insurance costs [$]", 
							"present value maintenance costs [$]", "total present value maintenance costs [$]", 
							"present value costs [$]", "total present value costs [$]", 
							"present value future costs [$]", "total present value future costs [$]", 
							"emissions [tCO$_2$-eq.]", "total emissions [tCO$_2$-eq.]"
			]
		
		#define subsets of the columns
		self.non_total_columns = [col for col in self.columns if not "total" in col and "time" not in col]
		self.total_columns = [col for col in self.columns if "total" in col]
		self.non_total_undiscounted_cost_columns = [col for col in self.columns if "cost" in col and "total" not in col and "present value" not in col]
		self.non_total_discounted_cost_columns = [col for col in self.columns if "cost" in col and "total" not in col and "present value" in col]
		self.costs_columns = [col for col in self.columns if "costs" in col]
		self.emissions_columns = [col for col in self.columns if "emissions" in col]
		
		#initialize results dataframe
		df_results = pd.DataFrame(index=self.times, columns=self.columns)
		df_results.index.name = "period [yr]"
		
		#set contributions in pre-purchase and post-use phase
		df_results.loc["pre-purchase"] = 0
		df_results.loc["post-use", self.non_total_columns] = 0
		
		#prepare time helper column
		df_results["time [yr]"] = df_results.index
		df_results.loc["pre-purchase", "time [yr]"] = 0
		df_results.loc["post-use", "time [yr]"] = df_results.iloc[-2].name
		df_results["time (for plotting) [yr]"] = df_results.index
		df_results.loc["pre-purchase", "time (for plotting) [yr]"] = -0.1*self.lifetime
		df_results.loc["post-use", "time (for plotting) [yr]"] = 1.1*self.lifetime
		
		#fill in mileage column
		df_results.loc[0, "mileage [mi]"] = 0
		# print(df_results)
		# print(self.lifetime_range)
		# print(df_results["time [yr]"].diff())
		# print(self.annual_mileage)
		df_results.loc[self.lifetime_range[1:], "mileage [mi]"] = df_results["time [yr]"].diff() * self.annual_mileage
		
		self.results = dict()
		self.results_fns = dict()
		for veh_name in self.veh_names:
			self.results[veh_name] = df_results.copy()
			self.results_fns[veh_name] = "veh_name={0:s}_area={1:s}_year={2:d}_income_group={3:s}.csv".format(veh_name.replace("/","-"), self.area, self.year, self.income_group) #results filenames
	
	def retrieve_results(self):
		for veh_name in self.veh_names:
			if os.path.isfile("results/"+self.results_fns[veh_name]):
				self.read_results(veh_name)
			else:
				self.run(veh_name)
	
	def mi2yr(self, miles):
		return miles/self.annual_mileage

	def yr2mi(self, years):
		return years*self.annual_mileage
	
	def get_fuel_cost_per_mile(self, veh_name):
		if self.df_vehicles.loc[veh_name, "powertrain_type"] == "ICEV":
			fuel_cost_per_mile = self.df_areas.loc[self.area, "gas_price %d [$/gal]"%self.year] / self.df_vehicles.loc[veh_name, "real-world mpg [mi/gal]"]
		elif self.df_vehicles.loc[veh_name, "powertrain_type"] == "EV":
			fuel_cost_per_mile = (0.01*((1-p_DCFC)*self.df_areas.loc[self.area, "electricity_price %d [ct/kWh]"%(self.year-1)] + p_DCFC*self.df_areas.loc["DCFC", "electricity_price %d [ct/kWh]"%(self.year-1)]) * self.df_vehicles.loc[veh_name, "energy use [kWh/mi]"])
		return fuel_cost_per_mile
	
	def get_monthly_insurance_cost(self, veh_name):
		#area and model dependency to be added later
		if self.df_vehicles.loc[veh_name, "powertrain_type"] == "ICEV":
			monthly_insurance_cost = 149
		elif self.df_vehicles.loc[veh_name, "powertrain_type"] == "EV":
			monthly_insurance_cost = 157
		return monthly_insurance_cost
	
	def get_maintenance_cost_per_mile(self, veh_name):
		#area and model dependency to be added later
		if self.df_vehicles.loc[veh_name, "powertrain_type"] == "ICEV":
			maintenance_cost_per_mile = 0.101
		elif self.df_vehicles.loc[veh_name, "powertrain_type"] == "EV":
			maintenance_cost_per_mile = 0.061
		return maintenance_cost_per_mile
	
	def get_emissions_per_mile(self, veh_name):
		if self.df_vehicles.loc[veh_name, "powertrain_type"] == "ICEV":
			emissions_per_mile = self.df_vehicles.loc[veh_name, "real-world CO2 emissions [g/mi]"]
		elif self.df_vehicles.loc[veh_name, "powertrain_type"] == "EV":
			emissions_per_mile = self.df_vehicles.loc[veh_name, "energy use [kWh/mi]"] * self.df_areas.loc[self.area, "electricity_emission_intensity 2021 [g/kWh]"] / eff_charging
		return emissions_per_mile*1e-6 #g to t conversion
	
	def run(self, veh_name):
		results_df = self.results[veh_name].copy()
		
		#purchase cost
		results_df.loc[0, "purchase costs [$]"] = self.df_vehicles.loc[veh_name, "average transaction price [$]"]
		if self.df_vehicles.loc[veh_name, "powertrain_type"] == "EV": #apply federal EV tax credit
			# results_df.loc[1, "incentives costs [$]"] = -7500
			results_df.loc[1, "incentives costs [$]"] = - self.df_income_groups.loc[self.income_group, "maximum benefit from federal $7,500 EV tax credit"]
		
		#calculate O&M costs
		results_df["operations costs [$]"] = results_df["time [yr]"].diff() * self.annual_mileage * self.get_fuel_cost_per_mile(veh_name)
		results_df["insurance costs [$]"] = results_df["time [yr]"].diff() * self.get_monthly_insurance_cost(veh_name)*12
		results_df["maintenance costs [$]"] = results_df["time [yr]"].diff() * self.annual_mileage * self.get_maintenance_cost_per_mile(veh_name)
		
		#sum up costs
		results_df["costs [$]"] = results_df[[	"purchase costs [$]", 
												"incentives costs [$]",
												"operations costs [$]",
												"insurance costs [$]", 
												"maintenance costs [$]"]].sum(axis=1)
		results_df["future costs [$]"] = results_df[[	"incentives costs [$]",
														"operations costs [$]",
														"insurance costs [$]", 
														"maintenance costs [$]"]].sum(axis=1)
		
		#discount costs
		for col in self.non_total_undiscounted_cost_columns:
			# results_df["present value "+col] = results_df[col] / (1+R)**results_df["time [yr]"]
			results_df["present value "+col] = results_df[col] / (1+self.df_income_groups.loc[self.income_group, "discount rate"])**results_df["time [yr]"]
		
		#calculate emissions
		results_df["emissions [tCO$_2$-eq.]"] = results_df["time [yr]"].diff() * self.annual_mileage * self.get_emissions_per_mile(veh_name)
		results_df.loc["pre-purchase", "emissions [tCO$_2$-eq.]"] = 0
		results_df.loc[0, "emissions [tCO$_2$-eq.]"] = self.df_vehicles.loc[veh_name, "production CO2 footprint [g]"] * 1e-6
		
		#cumulative costs/emissions
		for col in self.non_total_columns:
			results_df["total "+col] = results_df[col].cumsum()
		
		#round costs and emissions
		results_df = results_df.convert_dtypes()
		results_df[self.costs_columns] = results_df[self.costs_columns].replace(pd.NA, np.nan).round(0)
		results_df[self.emissions_columns] = results_df[self.emissions_columns].replace(pd.NA, np.nan).round(1)
		
		#write results_df into self.results[veh_name]
		self.results[veh_name] = results_df.copy()
		
		#save results
		self.results[veh_name].to_csv("results/"+self.results_fns[veh_name])
	
	def read_results(self, veh_name):
		self.results[veh_name] = pd.read_csv("results/"+self.results_fns[veh_name], index_col="period [yr]")
	
	def plot_results(self, y_quant):
		fig,ax = plt.subplots(figsize=(8,6))

		for veh_name in self.veh_names:
			x = self.results[veh_name]["time (for plotting) [yr]"]
			y = self.results[veh_name][y_quant]
			u.plot(x, y, frame=[fig,ax], kind="plot", label=self.df_vehicles.loc[veh_name, "label"], color=self.df_vehicles.loc[veh_name, "color"], lw=self.df_vehicles.loc[veh_name, "lw"], marker_option=self.df_vehicles.loc[veh_name, "marker_option"], zorder=self.df_vehicles.loc[veh_name, "zorder"], ls="-", alpha=1.)
		
		#figure setup
		textstr = "%s, %d"%(self.area, self.year)
		if "costs" in y_quant:
			textstr += "\ngas = {0:.2f} $/gal\nelectricity = {1:.1f} ct/kWh".format(self.df_areas.loc[self.area, "gas_price %d [$/gal]"%self.year], self.df_areas.loc[self.area, "electricity_price %d [ct/kWh]"%(self.year-1)])
		if y_quant in ["costs [$]", "total costs [$]", "present value costs [$]", "total present value costs [$]"]:
			ylabel = "Lifecycle costs [$]"
			ylim   = (0, max(85000, 1.05*ax.get_ylim()[1]))
			ylim   = (0.8*min([self.df_vehicles.loc[veh_name, "average transaction price [$]"] for veh_name in self.veh_names]), max(85000, 1.05*ax.get_ylim()[1]))
			# ylim   = (40000,75000)
		elif "emissions" in y_quant:
			ylabel = "Lifecycle emissions [tCO$_2$-eq.]"
			ylim   = (0, max(51, 1.02*ax.get_ylim()[1]))
			# ylim   = (0,54)
			textstr += "\nelectricity emission intensity = {0:.0f} g/kWh".format(self.df_areas.loc[self.area, "electricity_emission_intensity 2021 [g/kWh]"])
		else:
			ylabel = y_quant
			ylim = None #ax.get_ylim()
		
		ylabel = y_quant

		props = dict(boxstyle="round", facecolor="white", alpha=0.8)
		ax.text(0.97, 0.04, textstr, transform=ax.transAxes, fontsize=14,
				verticalalignment="bottom", ha="right", bbox=props)

		xlim = ax.get_xlim()
		ax.axvspan(xlim[0], 0, alpha=0.2, color="red")
		# ax.axvspan(self.lifetime_mileage, xlim[1], alpha=0.2, color="cyan")
		ax.axvspan(self.lifetime, xlim[1], alpha=0.2, color="cyan")
		u.fig_ax_setup(	fig, title=y_quant, 
						ylabel=ylabel, 
						xlim=xlim, ylim=ylim, 
						xticks=self.lifetime_range, 
						legend_position="upper left", 
						x_axis_formatting=True, y_axis_formatting=True
					)
		if False: #len(self.veh_names)==4:
			#specify order of items in legend
			handles, labels = plt.gca().get_legend_handles_labels()
			order = [2,3,0,1]
			ax.legend([handles[idx] for idx in order],[labels[idx] for idx in order], loc="upper left")
		if xaxis == "years":
			ax.set_xlabel("Years")
			# ax.set_xticks(self.lifetime_range)
		elif xaxis == "miles":
			secax = ax.secondary_xaxis(0, functions=(self.yr2mi, self.mi2yr))
			new_secxticks = range(0,int(np.ceil(self.yr2mi(self.lifetime))),25000)
			secax.set_xticks(new_secxticks)
			axis_formatter = matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
			secax.xaxis.set_major_formatter(axis_formatter)
			secax.grid(True, which="both", axis="both") #TODO
			ax.set_xlabel("Mileage [mi]")
			for tick in ax.xaxis.get_major_ticks():
				tick.set_visible(False)
		elif xaxis == "both":
			ax.set_xlabel("Years")
			secax = ax.secondary_xaxis(-0.16, functions=(self.yr2mi, self.mi2yr))
			new_secxticks = range(0,int(np.ceil(self.yr2mi(self.lifetime))),25000)
			secax.set_xticks(new_secxticks)
			axis_formatter = matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
			secax.xaxis.set_major_formatter(axis_formatter)
			secax.set_xlabel("Mileage [mi]")
			# secax.grid(1) #doesn't work
		xticks_old = ax.get_xticks()
		xticks = ax.xaxis.get_major_ticks()
		for i,x in enumerate(xticks_old):
			# if x < 0 or x > self.lifetime_mileage:
			if x < 0 or x >= self.lifetime:
				xticks[i].set_visible(False)
		
		filename = "plot.png"
		# u.save_figure(fig, "plots/"+filename, dpi=200)
	
	def get_results(self, veh_name, show_non_total_columns=True, show_time_columns=False):
		excl_cols = pd.Series(False, index=self.results[veh_name].columns) if show_time_columns else self.results[veh_name].columns.isin(["time [yr]", "time (for plotting) [yr]"]) #hack
		if show_non_total_columns:
			return self.results[veh_name].loc[:, ~excl_cols]
		else:
			return self.results[veh_name].loc[:, ~excl_cols][self.total_columns]
