// ReviewLens AI - Main Application Controller

document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

let currentProductId = null;
let currentReviewFilter = 'all';

function initApp() {
  setupNavigation();
  setupAnalyzer();
  checkBackendHealth();
  
  // Handle initial hash or default to overview
  const initialHash = window.location.hash.replace('#', '') || 'overview';
  navigateTo(initialHash);
  
  // Refresh Lucide icons
  if (window.lucide) {
    lucide.createIcons();
  }
}

// Router and Navigation
function setupNavigation() {
  const links = document.querySelectorAll('.sidebar-link[data-view]');
  links.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const view = link.getAttribute('data-view');
      navigateTo(view);
    });
  });

  window.addEventListener('hashchange', () => {
    const hash = window.location.hash.replace('#', '');
    if (hash.startsWith('product-detail/')) {
      const pid = hash.split('/')[1];
      showProductDetails(pid);
    } else {
      navigateTo(hash || 'overview', false);
    }
  });
}

function navigateTo(viewName, updateHash = true) {
  if (viewName.startsWith('product-detail/')) {
    const pid = viewName.split('/')[1];
    showProductDetails(pid);
    return;
  }

  // Update sidebar active state
  document.querySelectorAll('.sidebar-link').forEach(link => {
    if (link.getAttribute('data-view') === viewName) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });

  // Switch view section
  document.querySelectorAll('.view-section').forEach(sec => {
    sec.classList.remove('active-view');
  });

  const targetView = document.getElementById(`view-${viewName}`);
  if (targetView) {
    targetView.classList.add('active-view');
  } else {
    document.getElementById('view-overview').classList.add('active-view');
    viewName = 'overview';
  }

  if (updateHash) {
    window.location.hash = `#${viewName}`;
  }

  // View specific loaders
  if (viewName === 'overview') {
    loadOverviewData();
  } else if (viewName === 'products') {
    loadProductsData();
  } else if (viewName === 'model-info') {
    loadModelInfoData();
  }

  if (window.lucide) {
    lucide.createIcons();
  }
}

// Backend Health Check
async function checkBackendHealth() {
  const indicator = document.getElementById('backend-status');
  try {
    const res = await api.getHealth();
    if (res.status === 'healthy') {
      indicator.innerHTML = '<span class="status-indicator"></span> ML Backend Connected';
      indicator.title = `ReviewLens v${res.version} • Scikit-learn Ready`;
    } else {
      indicator.innerHTML = '<span class="status-indicator" style="background:#f59e0b"></span> Degraded Backend';
    }
  } catch (err) {
    indicator.innerHTML = '<span class="status-indicator" style="background:#ef4444"></span> Backend Offline';
    showToast('Cannot connect to Flask backend. Ensure "python backend/app.py" is running on port 5000.', 'danger');
  }
}

// -------------------------------------------------------------
// 1. Overview Dashboard Loader
// -------------------------------------------------------------
async function loadOverviewData() {
  try {
    const [overviewRes, comparisonsRes] = await Promise.all([
      api.getOverview(),
      api.getProductComparisons()
    ]);

    const data = overviewRes.data;
    
    // KPI Cards
    document.getElementById('kpi-total-reviews').textContent = data.total_reviews || 0;
    document.getElementById('kpi-pos-pct').textContent = `${data.sentiment_percentages.positive}%`;
    document.getElementById('kpi-neg-pct').textContent = `${data.sentiment_percentages.negative}%`;
    document.getElementById('kpi-neu-pct').textContent = `${data.sentiment_percentages.neutral}%`;

    // Highlight Products
    if (data.best_product) {
      document.getElementById('best-product-name').textContent = data.best_product.name;
      document.getElementById('best-product-score').textContent = `${data.best_product.positive_pct}% Positive (${data.best_product.sentiment_score}/100 Score)`;
    }
    if (data.worst_product) {
      document.getElementById('worst-product-name').textContent = data.worst_product.name;
      document.getElementById('worst-product-score').textContent = `${data.worst_product.negative_pct}% Negative (${data.worst_product.sentiment_score}/100 Score)`;
    }

    // Charts
    charts.renderSentimentDoughnut('chart-overall-doughnut', data.sentiment_counts);
    charts.renderProductComparison('chart-product-comparison', comparisonsRes.data);

    // Recent Analyses list
    renderRecentAnalyses(data.recent_analyses);

  } catch (err) {
    console.error('Error loading overview data:', err);
  }
}

