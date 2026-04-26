from __future__ import division
import numpy as np
import pandas as pd
import scipy.integrate
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# =========================
# USER PARAMETERS
# =========================

csv_path = r"C:\Users\Lukef\Code\Quantum_systems\ARC\Calculation_outputs\Cs_BR.csv"

B_target = 6.0  # Gauss

OmegaPk = 3 * np.pi * 1.0e3  # Rabi frequency (rad/s)

tMax = 2e-3  # longer time to see oscillations
dt_steps = 3000

# detuning from resonance (Hz → convert to rad/s later)
detuning_kHz = 0  # 0 for resonant Rabi oscillations

# polarization vector [pi, sigma+, sigma-]
pol_vec = np.array([0.8, 0.2, 0.0])  # pure π drive

# =========================
# LOAD DATA
# =========================

df = pd.read_csv(csv_path)
B_vals = df["B (G)"].values

# =========================
# CLOCK TRANSITION
# =========================

def get_clock_frequency(B_target):
    idx = np.argmin(np.abs(B_vals - B_target))

    E3 = df["F=3, mF=0"].values[idx]
    E4 = df["F=4, mF=0"].values[idx]

    omega0 = E4 - E3
    print("B field (G):", B_vals[idx])
    print("Transition:", omega0)

    return omega0

omega_0 = get_clock_frequency(B_target)

# =========================
# DETUNING (FIXED)
# =========================

Delta = 2 * np.pi * detuning_kHz * 1e3  # rad/s

# drive frequency = resonance + detuning
omega_drive = omega_0 + Delta

# =========================
# POLARIZATION → EFFECTIVE COUPLING
# =========================

pol_vec = pol_vec / np.linalg.norm(pol_vec)

Omega_pi    = OmegaPk * pol_vec[0]
Omega_sig_p = OmegaPk * pol_vec[1]
Omega_sig_m = OmegaPk * pol_vec[2]

Omega_total = np.sqrt(
    np.abs(Omega_pi)**2 +
    np.abs(Omega_sig_p)**2 +
    np.abs(Omega_sig_m)**2
)

# =========================
# INITIAL STATE |g⟩
# =========================

rho0 = np.zeros((2,2), dtype=complex)
rho0[0,0] = 1.0
rho0_flat = rho0.flatten()

# =========================
# HAMILTONIAN EVOLUTION (OBE WITHOUT DECAY)
# =========================

def OpticalBloch(t, rho_vec):

    rho = rho_vec.reshape(2,2)

    drho = np.zeros((2,2), dtype=complex)

    # detuning term
    drho[0,1] = (1j * Delta) * rho[0,1] + 1j * Omega_total/2 * (rho[0,0] - rho[1,1])
    drho[1,0] = np.conj(drho[0,1])

    imag = np.imag(rho[0,1])

    drho[0,0] = -Omega_total * imag
    drho[1,1] = +Omega_total * imag

    return drho.flatten()

# =========================
# TIME EVOLUTION
# =========================

def evolve():

    r = scipy.integrate.complex_ode(OpticalBloch)
    r.set_initial_value(rho0_flat, 0.0)

    t_vals = []
    Pg_vals = []
    Pe_vals = []

    dt = tMax / dt_steps

    while r.successful() and r.t < tMax:

        out = r.integrate(r.t + dt)
        rho = out.reshape(2,2)

        t_vals.append(r.t)
        Pg_vals.append(np.real(rho[0,0]))
        Pe_vals.append(np.real(rho[1,1]))

    return np.array(t_vals), np.array(Pg_vals), np.array(Pe_vals)


Omega_R = Omega_total  # rad/s

t_pi = np.pi / Omega_R  # seconds

print("\n=========================")
print("Effective Rabi frequency:")
print("Omega_R (rad/s):", Omega_R)
print("Omega_R (kHz):", Omega_R / (2*np.pi*1e3))

print("\nPi pulse time:")
print("t_pi (us):", t_pi * 1e6)
print("=========================\n")

# =========================
# RUN
# =========================



t, Pg, Pe = evolve()

# =========================
# PLOT RABI OSCILLATIONS
# =========================

fig, ax = plt.subplots()

ax.set_xlim(0, np.max(t) * 1e3)
ax.set_ylim(0, 1.1)

ax.set_xlabel("Time (ms)")
ax.set_ylabel("Ground state population")
ax.set_title("Rabi Oscillation (live build-up)")

line, = ax.plot([], [], lw=2)


def init():
    line.set_data([], [])
    return line,


def update(i):
    # progressively reveal curve
    x = t[:i] * 1e3
    y = Pg[:i]

    line.set_data(x, y)
    return line,


ani = animation.FuncAnimation(
    fig,
    update,
    frames=len(t),
    init_func=init,
    interval=5,   # speed (ms between frames)
    blit=True
)

plt.show()



