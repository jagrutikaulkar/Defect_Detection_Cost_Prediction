/* Analytics JavaScript */

// Store chart instances
let defectChartInstance = null;
let severityChartInstance = null;

// Load analytics data
async function loadAnalyticsData() {
    try {
        const response = await fetch('/api/defect/history', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'success' && data.data && data.data.length > 0) {
            // Process detections into analytics format
            const analytics = processDetectionsData(data.data);
            updateAnalyticsCharts(analytics);
            updateAnalyticsStats(analytics);
        } else {
            // Show empty state
            showEmptyAnalytics();
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// Update analytics charts
function updateAnalyticsCharts(data) {
    // Defect distribution chart
    const defectChartElement = document.getElementById('defectChart');
    if (defectChartElement) {
        const ctx = defectChartElement.getContext('2d');
        
        if (defectChartInstance) {
            defectChartInstance.destroy();
        }
        
        const labels = Object.keys(data.defect_distribution || {});
        const values = Object.values(data.defect_distribution || {});
        
        defectChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels.length > 0 ? labels : ['No data'],
                datasets: [{
                    data: values.length > 0 ? values : [0],
                    backgroundColor: [
                        '#3b82f6',
                        '#8b5cf6',
                        '#10b981',
                        '#f59e0b',
                        '#ef4444',
                        '#06b6d4'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    // Severity distribution chart
    const severityChartElement = document.getElementById('severityChart');
    if (severityChartElement) {
        const ctx = severityChartElement.getContext('2d');
        
        if (severityChartInstance) {
            severityChartInstance.destroy();
        }
        
        const severity_dist = data.severity_distribution || { high: 0, medium: 0, low: 0 };
        
        severityChartInstance = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['High', 'Medium', 'Low'],
                datasets: [{
                    data: [severity_dist.high, severity_dist.medium, severity_dist.low],
                    backgroundColor: ['#ef4444', '#f59e0b', '#10b981']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// Update analytics stats
function updateAnalyticsStats(data) {
    const totalStatsElement = document.getElementById('totalStats');
    if (totalStatsElement) {
        totalStatsElement.textContent = data.total_detections || 0;
    }
    
    const avgConfidenceElement = document.getElementById('avgConfidenceStats');
    if (avgConfidenceElement) {
        avgConfidenceElement.textContent = data.avg_confidence ? data.avg_confidence.toFixed(1) + '%' : '0%';
    }
}

// Process raw detections into analytics format
function processDetectionsData(detections) {
    const defect_distribution = {};
    const severity_distribution = { high: 0, medium: 0, low: 0 };
    let total_confidence = 0;
    
    detections.forEach(detection => {
        // Count defects by type
        const defect_type = detection.defect_type || 'Unknown';
        defect_distribution[defect_type] = (defect_distribution[defect_type] || 0) + 1;
        
        // Count severity
        if (detection.severity) {
            severity_distribution[detection.severity]++;
        }
        
        // Sum confidence
        total_confidence += detection.confidence || 0;
    });
    
    return {
        total_detections: detections.length,
        avg_confidence: detections.length > 0 ? total_confidence / detections.length : 0,
        defect_distribution,
        severity_distribution
    };
}

// Show empty state
function showEmptyAnalytics() {
    document.getElementById('totalStats').textContent = '0';
    document.getElementById('avgConfidenceStats').textContent = '0%';
    
    const defectChartElement = document.getElementById('defectChart');
    if (defectChartElement) {
        const ctx = defectChartElement.getContext('2d');
        if (defectChartInstance) defectChartInstance.destroy();
        defectChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['No Data'],
                datasets: [{
                    data: [1],
                    backgroundColor: ['#e5e7eb']
                }]
            }
        });
    }
    
    const severityChartElement = document.getElementById('severityChart');
    if (severityChartElement) {
        const ctx = severityChartElement.getContext('2d');
        if (severityChartInstance) severityChartInstance.destroy();
        severityChartInstance = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['High', 'Medium', 'Low'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ['#e5e7eb', '#e5e7eb', '#e5e7eb']
                }]
            }
        });
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('defectChart')) {
        loadAnalyticsData();
        
        // Refresh every 60 seconds
        setInterval(loadAnalyticsData, 60000);
    }
});
