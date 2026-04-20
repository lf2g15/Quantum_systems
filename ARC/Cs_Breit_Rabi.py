

from __future__ import division
import numpy
import matplotlib.pyplot as pyplot
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from scipy.optimize import curve_fit 


# Physical constants
muB = 9.27400968e-24  # J/T
h = 6.62607015e-34    # J*s

# Cs-133 parameters
I = 7/2
gJ = 2.0023193043622
gI = -0.00039885395

# Hyperfine splitting (Hz)
Delta_hfs = 9.192631770e9  # Hz (Cs clock transition)

# Convert to energy
Delta = h * Delta_hfs



Font_size = 12

###
#Data for calibration, 22/09/22 
# and 13/10/22
###

#%% Breit - Rabi 

def breit_rabi(B, mF, F):
    x = (gJ - gI) * muB * B / Delta

    if F == I + 1/2:  # F = 4
        return (-Delta/(2*(2*I+1))
                + gI*muB*mF*B
                + (Delta/2)*np.sqrt(1 + (4*mF/(2*I+1))*x + x**2))
    else:  # F = 3
        return (-Delta/(2*(2*I+1))
                + gI*muB*mF*B
                - (Delta/2)*np.sqrt(1 - (4*mF/(2*I+1))*x + x**2))

Bs = np.linspace(0, 10e-4, 2000)

levels = []
# Compute zero-field ground state energy (F=3, mF=0)
E0 = breit_rabi(0, 0, 3)

for B in Bs:
    energies = []

    # F = 4 manifold
    for mF in range(-4, 5):
        energies.append(breit_rabi(B, mF, 4) - E0)

    # F = 3 manifold
    for mF in range(-3, 4):
        energies.append(breit_rabi(B, mF, 3) - E0)

    levels.append(energies)

levels = np.array(levels)

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, dpi=300, figsize=(6,4))
fig.subplots_adjust(hspace=0.1)

# Plot upper manifold (F=4)
for i in range(9):
    if i == 4:  # F=4, mF=0
        ax1.plot(Bs*1e4, levels[:, i]/h/1e9, color='black', lw=1.5)
    else:
        ax1.plot(Bs*1e4, levels[:, i]/h/1e9, color='gold', alpha=0.6)

# Plot lower manifold (F=3)
for i in range(9, 16):
    if i == 12:  # F=3, mF=0
        ax2.plot(Bs*1e4, levels[:, i]/h/1e9, color='black', lw=1.5)
    else:
        ax2.plot(Bs*1e4, levels[:, i]/h/1e9, color='gold', alpha=0.6)

# Labels
ax2.set_xlabel('Magnetic field (G)')
ax2.set_ylabel('Energy (GHz)')
ax1.set_ylabel('Energy (GHz)')
v_range = 0.015
# Set limits to create the "gap"
E1 = levels[0, 0]/h/1e9
ax2.set_ylim(-v_range, v_range)        # around 0 GHz (F=3)
ax1.set_ylim(E1-v_range, E1+v_range)         # around 9.2 GHz (F=4)

ax1.set_xlim(min(Bs)*1e4, max(Bs)*1e4)

# Hide spines between plots
ax1.spines.bottom.set_visible(False)
ax2.spines.top.set_visible(False)

ax1.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
ax2.xaxis.tick_bottom()

# Diagonal break marks
d = 0.5
kwargs = dict(marker=[(-1, -d), (1, d)],
              markersize=10,
              linestyle="none",
              color='k',
              mec='k',
              mew=1,
              clip_on=False)

ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)
ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)

# ax1.text(10, 9.6, 'F = 4', fontsize=10)
# ax2.text(10, 0.3, 'F = 3', fontsize=10)

plt.show()




states = []
# F = 4
for mF in range(-4, 5):
    states.append((4, mF))
# F = 3
for mF in range(-3, 4):
    states.append((3, mF))
levels = np.array(levels)
import pandas as pd
import os

# Convert B to Gauss (to match your plot)
B_gauss = Bs * 1e4

# Create dictionary for DataFrame
data = {'B (G)': B_gauss}

# Add each state as a column
for i, (F, mF) in enumerate(states):
    col_name = f"F={F}, mF={mF}"
    data[col_name] = levels[:, i] / h / 1e9  # GHz

df = pd.DataFrame(data)
save_dir = "."  # or your desired folder
csv_path = os.path.join(save_dir, "Cs_BR.csv")

df.to_csv(csv_path, index=False)