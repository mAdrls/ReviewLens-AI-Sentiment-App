// ReviewLens AI - API Client
const API_BASE = (function() {
  if (window.location.protocol.startsWith('http')) {
    // When served via Flask or localhost dev server
    return `${window.location.origin}/api`;
  }
  // Fallback for direct local file opening (file://)
  return 'http://127.0.0.1:5000/api';
})();

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errMsg = (data && data.error) ? data.error : `HTTP error ${response.status}: ${response.statusText}`;
      throw new Error(errMsg);
    }

    return data;
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

const api = {
  getHealth: () => request('/health'),
  getOverview: () => request('/analytics/overview'),
  getProductComparisons: () => request('/analytics/products'),
  getProducts: () => request('/products'),
  getProduct: (id) => request(`/products/${encodeURIComponent(id)}`),
  getProductReviews: (id, sentiment) => {
    const q = sentiment && sentiment !== 'all' ? `?sentiment=${encodeURIComponent(sentiment)}` : '';
    return request(`/products/${encodeURIComponent(id)}/reviews${q}`);
  },
  analyzeReview: (reviewText) => request('/analyze', {
    method: 'POST',
    body: JSON.stringify({ review: reviewText })
  }),
  getModelInfo: () => request('/model/info'),
  getSessionHistory: () => request('/history')
};

window.api = api;
