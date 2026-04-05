/* Analytics JavaScript */

// Store chart instances
let defectChartInstance = null;
let severityChartInstance = null;
let categoriesChartInstance = null;

// Load analytics data
async function loadAnalyticsData() {
    try {
        console.log('Loading analytics data...');
        const token = localStorage.getItem('token');
        if (!token) {
            console.error('No token found');
            return;
        }
        
        const response = await fetch('/api/defect/history', {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('API Response:', data);
        
        if (data.status === 'success' && data.data && data.data.length > 0) {
            console.log('Processing', data.data.length, 'detections');
            // Process detections into analytics format
            const analytics = processDetectionsData(data.data);
            console.log('Processed analytics:', analytics);
            updateAnalyticsCharts(analytics);
            updateAnalyticsStats(analytics);
            updateRecentDetectionsTable(analytics.recent_detections);
        } else if (data.status === 'success') {
            console.log('No data received from API');
            showEmptyAnalytics();
        } else {
            console.error('API returned error:', data);
            showEmptyAnalytics();
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
        showEmptyAnalytics();
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
                    ],
                    borderColor: 'white',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: { size: 12, weight: 500 },
                            padding: 15
                        }
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
        
        const severity_dist = data.severity_distribution || { high: 0, medium: 0, low: 0, normal: 0 };
        
        severityChartInstance = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['High', 'Medium', 'Low', 'Normal'],
                datasets: [{
                    data: [severity_dist.high, severity_dist.medium, severity_dist.low, severity_dist.normal],
                    backgroundColor: ['#dc2626', '#f59e0b', '#10b981', '#3b82f6'],
                    borderColor: 'white',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: { size: 12, weight: 500 },
                            padding: 15
                        }
                    }
                }
            }
        });
    }
    
    // Categories chart (actual defect types)
    createCategoriesChart(data);
}

