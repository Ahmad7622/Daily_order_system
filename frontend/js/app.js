/**
 * Daily Customer Order Reporting System - Frontend App Logic
 */

const API_BASE_URL = '/api';

const PRODUCT_PRICES = {
    "Plain Shine": 2050,
    "Needle Texture": 2050,
    "Crocodile Texture": 2050,
    "Snake Texture": 2050,
    "Softy Grain Leather": 2099
};

// Global App State
let currentOrdersList = [];
let deleteTargetOrderId = null;

// DOM Elements
document.addEventListener('DOMContentLoaded', () => {
    initDateDefaults();
    initNavigation();
    initProductDropdownAutoAmount();
    initOrderFormSubmit();
    initFilterEvents();
    initReportEvents();
    initModalEvents();

    // Initial Data Fetch
    loadDashboardStats();
    loadOrdersTable();
});

/**
 * Initialize today's date defaults in pickers and topbar header
 */
function initDateDefaults() {
    const today = new Date();
    const dateStr = today.toISOString().split('T')[0]; // YYYY-MM-DD

    // Options for formatted date display
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('current-date-display').textContent = today.toLocaleDateString('en-GB', options);

    // Default dates in forms
    document.getElementById('dash-date-picker').value = dateStr;
    document.getElementById('order-date').value = dateStr;
    document.getElementById('daily-report-date').value = dateStr;

    // Weekly range: last 7 days
    const past7 = new Date();
    past7.setDate(today.getDate() - 6);
    document.getElementById('weekly-start-date').value = past7.toISOString().split('T')[0];
    document.getElementById('weekly-end-date').value = dateStr;
}

/**
 * Handle sidebar page switching
 */
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const pageViews = document.querySelectorAll('.page-view');
    const pageTitle = document.getElementById('page-title');

    const titles = {
        'dashboard': 'Dashboard',
        'orders': 'Orders Management',
        'daily-report': 'Daily PDF Report',
        'weekly-report': 'Weekly PDF Report'
    };

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetPage = item.getAttribute('data-page');

            navItems.forEach(n => n.classList.remove('active'));
            pageViews.forEach(v => v.classList.remove('active'));

            item.classList.add('active');
            const targetView = document.getElementById(`page-${targetPage}`);
            if (targetView) targetView.classList.add('active');

            if (pageTitle && titles[targetPage]) {
                pageTitle.textContent = titles[targetPage];
            }

            // Refresh page-specific data
            if (targetPage === 'dashboard') {
                loadDashboardStats();
            } else if (targetPage === 'orders') {
                loadOrdersTable();
            } else if (targetPage === 'daily-report') {
                loadDailyReportSummary();
            } else if (targetPage === 'weekly-report') {
                loadWeeklyReportSummary();
            }
        });
    });
}

/**
 * CRITICAL FEATURE: Product Dropdown Selection Auto-fills Price Amount
 */
function initProductDropdownAutoAmount() {
    const productSelect = document.getElementById('product-select');
    const amountInput = document.getElementById('product-amount');

    productSelect.addEventListener('change', (e) => {
        const selectedProduct = e.target.value;
        if (selectedProduct && PRODUCT_PRICES[selectedProduct]) {
            const price = PRODUCT_PRICES[selectedProduct];
            amountInput.value = `Rs. ${price.toLocaleString()}`;
        } else {
            amountInput.value = '';
        }
    });
}

/**
 * Dashboard Overview Data Fetcher
 */
async function loadDashboardStats() {
    const selectedDate = document.getElementById('dash-date-picker').value;
    try {
        const response = await fetch(`${API_BASE_URL}/stats/daily?date=${selectedDate}`);
        if (!response.ok) throw new Error(`HTTP Error ${response.status}`);

        const data = await response.json();

        document.getElementById('dash-total-orders').textContent = data.total_orders || 0;
        document.getElementById('dash-verified-orders').textContent = data.verified || 0;
        document.getElementById('dash-pending-orders').textContent = data.pending || 0;
        document.getElementById('dash-rejected-orders').textContent = data.rejected || 0;
        document.getElementById('dash-total-sales').textContent = `Rs. ${(data.total_sales || 0).toLocaleString()}`;

        renderTableRows('dash-recent-orders-tbody', data.orders || [], false);
    } catch (err) {
        showToast(`Failed to load dashboard stats: ${err.message}`, 'error');
    }
}

