import matplotlib.pyplot as plt

scenarios = ['Current State', '10% Return', '30% Return', '50% Return']

revenue = [0.0, 0.1, 0.3, 0.5]
plt.figure(figsize=(10, 6), facecolor='white')
tum_blue = '#005293'
plt.plot(scenarios, revenue, color=tum_blue, marker='o', linewidth=2.5, markersize=8, label='Revenue')

plt.title('Revenue Recovery Projection', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('Revenue (in Millions €)', fontsize=12, labelpad=10)
plt.xlabel('Return Scenarios', fontsize=12, labelpad=10)

plt.ylim(0, 0.6)

plt.grid(axis='y', linestyle='--', alpha=0.5)

for spine in ['top', 'right']:
    plt.gca().spines[spine].set_visible(False)

plt.legend(loc='lower center', frameon=False)

plt.tight_layout()
print("Generating your revenue projection chart...")
plt.show()