// ReviewLens AI - Charting Utilities (Chart.js 4.x)

const chartInstances = {};

function destroyChart(key) {
  if (chartInstances[key]) {
    chartInstances[key].destroy();
    delete chartInstances[key];
  }
}

const charts = {
  renderSentimentDoughnut(canvasId, counts) {
    destroyChart(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const total = (counts.positive || 0) + (counts.neutral || 0) + (counts.negative || 0);

    chartInstances[canvasId] = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Positive', 'Neutral', 'Negative'],
        datasets: [{
          data: [counts.positive || 0, counts.neutral || 0, counts.negative || 0],
          backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
          hoverBackgroundColor: ['#059669', '#d97706', '#dc2626'],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              padding: 16,
              font: { family: 'Inter', size: 12, weight: '500' }
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const val = context.raw || 0;
                const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                return ` ${context.label}: ${val} reviews (${pct}%)`;
              }
            }
          }
        }
      }
    });
  },

  renderProductComparison(canvasId, products) {
    destroyChart(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const labels = products.map(p => {
      // Shorten label if too long
      return p.name.length > 18 ? p.name.substring(0, 16) + '...' : p.name;
    });

    chartInstances[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Positive %',
            data: products.map(p => p.positive_pct),
            backgroundColor: '#10b981',
            borderRadius: 6
          },
          {
            label: 'Neutral %',
            data: products.map(p => p.neutral_pct),
            backgroundColor: '#f59e0b',
            borderRadius: 6
          },
          {
            label: 'Negative %',
            data: products.map(p => p.negative_pct),
            backgroundColor: '#ef4444',
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            grid: { display: false },
            ticks: { font: { family: 'Inter', size: 11 } }
          },
          y: {
            beginAtZero: true,
            max: 100,
            ticks: {
              callback: value => `${value}%`,
              font: { family: 'Inter', size: 11 }
            },
            grid: { color: '#f1f5f9' }
          }
        },
        plugins: {
          legend: {
            position: 'top',
            align: 'end',
            labels: {
              boxWidth: 10,
              padding: 12,
              font: { family: 'Inter', size: 11 }
            }
          },
          tooltip: {
            callbacks: {
              label: context => ` ${context.dataset.label}: ${context.raw}%`
            }
          }
        }
      }
    });
  },

  renderProductDetailDoughnut(canvasId, stats) {
    destroyChart(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    chartInstances[canvasId] = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Positive', 'Neutral', 'Negative'],
        datasets: [{
          data: [stats.positive_count, stats.neutral_count, stats.negative_count],
          backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { boxWidth: 10, padding: 10, font: { family: 'Inter', size: 11 } }
          }
        }
      }
    });
  }
};

window.charts = charts;
