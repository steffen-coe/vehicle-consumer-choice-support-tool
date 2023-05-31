#settings
veh_types = []
veh_types += ["Typical"]
veh_types += ["Typical Car"]
veh_types += ["Sedan"]
veh_types += ["Car SUV"]
veh_types += ["Typical Truck"]
veh_types += ["Truck SUV"]
veh_types += ["Minivan/Van"]
veh_types += ["Pickup"]
veh_names_pairs = [[veh_type+" ICEV", veh_type+" BEV"] for veh_type in veh_types]
veh_names_pairs += [["Toyota Corolla ICEV", "Chevrolet Bolt BEV"]]
veh_names_pairs

veh_types_colors = {
						"Typical": "#6929c4", 
						"Typical Car": "#1192e8", 
						"Sedan": "#005d5d", 
						"Car SUV": "#9f1853", 
						"Typical Truck": "#fa4d56", 
						"Truck SUV": "#570408", 
						"Minivan/Van": "#198038", 
						"Pickup": "#002d9c", 
						"affordable sedan": "#ee538b", 
} #source: https://carbondesignsystem.com/data-visualization/color-palettes/

areas = [
			# "DCFC", 
			"U.S.", 
			"WA", 
			# "TX", 
			# "CA", 
			# "NY", 
			# "MN", 
			"WV", 
	]

years = [
# 			2020, #doesn't work right now because electricity price 2019 is not available
			# 2021, 
			2022, 
	]

income_groups = [
		"less than $25k", 
		"$25-50k", 
		"$50-75k", 
		"$75-100k", 
		"$100-200k", 
		"more than $200k"
	]

#for waterfall plots
plot_types_dict = {
					"Waterfall plot for **one** vehicle type, showing **either** nominal or present value cost differences.": "one_either", 
					"Waterfall plot for **one** vehicle type, showing **both** nominal and present value cost differences.": "one_both", 
					"Waterfall plot for **all** vehicle types, showing **either** nominal or present value cost differences.": "all_either", 
	}
cost_types = ["purchase", "incentives", "operations", "insurance", "maintenance"]
ticktext = ["purchase 🚘", "incentives 💸", "operations ⛽", "insurance 📋", "maintenance 🛠", "total ⚖️"] #💨🛣⛽🔌
cost_types_future = [cost_type for cost_type in cost_types if cost_type!="purchase"]
fsize = 16
ffactor = 1.4

# xaxis = "years"
# xaxis = "miles"
xaxis = "both"

numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']

# annual_mileage = 13476 #mi/year
# annual_mileage = 11576 #mi/year
p_DCFC = 0.10 #share of fast-charging for BEV
eff_charging = 0.95 #charging efficiency

R = 0.025 #discount rate

rec_CO2 = 0 #recycling-phase emissions
rec_price = 0 #recycling-phase price


#consumer behavior
valuation_ratio = 0.5
