from arc import Caesium
import numpy as np
import pandas as pd
from scipy.constants import c, h, e
import os

save_dir = r"C:\Users\Lukef\Code\Quantum_systems\ARC\Calculation_outputs"
os.makedirs(save_dir, exist_ok=True)

atom = Caesium()

# -----------------------------
# STATE SPACE
# -----------------------------
nmin, nmax = 6, 7
lmin, lmax = 0, 1

# Ground hyperfine state: 6S1/2
n0, l0, j0 = 6, 0, 0.5
I = 7/2

F0_vals = atom.getHFSCoupling(n0, l0, j0, I)
ground_energy = atom.getEnergy(n0, l0, j0)

transitions_data = []

# -----------------------------
# LOOP OVER EXCITED ELECTRONIC STATES
# -----------------------------
for n in range(nmin, nmax + 1):
    for l in range(lmin, lmax + 1):

        if abs(l - l0) != 1:
            continue

        for j in np.arange(l - 0.5, l + 1.5, 1):
            if j < 0:
                continue

            F_vals = atom.getHFSCoupling(n, l, j, I)

            for F0 in F0_vals:
                for F in F_vals:

                    mF0_vals = np.arange(-F0, F0 + 1, 1)
                    mF_vals = np.arange(-F, F + 1, 1)

                    for mF0 in mF0_vals:
                        for mF in mF_vals:

                            q = mF - mF0

                            if q not in [-1, 0, 1]:
                                continue

                            energy = atom.getEnergy(n, l, j)
                            delta_energy = abs(ground_energy - energy) * e
                            wavelength_nm = (h * c / delta_energy) * 1e9

                            try:
                                dme = atom.getDipoleMatrixElementHFS(
                                    n0, l0, j0, F0, mF0,
                                    n, l, j, F, mF,
                                    int(q)
                                )
                            except:
                                continue

                            transitions_data.append({
                                "n": n,
                                "l": l,
                                "j": j,
                                "F_initial": F0,
                                "mF_initial": mF0,
                                "F_final": F,
                                "mF_final": mF,
                                "q": int(q),
                                "Wavelength (nm)": wavelength_nm,
                                "TDM (a.u.)": dme
                            })

df = pd.DataFrame(transitions_data)

print(df)

csv_path = os.path.join(save_dir, "Cs_HFS_transitions.csv")
df.to_csv(csv_path, index=False)