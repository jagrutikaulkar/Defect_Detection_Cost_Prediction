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
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
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
    
    // Check if it's a normal image (no defect)
    if (result.is_normal) {
        // Display results for NORMAL image
        document.getElementById('defectType').textContent = '✓ CLEAN';
        document.getElementById('defectType').style.backgroundColor = '#10b981';
        document.getElementById('defectType').style.color = '#fff';
        document.getElementById('confidence').textContent = `${result.confidence}%`;
        
        // Hide defect-specific fields
        document.getElementById('severity').parentElement.style.display = 'none';
        document.getElementById('defectArea').parentElement.style.display = 'none';
        document.getElementById('predictedCost').parentElement.style.display = 'none';
        
        // Get processing time
        const processingTimeMs = Math.round((result.processing_time || 0.045) * 1000);
        document.getElementById('processingTime').textContent = `${processingTimeMs}ms`;
        
        // Display probabilities
        const probContainer = document.getElementById('probabilitiesContainer');
        if (probContainer && result.all_predictions) {
            probContainer.innerHTML = Object.entries(result.all_predictions)
                .sort((a, b) => b[1] - a[1])
                .map(([className, conf]) => `
                    <div class="probability-item">
                        <span class="class-name">${className}</span>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${conf}%; background: #10b981"></div>
                        </div>
                        <span class="confidence-value">${conf.toFixed(1)}%</span>
                    </div>
                `).join('');
        }
    } else {
        // Display results for DEFECT image
        document.getElementById('defectType').style.backgroundColor = '#ef4444';
        document.getElementById('defectType').style.color = '#fff';
        const defectDisplay = result.defect_type.charAt(0).toUpperCase() + result.defect_type.slice(1);
        document.getElementById('defectType').textContent = defectDisplay;
        document.getElementById('confidence').textContent = `${result.confidence}%`;
        
        // Show defect-specific fields
        const severityEl = document.getElementById('severity');
        severityEl.parentElement.style.display = 'block';
        severityEl.textContent = result.severity.toUpperCase();
        severityEl.className = `value ${result.severity.toUpperCase()}`;
        
        document.getElementById('defectArea').parentElement.style.display = 'block';
        document.getElementById('defectArea').textContent = `${result.defect_area}%`;
        
        document.getElementById('predictedCost').parentElement.style.display = 'block';
        document.getElementById('predictedCost').textContent = `₹${result.predicted_cost.toFixed(2)}`;
        
        const processingTimeMs = Math.round((result.processing_time || 0.045) * 1000);
        document.getElementById('processingTime').textContent = `${processingTimeMs}ms`;
        
        // Display probabilities with better formatting
        const probContainer = document.getElementById('probabilitiesContainer');
        if (probContainer && result.all_predictions) {
            probContainer.innerHTML = Object.entries(result.all_predictions)
                .sort((a, b) => b[1] - a[1])
                .map(([className, conf]) => {
                    const isDetected = className === result.defect_type;
                    return `
                        <div class="probability-item ${isDetected ? 'detected' : ''}">
                            <span class="class-name">${className}</span>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${conf}%; background: ${isDetected ? '#3b82f6' : '#e5e7eb'}"></div>
                            </div>
                            <span class="confidence-value">${conf.toFixed(1)}%</span>
                        </div>
                    `;
                }).join('');
        }
    }
    
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Load detection history
async function loadDetectionHistory() {
    try {
        const tbody = document.getElementById('historyTable');
        if (!tbody) return;
        
        const token = localStorage.getItem('token');
        if (!token) {
            tbody.innerHTML = '<tr><td colspan="4">Please login to view history</td></tr>';
            return;
        }
        
        const response = await fetch('/api/defect/history', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            console.error(`[ERROR] History API returned status ${response.status}`);
            const errorText = await response.text();
            console.error('[ERROR] Response:', errorText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('[DEBUG] History data received:', data);
        
        if (data.status === 'success' && data.data && data.data.length > 0) {
            // Filter out video records - only show image detections in history table
            const imageDetections = data.data.filter(detection => {
                // Skip video records (they have 'type: video' or 'detected_frames')
                return detection.type !== 'video' && !detection.detected_frames && detection.confidence !== undefined;
            });
            
            console.log(`[DEBUG] Filtered ${imageDetections.length} image detections from ${data.data.length} total records`);
            
            if (imageDetections.length > 0) {
                tbody.innerHTML = imageDetections.map(detection => {
                    const severityDisplay = detection.is_normal ? 'NORMAL' : (detection.severity?.toUpperCase() || 'N/A');
                    const severityClass = detection.is_normal ? 'normal' : (detection.severity || 'low');
                    return `
                        <tr>
                            <td>${new Date(detection.created_at).toLocaleString()}</td>
                            <td>${detection.defect_type}</td>
                            <td>${parseFloat(detection.confidence).toFixed(1)}%</td>
                            <td><span class="severity ${severityClass}">${severityDisplay}</span></td>
                        </tr>
                    `;
                }).join('');
                console.log(`[DEBUG] Rendered ${imageDetections.length} detections in history table`);
            } else {
                console.log('[DEBUG] No image detections found (only video records)');
                tbody.innerHTML = '<tr><td colspan="4">No image detections yet</td></tr>';
            }
        } else {
            console.log('[DEBUG] No detections found in history');
            tbody.innerHTML = '<tr><td colspan="4">No detections yet</td></tr>';
        }
    } catch (error) {
        console.error('Error loading history:', error);
        const tbody = document.getElementById('historyTable');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="4">Error loading history - check console</td></tr>';
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
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
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
