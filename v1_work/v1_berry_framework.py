"""
Vector 1 Berry Framework
========================
Computes Berry connection A_i, curvature F_ij, and Chern numbers from a
wavefunction Ψ(θ) given on a discrete grid in parameter space.

Implements the Fukui-Hatsugai-Suzuki (FHS) discrete Berry phase algorithm,
which is gauge-invariant by construction and standard for numerical
topological-invariant computation in lattice systems.

Reference: Fukui, Hatsugai, Suzuki, J. Phys. Soc. Jpn. 74, 1674 (2005).

Usage:
    1. Provide psi[i,j,...] = complex wavefunction array on parameter grid
    2. Call berry_curvature(psi) to get F[i,j] on each plaquette
    3. Call chern_number(F) to integrate over closed surface

Convention: parameter space is θ_1, θ_2 (axes 0 and 1 of psi array).
Internal Hilbert dimension is the LAST axis of psi.
"""
import numpy as np

# ---------------------------------------------------------------------------
# Core Berry framework (gauge-invariant, FHS discretization)
# ---------------------------------------------------------------------------

def link_variable(psi_a, psi_b):
    """
    U(1) link variable U_ab = <psi_a|psi_b> / |<psi_a|psi_b>|.
    Gauge-invariant phase between two wavefunctions.
    psi_a, psi_b: complex arrays, last axis = Hilbert dim.
    """
    inner = np.sum(np.conj(psi_a) * psi_b, axis=-1)
    norm = np.abs(inner)
    # Avoid divide-by-zero at degeneracies (where wavefunctions become orthogonal)
    norm = np.where(norm < 1e-14, 1e-14, norm)
    return inner / norm


def berry_curvature(psi):
    """
    Compute Berry curvature F[i,j] on each plaquette of the (θ_1, θ_2) grid.
    
    psi: shape (N1, N2, dim) — complex wavefunction on N1×N2 grid
    returns: F shape (N1-1, N2-1) — real plaquette flux in (-π, π]
    
    Plaquette: corners at (i,j), (i+1,j), (i+1,j+1), (i,j+1).
    Wilson loop: U1 * U2 * U3^-1 * U4^-1 where Uk are link variables.
    F = -Im log(W). This is the gauge-invariant flux through the plaquette.
    """
    # Link variables along axis 0 (θ_1 direction): U1[i,j] = <psi[i,j]|psi[i+1,j]>
    U1 = link_variable(psi[:-1, :, :], psi[1:, :, :])
    # Link along axis 1: U2[i,j] = <psi[i,j]|psi[i,j+1]>
    U2 = link_variable(psi[:, :-1, :], psi[:, 1:, :])
    # Wilson loop around plaquette (i,j) -> (i+1,j) -> (i+1,j+1) -> (i,j+1) -> (i,j)
    W = U1[:, :-1] * U2[1:, :] * np.conj(U1[:, 1:]) * np.conj(U2[:-1, :])
    F = np.angle(W)  # in (-π, π]; FHS convention: +arg of plaquette Wilson loop
    return F


def chern_number(F):
    """
    Sum F over the surface to get total Chern number.
    For a CLOSED surface (e.g., sphere): C = (1/2π) ∮ F.
    For an open patch: returns total flux (not necessarily integer).
    
    F: shape (N1-1, N2-1)
    returns: real scalar
    """
    return float(np.sum(F)) / (2 * np.pi)


def find_monopoles(F, threshold_fraction=0.5):
    """
    Locate plaquettes carrying near-monopole flux (large |F|).
    Heuristic: plaquettes where |F| exceeds threshold_fraction × |F|_max.
    
    For a smooth field with isolated singularities, the monopole shows up
    as a plaquette with flux ≈ 2π × (Chern number around it).
    
    F: shape (N1-1, N2-1)
    returns: list of (i, j, F_value) tuples
    """
    if F.size == 0:
        return []
    F_max = np.max(np.abs(F))
    if F_max < 1e-10:
        return []
    threshold = threshold_fraction * F_max
    indices = np.argwhere(np.abs(F) >= threshold)
    return [(int(i), int(j), float(F[i, j])) for i, j in indices]


