/**
 * polling.js — Asynchronous polling for order status updates.
 *
 * Polls /orders/<id>/status every 5 seconds and updates the status badge
 * in real-time whenever the order status changes.
 */
function pollOrderStatus(orderId, currentStatus) {
    const statusUrl = `/orders/${orderId}/status`;
    const statusBadge = document.getElementById('order-status-badge');
    const pollingIndicator = document.getElementById('polling-indicator');

    const statusColors = {
        'pending':    'warning',
        'processing': 'info',
        'shipped':    'primary',
        'delivered':  'success',
        'cancelled':  'danger',
    };

    let lastStatus = currentStatus;
    let pollInterval;

    function checkStatus() {
        fetch(statusUrl)
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.json();
            })
            .then(data => {
                if (data.status !== lastStatus) {
                    lastStatus = data.status;

                    // Update badge class and text
                    const color = statusColors[data.status] || 'secondary';
                    statusBadge.className = `badge bg-${color} fs-6 ms-1`;
                    statusBadge.textContent =
                        data.status.charAt(0).toUpperCase() + data.status.slice(1);

                    showStatusNotification(data.status);

                    // Stop polling once the order reaches a terminal state
                    if (data.status === 'delivered' || data.status === 'cancelled') {
                        clearInterval(pollInterval);
                        if (pollingIndicator) {
                            pollingIndicator.innerHTML =
                                '<span class="badge bg-secondary fs-6">Polling Stopped (Final State)</span>' +
                                '<p class="text-muted small mt-2 mb-0">Order has reached its final status</p>';
                        }
                    }
                }
            })
            .catch(error => console.error('Polling error:', error));
    }

    function showStatusNotification(status) {
        const notifContainer = document.getElementById('status-notifications');
        if (!notifContainer) return;

        const alert = document.createElement('div');
        alert.className = 'alert alert-info alert-dismissible fade show';
        alert.innerHTML = `
            <strong>Status Updated!</strong>
            Your order status changed to: <strong>${status.charAt(0).toUpperCase() + status.slice(1)}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        notifContainer.prepend(alert);

        // Auto-dismiss after 8 seconds
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 300);
        }, 8000);
    }

    // Start polling every 5 seconds
    pollInterval = setInterval(checkStatus, 5000);

    return pollInterval;
}