function renderRecentAnalyses(items) {
  const container = document.getElementById('recent-analyses-list');
  if (!container) return;

  if (!items || items.length === 0) {
    container.innerHTML = `
      <div class="text-center py-4 text-muted">
        <i data-lucide="inbox" class="mb-2" style="width:24px;height:24px;"></i>
        <p class="small mb-0">No live review analyses in this session yet.</p>
        <span class="text-xs text-light">Try analyzing a review in the Review Analyzer tool!</span>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
    return;
  }

  container.innerHTML = items.map(item => `
    <div class="d-flex align-items-center justify-content-between p-2 mb-2 rounded bg-light border">
      <div class="pe-2 text-truncate" style="max-width: 70%;">
        <div class="small fw-semibold text-truncate">${escapeHtml(item.text)}</div>
        <div class="text-xs text-muted">${item.analyzed_at || 'Just now'}</div>
      </div>
      <div class="text-end">
        <span class="badge-sentiment ${item.sentiment}">
          ${item.sentiment} (${item.confidence_pct}%)
        </span>
      </div>
    </div>
  `).join('');
}

// -------------------------------------------------------------
// 2. Product Catalog Loader
// -------------------------------------------------------------
async function loadProductsData() {
  const container = document.getElementById('products-grid');
  if (!container) return;

  container.innerHTML = `
    <div class="col-12 text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="mt-2 text-muted small">Loading product catalog and sentiment models...</p>
    </div>
  `;

  try {
    const res = await api.getProducts();
    const products = res.data;

    container.innerHTML = products.map(p => {
      const stats = p.stats;
      return `
        <div class="col-md-6 col-lg-4">
          <div class="product-card">
            <div class="product-img-box">
              <span class="product-category-tag">${p.category}</span>
              <img src="${p.image_url}" alt="${escapeHtml(p.name)}" class="product-img" onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\\'product-img-fallback\\'><i data-lucide=\\'package\\' style=\\'width:42px;height:42px;\\'></i></div>'; lucide.createIcons();">
            </div>
            <div class="product-content">
              <div class="d-flex justify-content-between align-items-start mb-1">
                <h3 class="product-name">${escapeHtml(p.name)}</h3>
                <span class="product-price">$${p.price.toFixed(2)}</span>
              </div>
              <p class="product-desc">${escapeHtml(p.description)}</p>
              
              <div class="mt-auto">
                <div class="d-flex justify-content-between align-items-center text-xs text-muted mb-1">
                  <span>Sentiment Score: <strong>${p.sentiment_score}/100</strong></span>
                  <span><strong>${p.review_count}</strong> Reviews</span>
                </div>
                
                <div class="sentiment-bar-split" title="Positive: ${stats.positive_pct}%, Neutral: ${stats.neutral_pct}%, Negative: ${stats.negative_pct}%">
                  <div class="sentiment-bar-pos" style="width: ${stats.positive_pct}%"></div>
                  <div class="sentiment-bar-neu" style="width: ${stats.neutral_pct}%"></div>
                  <div class="sentiment-bar-neg" style="width: ${stats.negative_pct}%"></div>
                </div>

                <div class="d-flex justify-content-between text-xs text-muted mt-1 mb-3">
                  <span class="text-success">${stats.positive_pct}% Pos</span>
                  <span class="text-warning">${stats.neutral_pct}% Neu</span>
                  <span class="text-danger">${stats.negative_pct}% Neg</span>
                </div>

                <button class="btn btn-outline-primary btn-sm w-100 fw-semibold" onclick="showProductDetails('${p.id}')">
                  <i data-lucide="bar-chart-2" style="width:14px;height:14px;" class="me-1"></i> View Reviews & Insights
                </button>
              </div>
            </div>
          </div>
        </div>
      `;
    }).join('');

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    container.innerHTML = `<div class="col-12 text-center text-danger py-4">Failed to load products: ${err.message}</div>`;
  }
}

// -------------------------------------------------------------
// 3. Product Details View Loader
// -------------------------------------------------------------
async function showProductDetails(productId) {
  currentProductId = productId;
  currentReviewFilter = 'all';
  window.location.hash = `#product-detail/${productId}`;

  document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active-view'));
  const detailSec = document.getElementById('view-product-detail');
  if (detailSec) detailSec.classList.add('active-view');

  try {
    const [prodRes, reviewsRes] = await Promise.all([
      api.getProduct(productId),
      api.getProductReviews(productId, 'all')
    ]);

    const p = prodRes.data;
    const reviews = reviewsRes.data;

    // Header info
    document.getElementById('detail-product-name').textContent = p.name;
    document.getElementById('detail-product-category').textContent = p.category;
    document.getElementById('detail-product-price').textContent = `$${p.price.toFixed(2)}`;
    document.getElementById('detail-product-desc').textContent = p.description;
    document.getElementById('detail-summary-text').textContent = p.summary_text;

    // Features
    const featBox = document.getElementById('detail-product-features');
    if (featBox && p.features) {
      featBox.innerHTML = p.features.map(f => `<span class="badge bg-light text-dark border me-1 mb-1">${escapeHtml(f)}</span>`).join('');
    }

    // Keyword chips
    const posKwBox = document.getElementById('detail-positive-keywords');
    if (posKwBox) {
      posKwBox.innerHTML = p.top_positive_keywords.length > 0 
        ? p.top_positive_keywords.map(kw => `<span class="keyword-badge bg-emerald-light text-success border-success me-1 mb-1">+ ${escapeHtml(kw)}</span>`).join('')
        : '<span class="text-muted text-xs">No distinctive terms</span>';
    }

    const negKwBox = document.getElementById('detail-negative-keywords');
    if (negKwBox) {
      negKwBox.innerHTML = p.top_negative_keywords.length > 0
        ? p.top_negative_keywords.map(kw => `<span class="keyword-badge bg-rose-light text-danger border-danger me-1 mb-1">- ${escapeHtml(kw)}</span>`).join('')
        : '<span class="text-muted text-xs">No distinctive terms</span>';
    }

    // Chart
    charts.renderProductDetailDoughnut('chart-detail-doughnut', p.stats);

    // Reviews List
    renderReviewsList(reviews);

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    showToast(`Error opening product: ${err.message}`, 'danger');
  }
}

window.filterProductReviews = async function(filter) {
  currentReviewFilter = filter;
  document.querySelectorAll('.filter-pill').forEach(btn => {
    if (btn.getAttribute('data-filter') === filter) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  try {
    const res = await api.getProductReviews(currentProductId, filter);
    renderReviewsList(res.data);
  } catch (err) {
    showToast(`Error filtering reviews: ${err.message}`, 'danger');
  }
};

function renderReviewsList(reviews) {
  const container = document.getElementById('product-reviews-container');
  if (!container) return;

  if (!reviews || reviews.length === 0) {
    container.innerHTML = `
      <div class="text-center py-5 text-muted">
        <i data-lucide="message-square-off" style="width:32px;height:32px;" class="mb-2"></i>
        <p class="small mb-0">No sample reviews found matching filter '${currentReviewFilter}'.</p>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
    return;
  }

  container.innerHTML = reviews.map(r => {
    const stars = '★'.repeat(r.rating || 4) + '☆'.repeat(5 - (r.rating || 4));
    const keywords = (r.keywords || []).map(k => `<span class="badge bg-light text-muted border text-xs me-1">${escapeHtml(k)}</span>`).join('');
    return `
      <div class="review-item">
        <div class="review-header">
          <div>
            <span class="reviewer-name">${escapeHtml(r.author || 'Verified Customer')}</span>
            <span class="star-rating ms-2">${stars}</span>
            <span class="review-date ms-2">${r.date || 'Sample Review'}</span>
          </div>
          <span class="badge-sentiment ${r.predicted_sentiment}">
            ${r.predicted_sentiment} (${r.confidence_pct}%)
          </span>
        </div>
        <p class="review-text">${escapeHtml(r.text)}</p>
        ${keywords ? `<div class="mt-2">${keywords}</div>` : ''}
      </div>
    `;
  }).join('');
}

// -------------------------------------------------------------
// 4. Interactive Review Analyzer
// -------------------------------------------------------------
function setupAnalyzer() {
  const textarea = document.getElementById('analyzer-input');
  const charCounter = document.getElementById('analyzer-char-count');
  const btnAnalyze = document.getElementById('btn-analyze-review');
  const btnClear = document.getElementById('btn-clear-review');

  if (textarea && charCounter) {
    textarea.addEventListener('input', () => {
      charCounter.textContent = `${textarea.value.length} / 4000 characters`;
    });
  }

  if (btnAnalyze) {
    btnAnalyze.addEventListener('click', () => {
      const text = textarea.value.trim();
      if (!text) {
        showToast('Please enter or select a customer review to analyze.', 'warning');
        textarea.focus();
        return;
      }
      runAnalysis(text);
    });
  }

  if (btnClear) {
    btnClear.addEventListener('click', () => {
      textarea.value = '';
      if (charCounter) charCounter.textContent = '0 / 4000 characters';
      document.getElementById('analyzer-result-card').style.display = 'none';
      document.getElementById('analyzer-empty-placeholder').style.display = 'block';
    });
  }

  // Clickable example reviews
  document.querySelectorAll('.example-chip-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const exampleText = btn.getAttribute('data-text');
      textarea.value = exampleText;
      if (charCounter) charCounter.textContent = `${exampleText.length} / 4000 characters`;
      runAnalysis(exampleText);
    });
  });
}

async function runAnalysis(text) {
  const btnAnalyze = document.getElementById('btn-analyze-review');
  const spinner = document.getElementById('analyzer-spinner');
  const resultCard = document.getElementById('analyzer-result-card');
  const placeholder = document.getElementById('analyzer-empty-placeholder');

  if (btnAnalyze) btnAnalyze.disabled = true;
  if (spinner) spinner.style.display = 'inline-block';

  try {
    const res = await api.analyzeReview(text);
    const pred = res.data;

    // Hide placeholder, show card
    placeholder.style.display = 'none';
    resultCard.style.display = 'block';

    // Populate sentiment badge
    const badge = document.getElementById('res-sentiment-badge');
    badge.className = `badge-sentiment ${pred.sentiment} fs-6 py-2 px-3`;
    badge.innerHTML = `<i data-lucide="${getSentimentIcon(pred.sentiment)}" style="width:18px;height:18px;"></i> ${pred.sentiment.toUpperCase()}`;

    // Confidence
    document.getElementById('res-confidence-pct').textContent = `${pred.confidence_pct}%`;
    document.getElementById('res-confidence-level').textContent = `${pred.confidence_level} Confidence`;

    // Probability Bars
    const probs = pred.probabilities;
    const posPct = ((probs.positive || 0) * 100).toFixed(1);
    const neuPct = ((probs.neutral || 0) * 100).toFixed(1);
    const negPct = ((probs.negative || 0) * 100).toFixed(1);

    document.getElementById('res-bar-pos').style.width = `${posPct}%`;
    document.getElementById('res-val-pos').textContent = `${posPct}%`;
    document.getElementById('res-bar-neu').style.width = `${neuPct}%`;
    document.getElementById('res-val-neu').textContent = `${neuPct}%`;
    document.getElementById('res-bar-neg').style.width = `${negPct}%`;
    document.getElementById('res-val-neg').textContent = `${negPct}%`;

    // Keywords chips
    const kwBox = document.getElementById('res-keywords-box');
    if (pred.keywords && pred.keywords.length > 0) {
      kwBox.innerHTML = pred.keywords.map(kw => `
        <span class="keyword-badge">
          <i data-lucide="tag" style="width:12px;height:12px;"></i> ${escapeHtml(kw)}
        </span>
      `).join('');
    } else {
      kwBox.innerHTML = '<span class="text-muted text-xs">No distinctive n-gram tokens extracted</span>';
    }

    // Explanation
    document.getElementById('res-explanation').textContent = pred.explanation;
    document.getElementById('res-model-id').textContent = pred.model_identifier;

    if (window.lucide) lucide.createIcons();

  } catch (err) {
    showToast(`Analysis failed: ${err.message}`, 'danger');
  } finally {
    if (btnAnalyze) btnAnalyze.disabled = false;
    if (spinner) spinner.style.display = 'none';
  }
}

function getSentimentIcon(sentiment) {
  if (sentiment === 'positive') return 'smile';
  if (sentiment === 'negative') return 'frown';
  return 'meh';
}

// -------------------------------------------------------------
// 5. Model Information View Loader
// -------------------------------------------------------------
async function loadModelInfoData() {
  try {
    const res = await api.getModelInfo();
    const data = res.data;
    const m = data.metrics;

    if (m && m.accuracy_pct) {
      document.getElementById('model-accuracy-kpi').textContent = `${m.accuracy_pct}%`;
      document.getElementById('model-vocab-size').textContent = `${m.vocabulary_size} n-grams`;
      document.getElementById('model-train-samples').textContent = `${m.train_samples} samples`;
      document.getElementById('model-test-samples').textContent = `${m.test_samples} samples`;

      // Classification Report Table
      const rep = m.classification_report;
      const tableBody = document.getElementById('metrics-table-body');
      if (tableBody && rep) {
        const rows = ['positive', 'neutral', 'negative'].map(cls => {
          const item = rep[cls] || {};
          return `
            <tr>
              <td class="fw-semibold text-capitalize">${cls}</td>
              <td>${((item.precision || 0) * 100).toFixed(1)}%</td>
              <td>${((item.recall || 0) * 100).toFixed(1)}%</td>
              <td>${((item['f1-score'] || 0) * 100).toFixed(1)}%</td>
              <td>${item.support || 0}</td>
            </tr>
          `;
        }).join('');
        tableBody.innerHTML = rows;
      }

      // Confusion Matrix Visualizer
      renderConfusionMatrix(m.confusion_matrix);
    }
  } catch (err) {
    console.error('Error loading model info:', err);
  }
}

function renderConfusionMatrix(cmData) {
  const container = document.getElementById('confusion-matrix-box');
  if (!container || !cmData) return;

  const { labels, matrix } = cmData;
  let html = `
    <table class="table table-bordered text-center align-middle mb-0" style="font-size:0.85rem;">
      <thead class="bg-light">
        <tr>
          <th rowspan="2" class="align-middle">Actual Label</th>
          <th colspan="${labels.length}">Predicted Label</th>
        </tr>
        <tr>
          ${labels.map(l => `<th class="text-capitalize">${l}</th>`).join('')}
        </tr>
      </thead>
      <tbody>
  `;

  matrix.forEach((row, i) => {
    html += `<tr><th class="bg-light text-capitalize">${labels[i]}</th>`;
    row.forEach((val, j) => {
      const isDiagonal = i === j;
      const bg = isDiagonal ? 'rgba(16, 185, 129, 0.15)' : (val > 0 ? 'rgba(239, 68, 68, 0.08)' : '#ffffff');
      const textStyle = isDiagonal ? 'text-success fw-bold' : 'text-muted';
      html += `<td style="background:${bg}" class="${textStyle}">${val}</td>`;
    });
    html += `</tr>`;
  });

  html += `</tbody></table>`;
  container.innerHTML = html;
}

// -------------------------------------------------------------
// Utilities
// -------------------------------------------------------------
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function showToast(message, type = 'info') {
  const toastBox = document.getElementById('toast-container');
  if (!toastBox) return;

  const toastEl = document.createElement('div');
  toastEl.className = `alert alert-${type} shadow-sm d-flex align-items-center mb-2 alert-dismissible fade show`;
  toastEl.role = 'alert';
  toastEl.style.fontSize = '0.85rem';
  toastEl.innerHTML = `
    <div class="flex-grow-1">${escapeHtml(message)}</div>
    <button type="button" class="btn-close ms-2" data-bs-dismiss="alert" aria-label="Close"></button>
  `;

  toastBox.appendChild(toastEl);
  setTimeout(() => {
    toastEl.classList.remove('show');
    setTimeout(() => toastEl.remove(), 200);
  }, 4500);
}

window.showProductDetails = showProductDetails;
window.navigateTo = navigateTo;
