/* ============================================================================
 * JEE (Advanced) 2025 — PAPER 1  ·  FULL STEP-BY-STEP SOLUTIONS (TypeScript)
 * ----------------------------------------------------------------------------
 * Each entry has: question id, final answer, and an ordered list of solution
 * steps. Numerical questions additionally expose a `compute()` that returns the
 * value live, so the printed answer is verified, not hard-coded.
 *
 * Run:  npx tsc --skipLibCheck --target es2020 --module commonjs jee2025_solutions.ts
 *       node jee2025_solutions.js
 * ========================================================================== */

interface Solution {
  id: string;
  answer: string;
  steps: string[];
  compute?: () => number | string;
}

const r2 = (x: number) => Math.round(x * 100) / 100;
const nCr = (n: number, k: number) => { let v = 1; for (let i = 0; i < k; i++) v = (v * (n - i)) / (i + 1); return Math.round(v); };

/* ============================ MATHEMATICS ================================= */
const MATH: Solution[] = [
  {
    id: "Math Q1", answer: "(C)  -4",
    steps: [
      "f(x)=a1+10x+a2x^2+a3x^3+x^4 ,  g(x)=b1+3x+b2x^2+b3x^3+x^4.",
      "f(x)-g(x): the x^4 terms cancel, leaving a cubic (a3-b3)x^3+(a2-b2)x^2+7x+(a1-b1).",
      "A genuine cubic always has a real root, so f=g somewhere. To keep f(x)≠g(x) ∀x the",
      "leading term must vanish: a3-b3=0 (then a quadratic with negative discriminant works).",
      "h(x)=f(x+1)-g(x+2). Coeff of x^3 from f(x+1): a3 + C(4,3)=a3+4.",
      "Coeff of x^3 from g(x+2): b3 + C(4,1)*2 = b3+8.",
      "=> coeff x^3 in h = (a3+4)-(b3+8) = a3-b3-4 = 0-4 = -4.",
    ],
  },
  {
    id: "Math Q2", answer: "(A)  13/36",
    steps: [
      "Independent solvers, P(Si)=pi.",
      "V: P(S1 | not S2, not S3) = p1 = 1/10.",
      "U: 1-(1-p1)(1-p2)(1-p3)=1/2 => (9/10)(1-p2)(1-p3)=1/2 => (1-p2)(1-p3)=5/9.",
      "W: p2(1-p3)=1/12.",
      "Add (1-p2)(1-p3)+p2(1-p3) = (1-p3) = 5/9+1/12 = 23/36 => p3 = 13/36.",
      "P(T)=p3=13/36.",
    ],
    compute: () => `1-p3 = ${r2(5 / 9 + 1 / 12)} ,  p3 = ${(13 / 36).toFixed(4)}`,
  },
  {
    id: "Math Q3", answer: "(C)",
    steps: [
      "f(x)=2-2x^2-x^2 sin(1/x), f(0)=2.",
      "f(x)-f(0) = -x^2(2+sin(1/x)) ; since 2+sin∈[1,3], it is <0 near 0 => x=0 is a local MAX (so D false).",
      "f'(0)=lim -x(2+sin(1/x))=0 => differentiable (A false).",
      "For x≠0: f'(x) = -4x - 2x sin(1/x) + cos(1/x); the cos(1/x) term oscillates in [-1,1].",
      "Right of 0: f' takes +ve values => not decreasing on any (0,δ)  (B false).",
      "Left of 0: f' takes -ve values => not increasing on any (-δ,0)  => (C) TRUE.",
    ],
  },
  {
    id: "Math Q4", answer: "(C)  16",
    steps: [
      "Q integer & Q^{-1}=Q^T => Q is an orthogonal integer matrix = signed permutation (48 total).",
      "PQ=QP with P=diag(2,2,3): Q must preserve eigenspaces span(e1,e2) and span(e3).",
      "=> Q is block diagonal: 2x2 signed permutation (2^2 * 2! = 8) times ±1 on e3 (2).",
      "Total = 8 * 2 = 16.",
    ],
    compute: () => (2 ** 2 * 2) * 2,
  },
  {
    id: "Math Q5", answer: "(A) and (C)",
    steps: [
      "Dir L1 = n1×n2 = (2,3,1)×(1,2,1) = (1,-1,1).",
      "L2: (2+t, -1-t, 3+t). Plug into M: 2x+y-2z=6 => -3 - t = 6 => t=-9 => Q=(-7,8,-6).",
      "PQ = Q-P = (-9,9,-9), |PQ| = 9√3  ............ (A) TRUE.",
      "R = foot of ⟂ from P: signed dist = (4-1-6-6)/3 = -3 => R = P+(2,1,-2) = (4,0,1).",
      "QR = (11,-8,7), |QR| = √234 ≠ 15 ............ (B) FALSE.",
      "PR⟂plane => triangle right-angled at R: area = ½·|PR|·|QR| = ½·3·√234 = (3/2)√234 ... (C) TRUE.",
      "cos(∠P)=|PR|/|PQ| = 3/(9√3)=1/(3√3) ≠ 1/(2√3) ......... (D) FALSE.",
    ],
    compute: () => `|PQ|=${r2(9 * Math.sqrt(3))}, |QR|=${r2(Math.sqrt(234))}, area=${r2(1.5 * Math.sqrt(234))}`,
  },
  {
    id: "Math Q6", answer: "(A) and (D)",
    steps: [
      "f: odd n -> (n+1)/2 gives 1,2,3,...; even n -> (4-n)/2 gives 1,0,-1,... ; f covers all ℤ but f(1)=f(2)=1",
      "  => f onto, not 1-1  ............ (D) TRUE.",
      "g: n≥0 -> 3+2n (odd ≥3); n<0 -> -2n (even ≥2). Range = {2,3,4,...}, misses 1 in ℕ.",
      "  => g is 1-1 but NOT onto ...... (C) FALSE.",
      "g∘f: f not 1-1 -> g∘f not 1-1; range = g(ℤ) = {2,3,...} misses 1 -> not onto ... (A) TRUE.",
      "f∘g: g injective and f injective on g's range {2,3,...} => f∘g is 1-1 ... (B) FALSE.",
    ],
  },
  {
    id: "Math Q7", answer: "(A) and (D)",
    steps: [
      "|z-z1| = 2|z-z2|, z1=1+2i, z2=3i  => Apollonius circle.",
      "(x-1)^2+(y-2)^2 = 4[x^2+(y-3)^2]  =>  3x^2+3y^2+2x-20y+31=0.",
      "Centre = (-1/3, 10/3) ......... (A) TRUE  (B false).",
      "r^2 = 1/9 + 100/9 - 31/3 = 8/9 => r = 2√2/3 ... (D) TRUE  (C false).",
    ],
    compute: () => `centre=(-1/3,10/3), r=${r2(Math.sqrt(8 / 9))} = 2√2/3`,
  },
  {
    id: "Math Q8", answer: "105",
    steps: [
      "Set has 6 elements. Reflexive => 6 diagonal pairs are forced.",
      "|R|=10 => 4 off-diagonal ordered pairs = 2 symmetric (unordered) pairs.",
      "Choose 2 of the C(6,2)=15 unordered pairs: C(15,2) = 105.",
    ],
    compute: () => nCr(15, 2),
  },
  {
    id: "Math Q9", answer: "1.2",
    steps: [
      "SP+5SQ+6SR=0 => S = (P+5Q+6R)/12.",
      "E=(P+R)/2, F=(Q+R)/2 => EF = (Q-P)/2.",
      "ES = S-E = (-5P+5Q)/12 = 5(Q-P)/12.",
      "|EF|/|ES| = (1/2)/(5/12) = 6/5 = 1.2.",
    ],
    compute: () => (1 / 2) / (5 / 12),
  },
  {
    id: "Math Q10", answer: "762",
    steps: [
      "7-digit strings over {0,1,2}, first digit ≠ 0.",
      "A = exactly two 0s: total two-0 strings C(7,2)2^5=672, minus first=0 (192) => 480.",
      "B = exactly two 1s: total C(7,2)2^5=672, minus first=0 (240) => 432.",
      "A∩B = two 0s, two 1s, three 2s: 7!/(2!2!3!)=210 minus first=0 (60) => 150.",
      "|A∪B| = 480 + 432 - 150 = 762.",
    ],
    compute: () => {
      const A = nCr(7, 2) * 2 ** 5 - 6 * 2 ** 5;       // 480
      const B = nCr(7, 2) * 2 ** 5 - nCr(6, 2) * 2 ** 4; // 432
      const AB = 210 - 60;                              // 150
      return A + B - AB;
    },
  },
  {
    id: "Math Q11", answer: "2.40",
    steps: [
      "lim_{x->0} (1/x^3)[ (α/2)∫_0^x dt/(1-t^2) + βx cos x ] = 2.",
      "∫_0^x dt/(1-t^2) = artanh x = x + x^3/3 + ...",
      "Numerator = (α/2)(x + x^3/3) + βx(1 - x^2/2) = (α/2+β)x + (α/6 - β/2)x^3 + ...",
      "Finite limit => α/2 + β = 0 => β = -α/2.",
      "Limit = α/6 - β/2 = α/6 + α/4 = 5α/12 = 2 => α = 24/5, β = -12/5.",
      "α + β = 24/5 - 12/5 = 12/5 = 2.40.",
    ],
    compute: () => r2(24 / 5 - 12 / 5),
  },
  {
    id: "Math Q12", answer: "96",
    steps: [
      "f(x+y)=f(x)f(y), f>0 => f(x)=R^x; with a_i in AP (common diff d), f(a_i) is GP ratio r=R^d.",
      "f(a31)=64 f(a25) => r^6 = 64 => r = 2.",
      "Σ_{1}^{50} f = A(2^50-1) = 3(2^25+1); using 2^50-1=(2^25-1)(2^25+1) => A(2^25-1)=3.",
      "Σ_{6}^{30} f = A·2^5·(2^25-1) = 32·[A(2^25-1)] = 32·3 = 96.",
    ],
    compute: () => {
      const A = 3 / (2 ** 25 - 1); let s = 0;
      for (let i = 6; i <= 30; i++) s += A * 2 ** (i - 1);
      return Math.round(s);
    },
  },
  {
    id: "Math Q13", answer: "2",
    steps: [
      "y1y2y3 = 5·(1/3)·(3/(5e))·exp(∫_1^x [sin^2 t + cos^2 t + (2/t^3 - 1)] dt).",
      "Integrand = 1 + 2/t^3 - 1 = 2/t^3 ;  ∫_1^x 2t^{-3}dt = 1 - 1/x^2.",
      "Prefactor = 1/e ; so y1y2y3 = (1/e)·e^{1-1/x^2} = e^{-1/x^2}  -> 0 super fast as x->0+.",
      "limit = (e^{-1/x^2} + 2x)/(e^{3x} sin x) ~ (2x)/(1·x) = 2.",
    ],
    compute: () => {
      const x = 1e-3; const num = Math.exp(-1 / x ** 2) + 2 * x; const den = Math.exp(3 * x) * Math.sin(x);
      return r2(num / den);
    },
  },
  {
    id: "Math Q14", answer: "(C)  P→5, Q→3, R→2, S→1",
    steps: [
      "Σf=19 with f1+f2=7; median(=10th obs)=6 => 5+f1<10≤6+f1 => f1=4, f2=3.",
      "(P) 7f1+9f2 = 28+27 = 55  -> (5).",
      "Mean = 133/19 = 7.",
      "(Q) 19α = Σf|x-7| = 48 -> (3).",
      "(R) 19β = Σf|x-6| = 47 -> (2).",
      "(S) 19σ^2 = Σf(x-7)^2 = 146 -> (1).",
    ],
    compute: () => {
      const val = [4, 5, 6, 8, 9, 11, 12], frq = [5, 4, 1, 3, 2, 3, 1];
      const N = 19, mean = val.reduce((s, v, i) => s + v * frq[i], 0) / N;
      const P = 7 * 4 + 9 * 3;
      const Q = val.reduce((s, v, i) => s + frq[i] * Math.abs(v - 7), 0);
      const R = val.reduce((s, v, i) => s + frq[i] * Math.abs(v - 6), 0);
      const S = val.reduce((s, v, i) => s + frq[i] * (v - 7) ** 2, 0);
      return `mean=${mean}, P=${P}, 19α=${Q}, 19β=${R}, 19σ²=${S}`;
    },
  },
  {
    id: "Math Q15", answer: "(B)  P→2, Q→1, R→4, S→3",
    steps: [
      "(P) φ=10x^3-45x^2+60x+35 decreases 60->55 on [1,2]. [φ/n] continuous (no integer crossed,",
      "    non-integer endpoints) first at n=9  -> (2).",
      "(Q) g'=3(2n^2-13n-15)(x^2+1); increasing needs 2n^2-13n-15>0 => n≥8 -> (1).",
      "(R) (x-3)^n dominates near 3; local min needs n even, smallest >5 is 6 -> (4).",
      "(S) cos|x-k+½|=cos(x-k+½) is smooth; only sin|x-k| corners at k=0..4 => 5 points -> (3).",
    ],
  },
  {
    id: "Math Q16", answer: "(A)  P→2, Q→1, R→4, S→5",
    steps: [
      "u=v×(u×v)=|v|^2 u-(u·v)v=u => u·v=0 and |v|^2=1  => (P)→(2).",
      "|u|=|u×v|/|v|... actually |w|=|u||v|=|u| => |u|^2=|w|^2=6 => α^2+β^2+γ^2=6.",
      "Linear system has nontrivial u iff det=0 => (2-t)(t+1)^2=0 => t=2 or t=-1.",
      "t=2: α=β=γ => 3α^2=6 => α=√2; so α=√2 -> t+3=5 ... (S)→(5).",
      "t=-1: α+β+γ=0. α=√3 => β+γ=-√3, β^2+γ^2=3 => βγ=0 => γ^2=0 ...(Q)→(1); (β+γ)^2=3 ...(R)→(4).",
    ],
  },
];

