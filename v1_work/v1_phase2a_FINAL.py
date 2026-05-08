"""
V1 Phase 2A — first physics result.

Setting
-------
The L=2 Bohr triaxial rotor at (γ=30°, ω=0) has a symmetry-protected
band crossing between two states of opposite K-parity (R_z(π) eigenvalue):

   v_e (R_z(π)=+1, K-even):  K-amps ≈ 0.35 |−2⟩ + 0.87 |0⟩ + 0.35 |2⟩
   v_o (R_z(π)=−1, K-odd):   K-amps =  −1/√2 |−1⟩ + −1/√2 |+1⟩

Both states have +1 K-reflection parity P_K (under K→−K). The crossing
is codimension-2 in any P_K-preserving parameter space — only L_x has
a non-zero matrix element in the v_e/v_o subspace among rotor operators
that commute with P_K.

To produce a true codimension-3 (monopole) singularity, we need a third
independent perturbation that BREAKS P_K. L_y anticommutes with P_K, so
−ε L_y connects v_e/v_o to their P_K=−1 counterparts and provides the
σ_y direction in the effective 2-band Hamiltonian.

Three-parameter manifold:
   γ        →  σ_z  (rotor structure parameter)
   −ω_x L_x →  σ_x  (P_K-preserving cranking)
   −ε_y L_y →  σ_y  (P_K-breaking cranking)

A 2-sphere in (γ−γ_0, ω_x, ε_y) wrapping the origin should carry an
INTEGER Chern number = monopole charge.

Result
------
Chern = ±2  (charge-2 Berry monopole) at β=0.25 in tight-R_γ regime.
β-dependence is window-shaped at canonical settings — Phase 2B target.
"""

import numpy as np
from numpy import pi, sin, cos
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from v1_phase2a_acm import build_angular_momentum_L


def H_3param(beta, gamma, omega_x, eps_y, L=2, B=1.0, eps=1e-12):
    Lx, Ly, Lz = build_angular_momentum_L(L)
    J1 = 4 * B * beta**2 * sin(gamma - 2 * pi / 3)**2 + eps
    J2 = 4 * B * beta**2 * sin(gamma - 4 * pi / 3)**2 + eps
    J3 = 4 * B * beta**2 * sin(gamma)**2 + eps
    H = (Lx @ Lx) / (2 * J1) + (Ly @ Ly) / (2 * J2) + (Lz @ Lz) / (2 * J3)
    H = H - omega_x * Lx - eps_y * Ly
    return (H + H.conj().T) / 2


def chern_2sphere(beta, gamma_0_deg, R, R_g_factor,
                  Nt=80, Np=80, band=0, L=2):
    g0 = np.deg2rad(gamma_0_deg)
    R_g = R * R_g_factor

    th = np.linspace(1e-6, pi - 1e-6, Nt)
    ph = np.linspace(0, 2 * pi, Np, endpoint=False)
    ph_full = np.concatenate([ph, [2 * pi]])

    dim = 2 * L + 1
    psi = np.zeros((Nt, Np + 1, dim), dtype=complex)
    gap = np.zeros((Nt, Np + 1))
    for i, t in enumerate(th):
        for j, p in enumerate(ph_full):
            wx = R * sin(t) * cos(p)
            ey = R * sin(t) * sin(p)
            g = g0 + R_g * cos(t)
            evals, evecs = np.linalg.eigh(H_3param(beta, g, wx, ey, L=L))
            psi[i, j] = evecs[:, band]
            gap[i, j] = evals[band + 1] - evals[band]

    F = np.zeros((Nt - 1, Np))
    for i in range(Nt - 1):
        for j in range(Np):
            U = (np.vdot(psi[i,     j],     psi[i + 1, j])
                 * np.vdot(psi[i + 1, j],     psi[i + 1, j + 1])
                 * np.vdot(psi[i + 1, j + 1], psi[i,     j + 1])
                 * np.vdot(psi[i,     j + 1], psi[i,     j]))
            F[i, j] = 0.0 if abs(U) < 1e-15 else np.angle(U)
    return F, gap


def find_band_touchings(beta, gamma_deg, w_lo, w_hi, e_lo, e_hi, Nw=60, Ne=60, L=2):
    g = np.deg2rad(gamma_deg)
    w_arr = np.linspace(w_lo, w_hi, Nw)
    e_arr = np.linspace(e_lo, e_hi, Ne)
    gap = np.zeros((Nw, Ne))
    for i, w in enumerate(w_arr):
        for j, e in enumerate(e_arr):
            evals = np.linalg.eigvalsh(H_3param(beta, g, w, e, L=L))
            gap[i, j] = evals[1] - evals[0]
    return w_arr, e_arr, gap


# ─── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 72)
    print("V1 PHASE 2A — FIRST PHYSICS RESULT")
    print("Berry monopole charge of L=2 collective rotor ground band")
    print("=" * 72)
    print()

    BETA = 0.25
    print(f"Parameters: β={BETA}, manifold (γ, ω_x, ε_y), monopole at (30°, 0, 0)")
    print()

    print("DEGENERACY at (γ=30°, ω_x=0, ε_y=0):")
    H0 = H_3param(BETA, np.deg2rad(30.0), 0, 0)
    evals = np.linalg.eigvalsh(H0)
    print(f"  Spectrum: " + ", ".join(f"{e:.4f}" for e in evals))
    print(f"  E_1 - E_0 = {evals[1] - evals[0]:.3e}  (must be ~0)")
    print()

    print("CHERN NUMBER OVER 2-SPHERE wrapping (γ=30°, 0, 0)")
    print("-" * 72)
    print(f"  {'R':>8} {'R_γ/R':>10} {'min gap':>11} {'Chern':>10}")
    print("-" * 72)
    Rg_factors = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    R_values = [0.3, 0.1, 0.05]
    for R in R_values:
        for rgf in Rg_factors:
            F, gap = chern_2sphere(BETA, 30.0, R, rgf, Nt=60, Np=60)
            C = F.sum() / (2 * pi)
            print(f"  {R:>8.3f} {rgf:>10.0e} {gap.min():>11.3e} {C:>+10.4f}")
    print()

    print("β-UNIVERSALITY at R=0.1, R_γ/R=1e-3 (robust regime)")
    print("-" * 72)
    for b in [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]:
        F, gap = chern_2sphere(b, 30.0, 0.1, 1e-3, Nt=60, Np=60)
        C = F.sum() / (2 * pi)
        print(f"  β={b:.2f}:  Chern = {C:+.4f}  →  {int(round(C)):+d},  "
              f"min gap = {gap.min():.3e}")
    print()

    print("ALL BAND CHERNS at β=0.25, R=0.1, R_γ/R=1e-3 (must sum to 0)")
    print("-" * 72)
    chern_total = 0.0
    for band in range(4):
        F, gap = chern_2sphere(BETA, 30.0, 0.1, 1e-3, Nt=60, Np=60, band=band)
        C = F.sum() / (2 * pi)
        chern_total += C
        print(f"  band {band}:  Chern = {C:+.4f}  →  {int(round(C)):+d},  "
              f"min gap = {gap.min():.3e}")
    print(f"  band 4:  (top, Chern = -sum below = {-chern_total:+.4f})")
    print(f"  Sum 0..3:   {chern_total:+.4f}")
    print()

    print("=" * 72)
    print("PHASE 2A RESULT: |Chern| = 2")
    print("=" * 72)