// Create categories chart
function createCategoriesChart(data) {
    const categoriesChartElement = document.getElementById('categoriesChart');
    if (!categoriesChartElement) return;
    
    const ctx = categoriesChartElement.getContext('2d');
    if (categoriesChartInstance) categoriesChartInstance.destroy();
    
    const defects = Object.keys(data.defect_distribution || {});
    const counts = Object.values(data.defect_distribution || {});
    
    categoriesChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: defects.length > 0 ? defects : ['No data'],
            datasets: [{
                label: 'Count',
                data: counts.length > 0 ? counts : [0],
                backgroundColor: '#8b5cf6',
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// Update analytics statistics
function updateAnalyticsStats(data) {
    const totalStatsElement = document.getElementById('totalStats');
    if (totalStatsElement) {
        totalStatsElement.textContent = data.total_detections || 0;
    }
    
    const avgConfidenceElement = document.getElementById('avgConfidenceStats');
    if (avgConfidenceElement) {
        avgConfidenceElement.textContent = data.avg_confidence ? data.avg_confidence.toFixed(1) + '%' : '0%';
    }
    
    // Calculate additional metrics
    const severity_dist = data.severity_distribution || { high: 0, medium: 0, low: 0, normal: 0 };
    const total_defects = severity_dist.high + severity_dist.medium + severity_dist.low;
    const defect_rate = data.total_detections > 0 ? (total_defects / data.total_detections * 100).toFixed(1) : 0;
    
    // Update KPI cards
    if (document.getElementById('totalDefectsStats')) {
        document.getElementById('totalDefectsStats').textContent = total_defects;
    }
    if (document.getElementById('defectRateStats')) {
        document.getElementById('defectRateStats').textContent = defect_rate + '%';
    }
    
    // Calculate severity rates
    const highRate = data.total_detections > 0 ? Math.round((severity_dist.high / data.total_detections) * 100) : 0;
    const mediumRate = data.total_detections > 0 ? Math.round((severity_dist.medium / data.total_detections) * 100) : 0;
    const lowRate = data.total_detections > 0 ? Math.round((severity_dist.low / data.total_detections) * 100) : 0;
    
    // Quality score (inverse of defect rate)
    const qualityScore = Math.round(100 - defect_rate);
    
    // Update detailed metrics
    if (document.getElementById('highSeverityRate')) {
        document.getElementById('highSeverityRate').textContent = highRate + '%';
        document.getElementById('highSeverityBar').style.width = highRate + '%';
    }
    if (document.getElementById('mediumSeverityRate')) {
        document.getElementById('mediumSeverityRate').textContent = mediumRate + '%';
        document.getElementById('mediumSeverityBar').style.width = mediumRate + '%';
    }
    if (document.getElementById('lowSeverityRate')) {
        document.getElementById('lowSeverityRate').textContent = lowRate + '%';
        document.getElementById('lowSeverityBar').style.width = lowRate + '%';
    }
    if (document.getElementById('qualityScore')) {
        document.getElementById('qualityScore').textContent = qualityScore + '/100';
        document.getElementById('qualityScoreBar').style.width = qualityScore + '%';
    }
    
    // Update recent detections table
    updateRecentDetectionsTable(data.recent_detections || []);
}

// Update recent detections table
function updateRecentDetectionsTable(detections) {
    const tableBody = document.getElementById('recentDetectionsTable');
    if (!tableBody) return;
    
    if (!detections || detections.length === 0) {
        tableBody.innerHTML = '<tr><td colspan=\"5\" style=\"text-align: center; color: #9ca3af;\">No recent detections</td></tr>';
        return;
    }
    
    tableBody.innerHTML = detections.slice(0, 10).map(detection => {
        // Normalize field names from backend format
        const timestamp = detection.timestamp || detection.created_at;
        const area = detection.area_percentage || detection.defect_area || 0;
        const confidence = detection.confidence;
        
        return `
        <tr>
            <td>${new Date(timestamp).toLocaleString() || 'N/A'}</td>
            <td style=\"text-transform: capitalize;\">${detection.defect_type || 'Unknown'}</td>
            <td>
                <span class=\"severity ${detection.severity ? detection.severity.toLowerCase() : detection.is_normal ? 'normal' : 'normal'}\">
                    ${detection.severity || (detection.is_normal ? 'Normal' : 'Unknown')}
                </span>
            </td>
            <td><strong>${(confidence && confidence > 1 ? confidence : confidence * 100).toFixed(1)}%</strong></td>
            <td>${(typeof area === 'number' ? area : 0).toFixed(2)}%</td>
        </tr>
    `;
    }).join('');
}

// Process raw detections into analytics format
function processDetectionsData(detections) {
    const defect_distribution = {};
    const severity_distribution = { high: 0, medium: 0, low: 0, normal: 0 };
    let total_confidence = 0;
    
    detections.forEach(detection => {
        // Count defects by type
        const defect_type = detection.defect_type || 'Unknown';
        defect_distribution[defect_type] = (defect_distribution[defect_type] || 0) + 1;
        
        // Count severity - handle normal images separately
        if (detection.is_normal) {
            severity_distribution.normal++;
        } else if (detection.severity) {
            severity_distribution[detection.severity]++;
        }
        
        // Sum confidence - handle both formats (0-1 and 0-100)
        const conf = detection.confidence;
        total_confidence += (conf && conf > 1 ? conf / 100 : conf) || 0;
    });
    
    // Sort detections by timestamp (most recent first)
    // Handle both 'timestamp' and 'created_at' field names
    const recent_detections = detections
        .sort((a, b) => {
            const timeA = new Date(a.timestamp || a.created_at).getTime();
            const timeB = new Date(b.timestamp || b.created_at).getTime();
            return timeB - timeA;
        })
        .slice(0, 10);
    
    return {
        total_detections: detections.length,
        avg_confidence: detections.length > 0 ? (total_confidence / detections.length * 100) : 0,
        defect_distribution,
        severity_distribution,
        recent_detections
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
