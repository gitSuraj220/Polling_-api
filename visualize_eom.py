import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# Example kinematic parameters
u = 5.0     # initial velocity (m/s)
a = 2.0     # acceleration (m/s^2)
T = 6.0     # time window (s)
t = np.linspace(0, T, 400)
v = u + a*t
s = u*t + 0.5*a*t**2

fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

# ---------- Panel 1: v-t graph as a GEOMETRIC derivation ----------
ax = axes[0]
ax.plot(t, v, color='navy', lw=2.5, label=r"$v = u + at$")
# rectangle: u * t  (area = u t)
rect = Polygon([[0, 0], [T, 0], [T, u], [0, u]], closed=True,
               facecolor='skyblue', alpha=0.55, edgecolor='navy')
ax.add_patch(rect)
# triangle: 1/2 * t * (at)
tri = Polygon([[0, u], [T, u], [T, u + a*T]], closed=True,
              facecolor='salmon', alpha=0.55, edgecolor='darkred')
ax.add_patch(tri)
ax.text(T/2, u/2, r"rectangle$= u\,t$", ha='center', va='center', fontsize=12)
ax.text(T*0.72, u + a*T*0.33, r"triangle$=\frac{1}{2}(at)(t)$",
        ha='center', va='center', fontsize=12)
ax.annotate("", xy=(T, u), xytext=(T, u + a*T),
            arrowprops=dict(arrowstyle='<->', color='darkred'))
ax.text(T+0.1, u + a*T/2, r"$at$", color='darkred', fontsize=12, va='center')
ax.annotate("", xy=(0, 0), xytext=(0, u),
            arrowprops=dict(arrowstyle='<->', color='navy'))
ax.text(-0.45, u/2, r"$u$", color='navy', fontsize=12, va='center')
ax.set_xlim(0, T+1); ax.set_ylim(0, u + a*T + 2)
ax.set_xlabel("time  t"); ax.set_ylabel("velocity  v")
ax.set_title("Area under v–t graph = displacement\n"
             r"$s = ut + \frac{1}{2}at^2$")
ax.legend(loc='upper left'); ax.grid(alpha=0.25)

# ---------- Panel 2: velocity vs time (1st equation) ----------
ax = axes[1]
ax.plot(t, v, color='navy', lw=2.5)
ax.scatter([0], [u], color='red', zorder=5)
ax.text(0.2, u-1.2, f"u = {u:g} m/s", color='red', fontsize=11)
ax.text(T*0.45, u + a*T*0.30,
        f"slope = a = {a:g} m/s²", color='navy', fontsize=11, rotation=18)
ax.set_xlabel("time  t"); ax.set_ylabel("velocity  v")
ax.set_title(r"1st equation:   $v = u + at$")
ax.grid(alpha=0.25); ax.set_xlim(0, T)

# ---------- Panel 3: displacement vs time (2nd equation) ----------
ax = axes[2]
ax.plot(t, s, color='darkgreen', lw=2.5)
ax.fill_between(t, 0, s, color='lightgreen', alpha=0.3)
ax.set_xlabel("time  t"); ax.set_ylabel("displacement  s")
ax.set_title(r"2nd equation:   $s = ut + \frac{1}{2}at^2$"
             "\n(parabola — tangent slope = v)")
ax.grid(alpha=0.25); ax.set_xlim(0, T)

plt.suptitle("Equations of Motion (uniform acceleration a):   "
             r"$v=u+at$,   $s=ut+\frac{1}{2} at^2$,   $v^2=u^2+2as$",
             fontsize=15)
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig("/home/user/Polling_-api/eom_visualization.png", dpi=140, bbox_inches='tight')

# numeric check of v^2 = u^2 + 2as
lhs = v**2
rhs = u**2 + 2*a*s
print("max |v^2 - (u^2+2as)| =", np.max(np.abs(lhs - rhs)))
