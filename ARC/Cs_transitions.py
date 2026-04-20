from arc import *
import numpy as np
import pandas as pd
from scipy.constants import c, h, e
import os

save_dir = r"C:\Users\Lukef\Code\Quantum_systems\ARC\Calculation_outputs"
os.makedirs(save_dir, exist_ok=True)


atom = Caesium()

nmin, nmax = 6, 7
lmin, lmax = 0, 1



# Ground state
n0, l0, j0 = 6, 0, 0.5
ground_energy = atom.getEnergy(n0, l0, j0)

transitions_data = []

# Loop over all states
for n in range(nmin, nmax + 1):
    for l in range(lmin, lmax + 1):

        # Enforce dipole rule early
        if abs(l - l0) != 1:
            continue

        for j in np.arange(l - 0.5, l + 1.5, 1):
            if j < 0:
                continue

            # mj values
            mj0_vals = np.arange(-j0, j0 + 1, 1)
            mj_vals = np.arange(-j, j + 1, 1)

            for mj0 in mj0_vals:
                for mj in mj_vals:

                    q = mj - mj0

                    # Only allowed polarizations
                    if q not in [-1, 0, 1]:
                        continue

                    energy = atom.getEnergy(n, l, j)

                    delta_energy = abs(ground_energy - energy) * e
                    wavelength_nm = (h * c / delta_energy) * 1e9

                    try:
                        dme = atom.getDipoleMatrixElement(
                            n0, l0, j0, mj0,
                            n, l, j, mj,
                            int(q)
                        )
                    except:
                        continue

                    transitions_data.append({
                        "n": n,
                        "l": l,
                        "j": j,
                        "mj_initial": mj0,
                        "mj_final": mj,
                        "q": int(q),
                        "Wavelength (nm)": wavelength_nm,
                        "TDM (a0 e)": dme
                    })

df = pd.DataFrame(transitions_data)
print(df)

csv_path = os.path.join(save_dir, "Cs_transitions.csv")
df.to_csv(csv_path, index=False)