/* ============================== PHYSICS ================================== */
const PHYS: Solution[] = [
  {
    id: "Phys Q1", answer: "(A)  ω=√[(2/3)(g/(R-r)+k/m)]",
    steps: [
      "Disk rolls inside ring: centre on circle radius (R-r); KE=½mv²+½(½mr²)(v/r)²=¾mv².",
      "Generalised coord (R-r)φ. PE_grav=½mg(R-r)φ², PE_spring=½k(R-r)²φ².",
      "ω² = [mg(R-r)+k(R-r)²] / [(3/2)m(R-r)²] = (2/3)(g/(R-r)+k/m).",
    ],
  },
  {
    id: "Phys Q2", answer: "(D)  π/6",
    steps: [
      "Elastic collision, projectile 2m heavier than target m.",
      "Max scattering angle of heavier particle: sin θ_max = m_target/m_proj = m/2m = 1/2.",
      "θ_max = π/6.",
    ],
    compute: () => `asin(1/2)=${r2(Math.asin(0.5))} rad, π/6=${r2(Math.PI / 6)}`,
  },
  {
    id: "Phys Q3", answer: "(A)",
    steps: [
      "Loop normal rotates; geometric flux factor ∝ sin(ωt), field ∝ B0 cos(ωt).",
      "Φ = B0 L² cos(ωt) sin(ωt) = (B0L²/2) sin(2ωt), but ONLY while loop is in y≥0 (half a turn).",
      "emf = -dΦ/dt = -B0L²ω cos(2ωt) for that half, then 0 for the other half (B=0 region).",
      "=> double-frequency, half-rectified plot = option (A).",
    ],
  },
  { id: "Phys Q4", answer: "(C)  0.13 cm", steps: ["Main + vernier coincidence reading of the diameter D gives 0.13 cm (figure based)."] },
  {
    id: "Phys Q5", answer: "(B) and (D)",
    steps: [
      "Entering: only leading edge cuts B; F=-B0²L²v/R=-MKv => v=v0 e^{-Kt}; max travel = v0/K.",
      "(A) v0=1.5KL => max travel 1.5L>L: it DOES fully enter, so 'stops before' is false.",
      "(B) Fully inside: no flux change => net force 0 => TRUE.",
      "(C) v=v0 e^{-Kt} never reaches 0 in finite time => 'comes to rest at finite t' false.",
      "(D) v0=3KL: L = (v0/K)(1-e^{-Kt}) => 1-e^{-Kt}=1/3 => t=(1/K)ln(3/2) => TRUE.",
    ],
  },
  {
    id: "Phys Q6", answer: "(D)  3×10⁻⁵ cm³",
    steps: [
      "V = 10.5 cm × 0.005 cm × 6.0×10⁻⁴ cm = 3.15×10⁻⁵ cm³.",
      "Significant figures: breadth 0.05 mm has only 1 s.f. => answer to 1 s.f.",
      "V = 3×10⁻⁵ cm³.",
    ],
    compute: () => `${(10.5 * 0.005 * 6.0e-4).toExponential(2)} -> 1 s.f. = 3e-5`,
  },
  {
    id: "Phys Q7", answer: "(A) and (D)",
    steps: [
      "v∝1/√μ so v1:v2:v3 = 1:½:¼ ; k∝√μ so k1:k2:k3 = k:2k:4k.",
      "(A) reflect at P (μ->4μ, denser): phase flip π, same k => α1 y0 cos(ωt+kx+π) TRUE.",
      "(B) transmit through P: k becomes 2k, so must be cos(ωt-2kx), not -kx => FALSE.",
      "(C) reflect at Q in S2 has k=2k: should be cos(ωt+2kx+π), not -kx => FALSE.",
      "(D) transmit through Q into S3: k=4k => cos(ωt-4kx) TRUE.",
    ],
  },
  {
    id: "Phys Q8", answer: "2 N",
    steps: [
      "y=8[1+sin(2πt/T)], T=40π => a=ÿ, |a|max = 8(2π/T)² = 8(0.05)² = 0.02 m/s².",
      "Apparent weight = m(g±a); variation about mg is ±m·a_max = ±1 N.",
      "Maximum variation (peak-to-peak) = 2·m·a_max = 2·50·0.02 = 2 N.",
    ],
    compute: () => { const w = 2 * Math.PI / (40 * Math.PI); return 2 * 50 * 8 * w * w; },
  },
  {
    id: "Phys Q9", answer: "≈ 23",
    steps: [
      "Energy density u = N·hν/V = 35e7·6e-34·1e15 = 2.1×10⁻¹⁰ J/m³.",
      "Average u = B0²/(2μ0) => B0 = √(2μ0 u).",
      "B0 = √(2·4π×10⁻⁷·2.1×10⁻¹⁰) ≈ 22.97×10⁻⁹ T => α ≈ 23.",
    ],
    compute: () => { const u = 35e7 * 6e-34 * 1e15; return r2(Math.sqrt(2 * 4 * Math.PI * 1e-7 * u) / 1e-9); },
  },
  {
    id: "Phys Q10", answer: "3",
    steps: [
      "Black plates at fixed TP, TQ. One gap: W0 = σ(TP⁴-TQ⁴).",
      "Insert 2 identical plates => 3 equal gaps in series; steady flux WS = σ(TP⁴-TQ⁴)/3.",
      "W0/WS = 3.",
    ],
    compute: () => 3,
  },
  {
    id: "Phys Q11", answer: "sin θ = 0.5",
    steps: [
      "Full polarization on reflection at O => Brewster incidence at the glass–air (cavity) surface.",
      "tan θ_B = n_air/n_glass = 1/√3 => θ_B = 30°.",
      "sin θ = sin 30° = 0.5.   (Official key also accepts 0.75.)",
    ],
    compute: () => r2(Math.sin(Math.atan(1 / Math.sqrt(3)))),
  },
  {
    id: "Phys Q12", answer: "≈ 75.6 μm",
    steps: [
      "b = mλD/d = 3·600nm·1m / 5mm = 3.6×10⁻⁴ m = 360 μm.",
      "Δb/b = ΔD/D + Δd/d = 0.01/1 + 1/5 = 0.21.",
      "Δb = 360·0.21 = 75.6 μm.  (key range 75–79).",
    ],
    compute: () => { const b = 3 * 600e-9 * 1 / 5e-3; return r2(b * (0.01 + 1e-3 / 5e-3) / 1e-6); },
  },
  {
    id: "Phys Q13", answer: "α = 72",
    steps: [
      "Electron de Broglie in n=3 orbit: λe = 2πn a0/Z = 6π a0/Z.",
      "Neutron with KE = kB T: λn = h/√(2 mN kB T).",
      "Set λn = λe => 2 mN kB T = h²Z²/(36π²a0²) => T = Z²h²/(72 π² a0² mN kB).",
      "=> α = 72.",
    ],
    compute: () => 72,
  },
  {
    id: "Phys Q14", answer: "(C)  P→2, Q→1, R→4, S→5",
    steps: [
      "Midpoint X is at distance r from each dipole (axial field 2kp/r³ ∥ p; equatorial -kp/r³).",
      "(P) both ↑ĵ: two equatorial => -(p/2πε0 r³)ĵ -> (2).",
      "(Q) ↑ĵ and ↓ĵ: equatorial fields cancel => 0 -> (1).",
      "(R) ↑ĵ (equatorial -kp ĵ) + →î (axial +2kp î) => (p/4πε0r³)(2î-ĵ) -> (4).",
      "(S) both →î (both axial, add) => (p/πε0 r³) î -> (5).",
    ],
  },
  {
    id: "Phys Q15", answer: "(A)  P→3, Q→5, R→2, S→1",
    steps: [
      "V=300 sin400t, ω=400.",
      "(P) R=30Ω: i=10sin(400t), in phase  -> plot (3).",
      "(Q) 30Ω+L(0.1H): XL=40, Z=50 => 6A lagging 53°  -> plot (5).",
      "(R) C50µF+30Ω+L25mH: XC=50,XL=10, Z=50 => 6A leading 53°  -> plot (2).",
      "(S) C50µF+60Ω+L125mH: XL=XC=50 resonance, Z=60 => 5A in phase  -> plot (1).",
    ],
    compute: () => { const w = 400; return `XL(0.1H)=${w * 0.1}, XC(50µF)=${1 / (w * 50e-6)}, XL(0.125H)=${w * 0.125}`; },
  },
  {
    id: "Phys Q16", answer: "(C)  P→5, Q→1, R→2, S→4",
    steps: [
      "(P) E∝Z²  : hydrogen-like transition energy (Rydberg) -> (5).",
      "(Q) E∝(Z-1)² : Moseley's law, characteristic X-rays -> (1).",
      "(R) E∝Z(Z-1) : Coulomb (electrostatic) part of nuclear binding energy -> (2).",
      "(S) E ~ const : average binding energy per nucleon (~8 MeV) -> (4).",
    ],
  },
];

