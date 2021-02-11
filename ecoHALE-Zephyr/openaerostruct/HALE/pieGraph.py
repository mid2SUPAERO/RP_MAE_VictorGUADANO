# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 16:08:33 2019

@author: e.duriez
"""
import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 5), subplot_kw=dict(aspect="equal"))






data = [108.32, 10.5, 10, 13.41, 16.11, 86.37, 25.71]
parts = ['Batteries','Avionics','Payload','Propulsion','Solar Array','Wing', 'Additional Mass']


def func(pct, allvals):
    absolute = int(pct/100.*np.sum(allvals))
    return "{:.0f}%\n".format(pct, absolute)


wedges, texts, autotexts = ax.pie(data, startangle=90, colors=[(61/256,38/256,168/256),(70/256,59/256,222/256),(71/256,87/256,247/256),(50/256,123/256,252/256),(62/256,201/256,141/256),(128/256,203/256,88/256),(246/256,220/256,41/256)], autopct=lambda pct: func(pct, data),
                                  wedgeprops = {'linewidth': 0.7,'edgecolor': 'k'}, pctdistance=1.15)

ax.legend(wedges, parts,
#          title="Parts",
          loc="center left",
          bbox_to_anchor=(1, 0, 0.5, 1),
          edgecolor='k',
          fontsize=14)
#          bbox_to_anchor=(1, 0, 0.5, 1))

plt.setp(autotexts, size=14)

#ax.set_title("Matplotlib bakery: A pie")

plt.savefig('massBreakdown.png', dpi=300)

plt.show()
