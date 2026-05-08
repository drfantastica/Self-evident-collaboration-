"""
V1 Phase 2A — Berry curvature on (β, γ) shape space for the L=2 collective rotor.
First physics result for the SIS-Fold formalism.

Setup
-----
Rigid triaxial rotor at fixed angular momentum L (default 2).
Body-frame Hamiltonian:
    H_rot(β,γ) = Σ_k L_k² / (2 J_k(β,γ))
with Bohr-Mottelson moments of inertia
    J_k(β,γ) = 4Bβ² sin²(γ - 2πk/3),  k=1,2,3.

(β, γ) are treated as classical parameters (slow collective coordinates);
the Hilbert space at each point is the (2L+1)-dim K-basis of body-frame
angular-momentum projection. The ground state |Ψ_0(β,γ)⟩ in K-basis is
the eigenvector of H_rot at each (β,γ).

The SIS connection on shape space is
    A_i^SIS(β,γ) = i⟨Ψ_0|∂_i|Ψ_0⟩,
its curvature
    F_ij^SIS = ∂_i A_j - ∂_j A_i,
and its first Chern number
    C₁ = (1/2π) ∫ F_ij dβ ∧ dγ
should be integer-quantized whenever no degeneracy is crossed in the
interior of the integration region.

Reused from Phase 1 (validated):
    • build_angular_momentum_L  — body-frame ang-mom operators in K-basis
    • fhs_berry_curvature        — gauge-invariant Wilson-loop curvature
    • chern_number_total         — sum F over plaquettes / 2π
    • find_monopoles             — locate flux concentrations
"""

import numpy as np
from numpy import pi, sin
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ─── Phase 1 framework (re-used; validated on Chern = 0, -1, -2, -3, -5, -7) ───

def build_angular_momentum_L(L):
    """Body-frame angular-momentum operators L_x, L_y, L_z in |L,K⟩ basis.
    K = -L, -L+1, ..., +L.  L_+ |L,K⟩ = √(L(L+1) - K(K+1)) |L,K+1⟩.
    """
    dim = 2 * L + 1
    K_vals = np.arange(-L, L + 1)
    Lz = np.diag(K_vals.astype(complex))
    Lp = np.zeros((dim, dim), dtype=complex)
    for i, K in enumerate(K_vals):
        if K + 1 <= L:
            Lp[i + 1, i] = np.sqrt(L * (L + 1) - K * (K + 1))
    Lm = Lp.conj().T
    Lx = (Lp + Lm) / 2
    Ly = (Lp - Lm) / (2j)
    return Lx, Ly, Lz


def fhs_berry_curvature(psi_grid):
    """Gauge-invariant FHS Wilson-loop Berry curvature on a 2D grid.

    psi_grid : (N1, N2, dim_H) complex.  Ground-state wavefunctions per cell.
    Returns F : (N1-1, N2-1) real.  Plaquette curvature in radians.
    """
    N1, N2, _ = psi_grid.shape
    F = np.zeros((N1 - 1, N2 - 1))
    for i in range(N1 - 1):
        for j in range(N2 - 1):
            u1 = np.vdot(psi_grid[i,     j],     psi_grid[i + 1, j])
            u2 = np.vdot(psi_grid[i + 1, j],     psi_grid[i + 1, j + 1])
            u3 = np.vdot(psi_grid[i + 1, j + 1], psi_grid[i,     j + 1])
            u4 = np.vdot(psi_grid[i,     j + 1], psi_grid[i,     j])
            U = u1 * u2 * u3 * u4
            F[i, j] = 0.0 if abs(U) < 1e-15 else np.angle(U)
    return F


def chern_number_total(F):
    return F.sum() / (2 * pi)


def find_monopoles(F, sigma=4.0):
    """Plaquettes whose |F| exceeds sigma · std(F)."""
    threshold = sigma * F.std()
    return np.argwhere(np.abs(F) > threshold)


# ─── Phase 2A: physical Hamiltonian ──────────────────────────────────────────

def rotor_H(beta, gamma, omega=0.0, n_axis=(1.0, 1.0, 1.0),
            L=2, B=1.0, eps=1e-10):
    """Bohr triaxial rotor with tilted-axis cranking."""
    Lx, Ly, Lz = build_angular_momentum_L(L)
    n = np.asarray(n_axis, dtype=float)
    n = n / np.linalg.norm(n)
    L_dot_n = n[0] * Lx + n[1] * Ly + n[2] * Lz

    J1 = 4 * B * beta**2 * sin(gamma - 2 * pi / 3)**2 + eps
    J2 = 4 * B * beta**2 * sin(gamma - 4 * pi / 3)**2 + eps
    J3 = 4 * B * beta**2 * sin(gamma)**2 + eps
    H = (Lx @ Lx) / (2 * J1) + (Ly @ Ly) / (2 * J2) + (Lz @ Lz) / (2 * J3)
    if omega != 0.0:
        H = H - omega * L_dot_n
    return (H + H.conj().T) / 2