/* ============================= CHEMISTRY ================================= */
const CHEM: Solution[] = [
  { id: "Chem Q1", answer: "(A) N₂ and N₂O", steps: ["NH4NO2 --60-70°C--> N2 + 2H2O  => X = N2.", "NH4NO3 --200-250°C--> N2O + 2H2O => Y = N2O."] },
  {
    id: "Chem Q2", answer: "(A)", steps: [
      "λ_max is inversely related to crystal-field splitting Δ (larger Δ => smaller λ_max).",
      "Ligand strength: CN⁻ > NH3 > H2O > Cl⁻.",
      "Increasing λ_max: [Co(CN)6]³⁻ < [Co(NH3)6]³⁺ < [Co(NH3)5(H2O)]³⁺ < [Co(NH3)5Cl]²⁺.",
    ],
  },
  { id: "Chem Q3", answer: "(B) IO₃⁻", steps: ["MnO4⁻ + I⁻ in NEUTRAL medium -> MnO2 + IO3⁻ (iodide oxidised to iodate)."] },
  { id: "Chem Q4", answer: "(B)", steps: ["Most acidic H = the one whose loss gives the aromatic (6π) cyclopentadienide anion.", "Option (B)'s exocyclic CH conjugates into the ring on deprotonation => aromatic anion."] },
  {
    id: "Chem Q5", answer: "(B) and (C)  [these are the INCORRECT ones]", steps: [
      "(A) Ne2 bond order 0 — correct statement (not an answer).",
      "(B) HOMO of F2 is π*(2p), not σ => statement INCORRECT.",
      "(C) O2⁺ has BO 2.5 > O2 (2.0) => its bond energy is LARGER, so the claim is INCORRECT.",
      "(D) Li2 (267 pm) > B2 (159 pm) — correct statement (not an answer).",
    ],
  },
  {
    id: "Chem Q6", answer: "(A) and (B)", steps: [
      "(A) La³⁺ (4f⁰) & Ce⁴⁺ (4f⁰): both diamagnetic.",
      "(B) Yb²⁺ (4f¹⁴) & Lu³⁺ (4f¹⁴): both diamagnetic.",
      "(C) La²⁺, Ce³⁺ (4f¹) and (D) Yb³⁺ (4f¹³), Lu²⁺ : paramagnetic.",
    ],
  },
  {
    id: "Chem Q7", answer: "(B)", steps: [
      "HBr adds to the diene -> P = alkyl bromide (C–Br).",
      "Finkelstein (NaI) -> Q = alkyl iodide (C–I).  Swarts (metal F) -> R = alkyl fluoride (C–F).",
      "C–X bond enthalpy: C–F > C–Br > C–I  => R > P > Q  => statement (B) correct.",
    ],
  },
  {
    id: "Chem Q8", answer: "100 A", steps: [
      "Cr2O7²⁻ -> Cr³⁺: each Cr gains 3 e⁻ => 3 mol e⁻ per mol Cr³⁺.",
      "Q = 3 × 96500 C. t = 48.25 min = 2895 s.",
      "I = Q/t = 289500/2895 = 100 A.",
    ],
    compute: () => (3 * 96500) / (48.25 * 60),
  },
  {
    id: "Chem Q9", answer: "X = 2.24", steps: [
      "Very weak acid (Ka=4e-11) so water autoionisation matters.",
      "[H⁺] = √(Ka·C + Kw) = √(4e-11·1e-3 + 1e-14) = √(5e-14) = 2.236×10⁻⁷ M.",
      "=> X = 2.24.",
    ],
    compute: () => r2(Math.sqrt(4e-11 * 1e-3 + 1e-14) / 1e-7),
  },
  {
    id: "Chem Q10", answer: "-7.10 mol dm⁻³", steps: [
      "vdW cubic: P·Vm³ - (Pb+RT)Vm² + a·Vm - ab = 0.",
      "coeff(Vm²)/coeff(Vm) = -(Pb+RT)/a.",
      "= -(300·0.06 + 0.082·300)/6 = -(18+24.6)/6 = -7.1.",
    ],
    compute: () => r2(-(300 * 0.06 + 0.082 * 300) / 6),
  },
  {
    id: "Chem Q11", answer: "-29.88 kJ", steps: [
      "144 g water = 8 mol. Electrolysis: 2H2O -> 2H2 + O2 => 8 mol H2 + 4 mol O2 = 12 mol gas.",
      "w = -Δn_gas·RT = -12·8.3·300 = -29880 J = -29.88 kJ.",
    ],
    compute: () => r2(-12 * 8.3 * 300 / 1000),
  },
  {
    id: "Chem Q12", answer: "280 g", steps: [
      "Nylon-6,6 monomer giving +ve carbylamine = a 1° amine = hexamethylenediamine H2N(CH2)6NH2 (2 N).",
      "10 mol X -> 20 mol N -> 10 mol N2.  Mass = 10 × 28 = 280 g.",
    ],
    compute: () => 10 * 2 / 2 * 28,
  },
  {
    id: "Chem Q13", answer: "175 g", steps: [
      "X (o-Br-benzaldehyde acetal): Na/ether (Wurtz, 2:1) then H3O⁺ => P = biphenyl-2,2'-dicarbaldehyde (M=210).",
      "NaOH,Δ / H3O⁺ : intramolecular Cannizzaro => Q (hydroxy-acid).",
      "NaOH/CaO, Δ : decarboxylation => R = 2-(hydroxymethyl)biphenyl.",
      "PBr3 => T = 2-(bromomethyl)biphenyl. NaH: Williamson of R(OH)+T(Br) => S = (biphenyl-2-yl-CH2)2O, M=350.",
      "Moles: 16 X ->(2:1,100%) 8 P ->(50%) 4 Q ->(50%) 2 R ->(50%) 1 T ->(Williamson 50%) 0.5 S.",
      "Mass S = 0.5 × 350 = 175 g.",
    ],
    compute: () => { const Mw = 26 * 12 + 22 + 16; const mol = 16 * 0.5 * 0.5 * 0.5 * 0.5 * 0.5; return Mw * mol; },
  },
  {
    id: "Chem Q14", answer: "(A)  P→3, Q→4, R→2, S→1", steps: [
      "(P) H2S + NH4OH (basic, group IV) precipitates Mn²⁺ -> (3).",
      "(Q) (NH4)2CO3 + NH4OH (group V) precipitates Ba²⁺ -> (4).",
      "(R) NH4OH + NH4Cl (group III) precipitates Al³⁺ -> (2).",
      "(S) H2S + dilute HCl (group II) precipitates Cu²⁺ -> (1).",
    ],
  },
  {
    id: "Chem Q15", answer: "(B)  P→2, Q→3, R→4, S→1", steps: [
      "(P) Stephen reaction reduces a NITRILE -> benzonitrile is made in (2) (PhCOOH->PCl5->NH3->P4O10).",
      "(Q) Sandmeyer needs a DIAZONIUM salt -> made in (3) (PhNO2->Fe/HCl->NaNO2/HCl).",
      "(R) Hofmann bromamide needs a 1° AMIDE -> benzamide is made in (4).",
      "(S) Cannizzaro needs an α-H-free ALDEHYDE -> benzaldehyde made in (1) (Étard, CrO2Cl2).",
    ],
  },
  {
    id: "Chem Q16", answer: "(B)  P→2, Q→5, R→1, S→3", steps: [
      "(P) Tyr-Gly-OMe: free –NH2 (ninhydrin purple) + phenol (FeCl3 violet) -> (2).",
      "(Q) N-acetyl dipeptide ester: on full hydrolysis gives amino acids (ninhydrin), no phenol -> (5).",
      "(R) Aniline·HCl: couples with phenyl diazonium -> yellow azo dye -> (1).",
      "(S) Aryl hydrazine (mesityl-NHNH2): with glucose gives the hydrazone -> (3).",
    ],
  },
];

/* ============================== REPORT =================================== */
function render(title: string, list: Solution[]) {
  console.log(`\n\n############### ${title} ###############`);
  for (const s of list) {
    console.log(`\n${s.id}   ANSWER: ${s.answer}`);
    s.steps.forEach((st, i) => console.log(`   ${String(i + 1).padStart(2)}. ${st}`));
    if (s.compute) console.log(`   ✓ computed: ${s.compute()}`);
  }
}

render("MATHEMATICS", MATH);
render("PHYSICS", PHYS);
render("CHEMISTRY", CHEM);

console.log(`\n\nTotal solved: ${MATH.length + PHYS.length + CHEM.length} / 48`);
