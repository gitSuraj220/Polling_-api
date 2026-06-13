import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

def f(x, a):
    return 1/np.sqrt(1+x) + 1/np.sqrt(1+a) + np.sqrt((a*x)/(a*x + 8))

fig = plt.figure(figsize=(15, 6))

# ---- Panel 1: f(x) curves for several fixed a, on a log x-axis ----
ax1 = fig.add_subplot(1, 2, 1)
x = np.logspace(-3, 3, 800)
for a in [0.05, 0.5, 2, 8, 50]:
    ax1.plot(x, f(x, a), lw=2, label=f"a = {a}")
ax1.axhline(1, color='red', ls='--', lw=1.8)
ax1.axhline(2, color='red', ls='--', lw=1.8)
ax1.fill_between(x, 1, 2, color='red', alpha=0.05)
ax1.set_xscale('log')
ax1.set_ylim(0.8, 2.2)
ax1.set_xlabel("x  (log scale)")
ax1.set_ylabel("f(x)")
ax1.set_title("f(x) is always trapped in the open band (1, 2)")
ax1.text(1e-3, 2.04, "upper bound  f = 2", color='red', fontsize=10)
ax1.text(1e-3, 0.88, "lower bound  f = 1", color='red', fontsize=10)
ax1.legend(title="fixed a", loc='center right')
ax1.grid(True, which='both', alpha=0.25)

# ---- Panel 2: surface f(x,a) over the (x,a) plane (log-log grid) ----
ax2 = fig.add_subplot(1, 2, 2, projection='3d')
lx = np.linspace(-3, 3, 120)
la = np.linspace(-3, 3, 120)
LX, LA = np.meshgrid(lx, la)
X, A = 10**LX, 10**LA
Z = f(X, A)
surf = ax2.plot_surface(LX, LA, Z, cmap=cm.viridis, vmin=1, vmax=2,
                        linewidth=0, antialiased=True, alpha=0.95)
# the two limiting planes
ax2.plot_surface(LX, LA, np.full_like(Z, 1), color='red', alpha=0.12)
ax2.plot_surface(LX, LA, np.full_like(Z, 2), color='red', alpha=0.12)
ax2.set_xlabel("log10(x)")
ax2.set_ylabel("log10(a)")
ax2.set_zlabel("f(x, a)")
ax2.set_zlim(1, 2)
ax2.set_title("f(x,a):  ->2 as x,a->0   and   ->1 as x,a->inf")
ax2.view_init(elev=22, azim=-130)
fig.colorbar(surf, ax=ax2, shrink=0.5, pad=0.1, label="f value")

plt.suptitle(r"$f(x)=\frac{1}{\sqrt{1+x}}+\frac{1}{\sqrt{1+a}}+\sqrt{\frac{ax}{ax+8}}$   satisfies   $1 < f < 2$",
             fontsize=14)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig("/home/user/Polling_-api/fx_visualization.png", dpi=140, bbox_inches='tight')
print("min over grid:", Z.min(), "  max over grid:", Z.max())