/**
 * Orders Page Data Fetcher with Search & Filters
 */
async function loadOrdersTable() {
    const searchVal = document.getElementById('order-search-input').value.trim();
    const dateVal = document.getElementById('order-date-filter').value;
    const statusVal = document.getElementById('order-status-filter').value;

    let url = `${API_BASE_URL}/orders?`;
    const params = new URLSearchParams();
    if (searchVal) params.append('search', searchVal);
    if (dateVal) params.append('order_date', dateVal);
    if (statusVal && statusVal !== 'All') params.append('status', statusVal);

    url += params.toString();

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP Error ${response.status}`);

        const orders = await response.json();
        currentOrdersList = orders;
        renderTableRows('orders-table-tbody', orders, true);
    } catch (err) {
        showToast(`Failed to load orders: ${err.message}`, 'error');
    }
}

/**
 * Render Orders Table Rows
 */
function renderTableRows(containerId, orders, includeActions = true) {
    const tbody = document.getElementById(containerId);
    if (!tbody) return;

    if (!orders || orders.length === 0) {
        const colCount = includeActions ? 10 : 8;
        tbody.innerHTML = `<tr><td colspan="${colCount}" class="text-center text-muted">No orders found.</td></tr>`;
        return;
    }

    tbody.innerHTML = orders.map(o => {
        const formattedId = `#${String(o.id).padStart(3, '0')}`;
        const amountFormatted = `Rs. ${Number(o.amount).toLocaleString()}`;
        const badgeClass = o.status === 'Verified' ? 'badge-verified' : (o.status === 'Pending' ? 'badge-pending' : 'badge-rejected');

        return `
            <tr>
                <td><strong>${formattedId}</strong></td>
                <td>${escapeHtml(o.customer_name)}</td>
                <td>${escapeHtml(o.phone)}</td>
                <td><code>${escapeHtml(o.tracking_id)}</code></td>
                <td><span class="badge" style="background:#e2e8f0; color:#334155;">${escapeHtml(o.product_code)}</span></td>
                <td>${escapeHtml(o.product_name)}</td>
                <td><strong>${amountFormatted}</strong></td>
                <td><span class="badge ${badgeClass}">${o.status}</span></td>
                ${includeActions ? `<td>${o.order_date}</td>` : ''}
                ${includeActions ? `
                    <td>
                        <button class="btn btn-secondary btn-sm" onclick="openEditOrderModal(${o.id})">
                            <i class="fa-solid fa-pen-to-square"></i> Edit
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="promptDeleteOrder(${o.id})">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </td>
                ` : ''}
            </tr>
        `;
    }).join('');
}

/**
 * Handle Order Form Submit (Add & Edit)
 */
