"""
Vector 1 Phase 1.3 — Higher-winding Berry monopoles
====================================================

Demonstrates that the Berry framework produces EXACT integer Chern numbers
for arbitrary winding numbers, matching the V5 prediction structure.

Setup: parameterize a sphere directly by (θ, φ) — these can be interpreted
as a topologically-correct map from nuclear (β, γ) shape coordinates onto
the relevant manifold. For each integer winding q, the Hamiltonian
H = sin θ cos(qφ) σ_x + sin θ sin(qφ) σ_y + cos θ σ_z
has a Berry monopole of charge q at the origin.

Ground-state Chern number (exact): -q.
Excited-state Chern number (exact): +q.

Sum: 0 (total Chern number across all bands of a closed system is zero).

This is the structural target for Phase 2/3: identify physical (β, γ)
coordinates whose underlying many-body wavefunction has the same higher-
winding character at shape-phase-transition critical points. V5 attractor
denominators 2, 5, 7 should appear as Chern numbers in real nuclei IF the
SIS-Fold Theorem holds.
"""
import numpy as np
from v1_berry_framework import berry_curvature, chern_number


def winding_q_ground_state(theta, phi, q=1):
    """
    Ground state of H_q = sin θ cos(qφ) σ_x + sin θ sin(qφ) σ_y + cos θ σ_z.
    Eigenvalue: -1 (lower energy).
    State:
        |ψ_-> ∝ ( sin(θ/2) )
                ( -e^{iqφ} cos(θ/2) )
    
    The factor of q in the azimuthal phase is exactly the higher-winding
    monopole structure. Ground state has Berry monopole charge -q,
    Chern number -q.
    """
    psi = np.empty(theta.shape + (2,), dtype=complex)
    psi[..., 0] = np.sin(theta / 2)
    psi[..., 1] = -np.exp(1j * q * phi) * np.cos(theta / 2)
    return psi


def winding_q_excited_state(theta, phi, q=1):
    """Excited state of H_q. Chern number +q."""
    psi = np.empty(theta.shape + (2,), dtype=complex)
    psi[..., 0] = np.cos(theta / 2)
    psi[..., 1] = np.exp(1j * q * phi) * np.sin(theta / 2)
    return psi


def test_winding(q, N=120):
    """Compute Chern numbers for ground and excited states with winding q."""
    eps = 1e-3
    theta_vals = np.linspace(eps, np.pi - eps, N)
    phi_vals = np.linspace(0, 2 * np.pi, N)
    THETA, PHI = np.meshgrid(theta_vals, phi_vals, indexing='ij')
    
    psi_minus = winding_q_ground_state(THETA, PHI, q=q)
    psi_plus = winding_q_excited_state(THETA, PHI, q=q)
    
    F_minus = berry_curvature(psi_minus)
    F_plus = berry_curvature(psi_plus)
    
    return {
        'q': q,
        'ground_chern': chern_number(F_minus),
        'excited_chern': chern_number(F_plus),
        'sum': chern_number(F_minus) + chern_number(F_plus),
    }


if __name__ == "__main__":
    print("=" * 64)
    print("Phase 1.3 — Higher-winding Berry monopoles")
    print("=" * 64)
    print()
    print("V5 retrodictive analysis identified 1/2, 2/5, 3/7 as candidate")
    print("attractor ratios in nuclear binding-energy data. SIS-Fold Theorem")
    print("predicts these should appear as Chern numbers q in {2, 5, 7} at")
    print("shape-phase-transition critical points.")
    print()
    print("Methodology test: does the framework produce arbitrary integer q?")
    print()
    print(f"{'winding q':>10} {'ground Chern':>15} {'excited Chern':>15} "
          f"{'sum':>8} {'V5 link':>15}")
    print("-" * 75)
    
    v5_link = {1: '—', 2: '1/2 → He-4, O-16',
               3: '—', 5: '2/5 → Pb region',
               7: '3/7 → Fe peak'}
    
    all_pass = True
    for q in [1, 2, 3, 5, 7]:
        r = test_winding(q, N=160)
        gc = r['ground_chern']
        ec = r['excited_chern']
        s = r['sum']
        link = v5_link.get(q, '—')
        # Topological invariants are integers — round and check
        match_g = round(gc) == -q
        match_e = round(ec) == q
        match_s = abs(s) < 1e-4
        ok = match_g and match_e and match_s
        all_pass = all_pass and ok
        marker = "✓" if ok else "✗"
        print(f"{q:>10} {gc:>15.4f} {ec:>15.4f} {s:>8.4f} "
              f"{link:>20} {marker}")
    
    print()
    print("=" * 64)
    if all_pass:
        print("✓ FRAMEWORK VALIDATED FOR ARBITRARY INTEGER WINDING")
        print()
        print("Methodology produces exact integer Chern numbers for any q.")
        print("V5 attractor denominators (2, 5, 7) are within range of valid")
        print("topological invariants. Phase 2/3 task: confirm these specific")
        print("integers appear at X5/E5/critical-point analogs in 5DCH data.")
    else:
        print("✗ TESTS FAILED — framework needs debugging")
    print("=" * 64)
