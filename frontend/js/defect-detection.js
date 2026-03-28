/* Defect Detection JavaScript */

// Real steel surface defect types used in industry
const DEFECT_CLASSES = ['Scale', 'Scratch', 'Dent', 'Pit/Corrosion', 'Stain', 'Crack'];

// Handle file input change
document.addEventListener('DOMContentLoaded', () => {
    const imageInput = document.getElementById('imageInput');
    if (imageInput) {
        imageInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleDefectDetection(e.target.files[0]);
            }
        });
    }
});

// Handle image upload and detection
async function handleDefectDetection(file) {
    // Show preview immediately
    const reader = new FileReader();
    reader.onload = (e) => {
        const previewImg = document.getElementById('previewImage');
        if (previewImg) {
            previewImg.src = e.target.result;
        }
    };
    reader.readAsDataURL(file);
    
    // Get production parameters from user input
    const machineTime = parseFloat(document.getElementById('machineTime')?.value || 2.0);
    const laborCost = parseFloat(document.getElementById('laborCost')?.value || 300);
    const materialCost = parseFloat(document.getElementById('materialCost')?.value || 200);
    
    const formData = new FormData();
    formData.append('image', file);
    formData.append('machine_time', machineTime);
    formData.append('labor_cost', laborCost);
    formData.append('material_cost', materialCost);
    
    try {
        showNotification('Processing image with production parameters...', 'success');
        
        const response = await fetch('/api/defect/detect', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success' && data.data) {
            showNotification('Detection complete!', 'success');
            showDetectionResults(data.data);
            loadDetectionHistory();
        } else if (data.success) {
            showNotification('Detection complete!', 'success');
            showDetectionResults(data.data || data);
            loadDetectionHistory();
        } else {
            throw new Error(data.error || 'Detection failed');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error: ' + error.message, 'error');
    }
}

// Generate demo detection result
function generateDemoDetectionResult() {
    const randomClass = DEFECT_CLASSES[Math.floor(Math.random() * DEFECT_CLASSES.length)];
    const baseConfidence = 92 + Math.random() * 8; // Higher confidence range
    
    const probabilities = DEFECT_CLASSES.map(className => {
        let conf;
        if (className === randomClass) {
            // Make the detected class have highest confidence
            conf = baseConfidence;
        } else {
            // Other classes have much lower confidence
            conf = (100 - baseConfidence) / (DEFECT_CLASSES.length - 1) + Math.random() * 5;
        }
        return {
            class: className,
            confidence: Math.max(5, Math.min(100, conf))
        };
    }).sort((a, b) => b.confidence - a.confidence);
    
    // Ensure the top result matches our predicted class
    const topResult = probabilities[0];
    
    return {
        defect_type: topResult.class,
        confidence: Math.round(topResult.confidence * 10) / 10,
        severity: topResult.confidence > 90 ? 'high' : topResult.confidence > 75 ? 'medium' : 'low',
        processing_time: 0.045 + Math.random() * 0.01,
        probabilities: probabilities
    };
}

// Show detection results
function showDetectionResults(result) {
    const resultsSection = document.getElementById('resultsSection');
    if (!resultsSection) return;
    
    // Update results with proper defect type display
    const defectDisplay = result.defect_type.charAt(0).toUpperCase() + result.defect_type.slice(1);
    document.getElementById('defectType').textContent = defectDisplay;
    document.getElementById('confidence').textContent = `${result.confidence}%`;
    const severityEl = document.getElementById('severity');
    severityEl.textContent = result.severity.toUpperCase();
    severityEl.className = `value ${result.severity.toUpperCase()}`;
    document.getElementById('defectArea').textContent = `${result.defect_area}%`;
    document.getElementById('predictedCost').textContent = `₹${result.predicted_cost.toFixed(2)}`;
    const processingTimeMs = Math.round(result.processing_time * 1000);
    document.getElementById('processingTime').textContent = `${processingTimeMs}ms`;
    
    // Display probabilities
    const probContainer = document.getElementById('probabilitiesContainer');
    if (probContainer && result.probabilities) {
        probContainer.innerHTML = result.probabilities.map((p, i) => `
            <div class="probability-item">
                <span>${p.class || p.name || p}</span>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${p.confidence}%\"></div>
                </div>
                <span>${p.confidence.toFixed(1)}%</span>
            </div>
        `).join('');
    }
    
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Load detection history
async function loadDetectionHistory() {
    try {
        const tbody = document.getElementById('historyTable');
        if (!tbody) return;
        
        const response = await fetch('/api/defect/history', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'success' && data.data && data.data.length > 0) {
            tbody.innerHTML = data.data.map(detection => `
                <tr>
                    <td>${new Date(detection.created_at).toLocaleString()}</td>
                    <td>${detection.defect_type}</td>
                    <td>${detection.confidence.toFixed(1)}%</td>
                    <td><span class="severity ${detection.severity}">${detection.severity.toUpperCase()}</span></td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="4">No detections yet</td></tr>';
        }
    } catch (error) {
        console.error('Error loading history:', error);
        const tbody = document.getElementById('historyTable');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="4">Error loading history</td></tr>';
        }
    }
}

// Delete detection history
async function deleteDetectionHistory() {
    if (!confirm('Are you sure you want to delete all detection history? This cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/defect/history/delete', {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification('Detection history deleted successfully', 'success');
            loadDetectionHistory();
        } else {
            showNotification('Failed to delete detection history', 'error');
        }
    } catch (error) {
        console.error('Error deleting history:', error);
        showNotification('Error deleting detection history', 'error');
    }
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadDetectionHistory);
} else {
    loadDetectionHistory();
}

// Initialize page - load history on page load
if (document.readyState !== 'loading') {
    loadDetectionHistory();
} else {
    document.addEventListener('DOMContentLoaded', loadDetectionHistory);
}