function initOrderFormSubmit() {
    const orderForm = document.getElementById('order-form');
    orderForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const orderId = document.getElementById('form-order-id').value;
        const pName = document.getElementById('product-select').value;

        if (!PRODUCT_PRICES[pName]) {
            showToast('Please select a valid product.', 'error');
            return;
        }

        const payload = {
            customer_name: document.getElementById('customer-name').value.trim(),
            phone: document.getElementById('phone-number').value.trim(),
            tracking_id: document.getElementById('tracking-id').value.trim(),
            product_code: document.getElementById('product-code').value.trim(),
            product_name: pName,
            order_date: document.getElementById('order-date').value,
            status: document.getElementById('order-status').value
        };

        try {
            let response;
            if (orderId) {
                // Update Order
                response = await fetch(`${API_BASE_URL}/orders/${orderId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            } else {
                // Add New Order
                response = await fetch(`${API_BASE_URL}/orders`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            }

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to save order');
            }

            showToast('Order saved successfully.', 'success');
            closeOrderModal();

            // Refresh tables and dashboard
            loadDashboardStats();
            loadOrdersTable();

        } catch (err) {
            showToast(`Error: ${err.message}`, 'error');
        }
    });
}

/**
 * Modal Handling Logic
 */
function initModalEvents() {
    document.getElementById('open-add-modal-btn').addEventListener('click', openAddOrderModal);
    document.getElementById('close-modal-btn').addEventListener('click', closeOrderModal);
    document.getElementById('cancel-modal-btn').addEventListener('click', closeOrderModal);

    document.getElementById('close-delete-modal-btn').addEventListener('click', closeDeleteModal);
    document.getElementById('cancel-delete-btn').addEventListener('click', closeDeleteModal);
    document.getElementById('confirm-delete-btn').addEventListener('click', executeDeleteOrder);

    document.getElementById('dash-refresh-btn').addEventListener('click', loadDashboardStats);
    document.getElementById('dash-date-picker').addEventListener('change', loadDashboardStats);
}

function openAddOrderModal() {
    document.getElementById('order-form').reset();
    document.getElementById('form-order-id').value = '';
    document.getElementById('modal-title').innerHTML = '<i class="fa-solid fa-cart-plus"></i> Add New Order';
    document.getElementById('order-date').value = new Date().toISOString().split('T')[0];
    document.getElementById('product-amount').value = '';
    document.getElementById('order-modal').classList.add('show');
}

window.openEditOrderModal = function(id) {
    const order = currentOrdersList.find(o => o.id === id);
    if (!order) return;

    document.getElementById('form-order-id').value = order.id;
    document.getElementById('customer-name').value = order.customer_name;
    document.getElementById('phone-number').value = order.phone;
    document.getElementById('tracking-id').value = order.tracking_id;
    document.getElementById('product-code').value = order.product_code;
    document.getElementById('product-select').value = order.product_name;
    document.getElementById('product-amount').value = `Rs. ${Number(order.amount).toLocaleString()}`;
    document.getElementById('order-date').value = order.order_date;
    document.getElementById('order-status').value = order.status;

    document.getElementById('modal-title').innerHTML = `<i class="fa-solid fa-pen-to-square"></i> Edit Order #${String(id).padStart(3, '0')}`;
    document.getElementById('order-modal').classList.add('show');
};

function closeOrderModal() {
    document.getElementById('order-modal').classList.remove('show');
}

window.promptDeleteOrder = function(id) {
    deleteTargetOrderId = id;
    document.getElementById('delete-order-label').textContent = `#${String(id).padStart(3, '0')}`;
    document.getElementById('delete-modal').classList.add('show');
};

function closeDeleteModal() {
    deleteTargetOrderId = null;
    document.getElementById('delete-modal').classList.remove('show');
}

async function executeDeleteOrder() {
    if (!deleteTargetOrderId) return;
    try {
        const response = await fetch(`${API_BASE_URL}/orders/${deleteTargetOrderId}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete order');

        showToast('Order deleted successfully.', 'success');
        closeDeleteModal();
        loadDashboardStats();
        loadOrdersTable();
    } catch (err) {
        showToast(`Delete Error: ${err.message}`, 'error');
    }
}

/**
 * Filter Events for Orders View
 */
function initFilterEvents() {
    const searchInput = document.getElementById('order-search-input');
    const dateInput = document.getElementById('order-date-filter');
    const statusSelect = document.getElementById('order-status-filter');
    const resetBtn = document.getElementById('reset-filters-btn');

    let debounceTimer;
    searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(loadOrdersTable, 300);
    });

    dateInput.addEventListener('change', loadOrdersTable);
    statusSelect.addEventListener('change', loadOrdersTable);

    resetBtn.addEventListener('click', () => {
        searchInput.value = '';
        dateInput.value = '';
        statusSelect.value = 'All';
        loadOrdersTable();
    });
}

/**
 * Daily & Weekly PDF Report Loaders & Downloader Setup
 */
function initReportEvents() {
    document.getElementById('load-daily-report-btn').addEventListener('click', loadDailyReportSummary);
    document.getElementById('download-daily-pdf-btn').addEventListener('click', downloadDailyPDF);

    document.getElementById('load-weekly-report-btn').addEventListener('click', loadWeeklyReportSummary);
    document.getElementById('download-weekly-pdf-btn').addEventListener('click', downloadWeeklyPDF);
}

async function loadDailyReportSummary() {
    const dateVal = document.getElementById('daily-report-date').value;
    if (!dateVal) return;

    try {
        const response = await fetch(`${API_BASE_URL}/stats/daily?date=${dateVal}`);
        if (!response.ok) throw new Error('Failed to load daily stats');

        const data = await response.json();
        document.getElementById('daily-rep-total').textContent = data.total_orders;
        document.getElementById('daily-rep-verified').textContent = data.verified;
        document.getElementById('daily-rep-pending').textContent = data.pending;
        document.getElementById('daily-rep-rejected').textContent = data.rejected;
        document.getElementById('daily-rep-sales').textContent = `Rs. ${(data.total_sales || 0).toLocaleString()}`;

        renderTableRows('daily-report-tbody', data.orders || [], false);
    } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
    }
}

async function downloadDailyPDF() {
    const dateVal = document.getElementById('daily-report-date').value;
    if (!dateVal) {
        showToast('Please select a date for the report', 'error');
        return;
    }

    try {
        showToast('Generating Daily PDF...', 'info');
        const pdfUrl = `${API_BASE_URL}/reports/daily?date=${dateVal}`;
        triggerFileDownload(pdfUrl, `Daily_Order_Report_${dateVal}.pdf`);
    } catch (err) {
        showToast(`PDF Download Error: ${err.message}`, 'error');
    }
}

async function loadWeeklyReportSummary() {
    const startVal = document.getElementById('weekly-start-date').value;
    const endVal = document.getElementById('weekly-end-date').value;

    if (!startVal || !endVal) {
        showToast('Please select start and end dates', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/stats/weekly?start_date=${startVal}&end_date=${endVal}`);
        if (!response.ok) throw new Error('Failed to load weekly stats');

        const data = await response.json();
        document.getElementById('weekly-rep-total').textContent = data.total_orders;
        document.getElementById('weekly-rep-verified').textContent = data.verified;
        document.getElementById('weekly-rep-pending').textContent = data.pending;
        document.getElementById('weekly-rep-rejected').textContent = data.rejected;
        document.getElementById('weekly-rep-sales').textContent = `Rs. ${(data.total_sales || 0).toLocaleString()}`;

        // Render Breakdown Table
        const tbody = document.getElementById('weekly-breakdown-tbody');
        const breakdown = data.daily_breakdown || [];

        if (breakdown.length === 0) {
            tbody.innerHTML = `<tr><td colspan="3" class="text-center text-muted">No orders found in date range.</td></tr>`;
        } else {
            tbody.innerHTML = breakdown.map(b => `
                <tr>
                    <td><strong>${b.date}</strong></td>
                    <td>${b.orders} orders</td>
                    <td><strong>Rs. ${Number(b.sales).toLocaleString()}</strong></td>
                </tr>
            `).join('');
        }
    } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
    }
}

async function downloadWeeklyPDF() {
    const startVal = document.getElementById('weekly-start-date').value;
    const endVal = document.getElementById('weekly-end-date').value;

    if (!startVal || !endVal) {
        showToast('Please select start and end dates', 'error');
        return;
    }

    try {
        showToast('Generating Weekly PDF...', 'info');
        const pdfUrl = `${API_BASE_URL}/reports/weekly?start_date=${startVal}&end_date=${endVal}`;
        triggerFileDownload(pdfUrl, `Weekly_Order_Report_${startVal}_to_${endVal}.pdf`);
    } catch (err) {
        showToast(`PDF Download Error: ${err.message}`, 'error');
    }
}

/**
 * Trigger File Download via Browser Fetch & Blob
 */
async function triggerFileDownload(url, filename) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Server returned status ${res.status}`);
    const blob = await res.blob();
    const blobUrl = window.URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(blobUrl);
}

/**
 * Toast Notification Utility
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icon = type === 'success' ? 'fa-circle-check' : (type === 'error' ? 'fa-circle-xmark' : 'fa-circle-info');
    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${escapeHtml(message)}</span>`;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(30px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
