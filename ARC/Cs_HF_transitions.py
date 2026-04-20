from sympy.physics.quantum.cg import CG
from sympy.physics.wigner import wigner_6j
from sympy import sqrt, S, N

# Cs-133 constants
I = S(7)/2
J = S(1)/2

def hyperfine_dipole_strength(F, mF, Fp, mFp, q):
    # Clebsch-Gordan part
    cg = CG(F, mF, 1, q, Fp, mFp).doit()

    # 6-j symbol (hyperfine structure factor)
    sixj = wigner_6j(J, F, I, Fp, J, 1)

    # prefactor
    prefactor = (-1)**(Fp + J + I + 1) * sqrt((2*Fp + 1)*(2*F + 1))

    amp = prefactor * sixj * cg

    return amp.simplify()

# Example: |F=3,mF=0> -> |F'=4,mF'=0>, pi transition
strength = hyperfine_dipole_strength(3, 0, 4, 0, 0)

print("Symbolic:", strength)
print("Numeric :", N(strength))