# ---------------------------------------------------------------------------
# Validation: 2-level system on the Bloch sphere
# ---------------------------------------------------------------------------
# Canonical Berry monopole: H(R) = R · σ, ground state |ψ_-(R)>.
# Berry curvature on R-sphere: F = -1/(2 R²) (radial monopole field).
# Chern number around the origin: C = -1 (ground state).
# Reference: Berry 1984; standard textbook example (e.g. Xiao-Chang-Niu).
# ---------------------------------------------------------------------------

def two_level_ground_state(theta, phi):
    """
    Ground state of H = sin θ cos φ σ_x + sin θ sin φ σ_y + cos θ σ_z.
    
    Lower-energy eigenstate at point (θ, φ) on the Bloch sphere:
        |ψ_-> = ( sin(θ/2)            )
                ( -e^{iφ} cos(θ/2)    )
    
    This gauge has a Dirac string at θ = 0 (north pole). FHS link variables
    are gauge-invariant on the bulk; the singularity contributes to Chern
    counting via the wrapped flux.
    
    theta, phi: arrays of same shape, broadcasting compatible
    returns: complex array, last axis = 2 (Hilbert dim)
    """
    theta = np.asarray(theta)
    phi = np.asarray(phi)
    psi = np.empty(theta.shape + (2,), dtype=complex)
    psi[..., 0] = np.sin(theta / 2)
    psi[..., 1] = -np.exp(1j * phi) * np.cos(theta / 2)
    return psi


def validate_two_level(N=80):
    """
    Build the ground state on the full Bloch sphere and verify Chern = -1.
    Grid: θ ∈ [ε, π-ε] × φ ∈ [0, 2π], identify φ=0 with φ=2π.
    
    With N×N grid, Chern integration should reach -1 to within ~0.01.
    """
    eps = 1e-3  # small offset from poles to avoid coordinate singularity
    theta_vals = np.linspace(eps, np.pi - eps, N)
    phi_vals = np.linspace(0, 2 * np.pi, N)  # endpoints identified
    THETA, PHI = np.meshgrid(theta_vals, phi_vals, indexing='ij')
    psi = two_level_ground_state(THETA, PHI)
    F = berry_curvature(psi)
    C = chern_number(F)
    return {
        'grid': (N, N),
        'F_min': float(np.min(F)),
        'F_max': float(np.max(F)),
        'F_total_flux': float(np.sum(F)),
        'chern_number': C,
        'expected_chern': -1.0,
        'error': abs(C - (-1.0)),
    }


# ---------------------------------------------------------------------------
# Sanity check on a torus: trivial wavefunction (no Berry phase)
# ---------------------------------------------------------------------------

def trivial_wavefunction(theta, phi):
    """Constant state |0> — Berry connection should vanish identically."""
    psi = np.zeros(theta.shape + (2,), dtype=complex)
    psi[..., 0] = 1.0
    return psi


def validate_trivial(N=50):
    """Trivial wavefunction → all plaquette fluxes ≈ 0."""
    theta_vals = np.linspace(0, 1, N)
    phi_vals = np.linspace(0, 1, N)
    THETA, PHI = np.meshgrid(theta_vals, phi_vals, indexing='ij')
    psi = trivial_wavefunction(THETA, PHI)
    F = berry_curvature(psi)
    return {
        'grid': (N, N),
        'F_max_abs': float(np.max(np.abs(F))),
        'F_total_flux': float(np.sum(F)),
        'chern_number': chern_number(F),
        'expected_chern': 0.0,
    }


# ---------------------------------------------------------------------------
# Main: run validations
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Vector 1 Berry Framework — validation suite")
    print("=" * 60)
    
    print("\n[1] Trivial wavefunction (expected Chern = 0):")
    r = validate_trivial(N=50)
    for k, v in r.items():
        print(f"    {k}: {v}")
    assert abs(r['chern_number']) < 1e-9, "Trivial wavefunction should give zero Chern"
    print("    ✓ PASS")
    
    print("\n[2] Two-level Bloch-sphere ground state (expected Chern = -1):")
    for N in [40, 80, 160]:
        r = validate_two_level(N=N)
        print(f"    N={N}: Chern = {r['chern_number']:.6f}, "
              f"error = {r['error']:.6f}")
    assert r['error'] < 0.01, f"Should converge to -1, got error {r['error']}"
    print("    ✓ PASS")
    
    print("\n" + "=" * 60)
    print("Framework validated. Ready for Bohr-Mottelson Ψ(β,γ).")
    print("=" * 60)
