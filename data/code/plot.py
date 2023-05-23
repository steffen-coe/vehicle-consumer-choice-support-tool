# -*- coding: utf-8 -*-
"""
Created on Thu May 12 14:22:51 2022

@author: steff
"""

import utils as u
import matplotlib.pyplot as plt
# import pandas as pd
import numpy as np

import init
init.run()

def lca(l, scenario="current mixes"): #instead pass one number for prod, then a list of numbers (or pd df) with use phase numbers for each year, then one number for end-of-use phase
    prod, w2t, t2w, rec = l
    if scenario == "scenario (sold today)":
        x = [-0.1*lifetime_mileage, *range(0, lifetime_mileage, annual_mileage), lifetime_mileage, 1.1*lifetime_mileage]
        y = [0]
        y += [prod*lifetime_mileage] #production-phase emissions
        for year in range(int(np.floor(lifetime))):
            y += [(w2t+t2w) * (1-year/30) * annual_mileage] #use-phase emissions
        y += [(w2t+t2w) * (1-lifetime/30) * annual_mileage] #emissions for last year of use
        y += [rec*lifetime_mileage] #recycling-phase emissions
    elif scenario == "scenario (sold in 10 years)":
        x = [-0.1*lifetime_mileage, *range(0, lifetime_mileage, annual_mileage), lifetime_mileage, 1.1*lifetime_mileage]
        y = [0]
        y += [prod*(1-0.4325*0.333)*lifetime_mileage] #production-phase emissions
        for year in range(int(np.floor(lifetime))):
            y += [(w2t+t2w) * (1-(10+year)/30) * annual_mileage] #use-phase emissions
        y += [(w2t+t2w) * (1-(10+lifetime)/30) * annual_mileage] #emissions for last year of use
        y += [rec*lifetime_mileage] #recycling-phase emissions
    elif scenario == "current mixes":
        x = [-0.1*lifetime_mileage, 0, lifetime_mileage, 1.1*lifetime_mileage]
        y = [0]
        y += [prod*lifetime_mileage] #production-phase emissions
        y += [(w2t+t2w)*lifetime_mileage] #use-phase emissions
        y += [rec*lifetime_mileage] #recycling-phase emissions
    y = np.cumsum(y) * 1e-6 #* 1.1023
    return x,y

# df = pd.read_excel("data.xlsx", sheet_name="gCO2-eq. per km")
# df_key = pd.read_excel("data.xslx", sheet_name="key", index_col="column")

#g-CO2-eq./km for production, use (includes well-to-tank and tank-to-wheel), and recycling phases
data = {
        "Diesel" : [[29, 11, 100, 0], "black"], 
        "EV (China mix)": [[57, 126, 0, 0], "#f52c7c"], 
        "EV (EU-28 mix)": [[57, 62, 0, 0], "#001489"], 
        "EV (German mix)": [[57, 87, 0, 0], "#e8561c"], 
        "EV (US mix)": [[57, 85, 0, 0], "#2c97f5"], 
        "EV (100% wind power)" : [[57, 2, 0, 0], "#04b50c"], 
        }

lifetime_mileage = 200000 #in km
annual_mileage = 11300 #in km/year
lifetime = lifetime_mileage/annual_mileage #in years

print(lifetime)

fig,ax = plt.subplots(figsize=(8,6))

for mix in data.keys():
    print("")
    print(mix)
    d = data[mix]
    x,y = lca(d[0])
    u.print_table(x,y)
    u.plot(x, y, frame=[fig,ax], kind="plot", color=d[1], label=mix, lw=3, marker_option="o", alpha=1.)

# x,y = lca(data["EV (EU-28 mix)"][0], scenario="scenario (sold today)")
# u.print_table(x,y)
# u.plot(x, y, frame=[fig,ax], kind="plot", color="#2e40a6", label="EV (EU-28 mix, scenario: sold today)", lw=3, marker_option="o", alpha=1.)

# x,y = lca(data["EV (EU-28 mix)"][0], scenario="scenario (sold in 10 years)")
# u.print_table(x,y)
# u.plot(x, y, frame=[fig,ax], kind="plot", color="#5664b8", label="EV (EU-28 mix, scenario: sold in 10 years)", lw=3, marker_option="o", alpha=1.)

xlims = ax.get_xlim()
ax.axvspan(-50000, 0, alpha=0.2, color="red")
#ax.axvspan(0, lifetime_mileage, alpha=0.2, color="grey")
ax.axvspan(lifetime_mileage, lifetime_mileage+50000, alpha=0.2, color="cyan")
ax.set_xlim(xlims)
ax.set_ylim(-1, 41)

u.fig_ax_setup(fig, xlabel="Mileage (in km)", 
               ylabel="Lifecycle emissions (in tCO$_2$-eq.)", 
               legend_position="upper left", 
               x_axis_formatting=True, )


