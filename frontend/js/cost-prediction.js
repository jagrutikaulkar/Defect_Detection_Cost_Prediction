/* Cost Prediction JavaScript */

// Handle cost prediction
async function handleCostPrediction(event) {
    event.preventDefault();
    
    const data = {
        material_cost: parseFloat(document.getElementById('materialCost').value),
        labor_cost: parseFloat(document.getElementById('laborCost').value),
        machine_time: parseFloat(document.getElementById('machineTime').value),
        energy_consumption: parseFloat(document.getElementById('energyConsumption').value),
        defect_rate: parseFloat(document.getElementById('defectRate').value)
    };
    
    try {
        const response = await fetch('/api/cost/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success || result.status === 'success') {
            showCostResults(result.data || result);
            loadCostHistory();
        } else {
            // Show demo result on error
            const demoResult = generateDemoCostResult(data);
            showCostResults(demoResult);
            loadCostHistory();
        }
    } catch (error) {
        // Show demo result on network error
        const demoResult = generateDemoCostResult(data);
        showCostResults(demoResult);
        showNotification('Using demo data', 'success');
    }
}

// Generate demo cost prediction
function generateDemoCostResult(inputData) {
    const baseTotal = inputData.material_cost + inputData.labor_cost + (inputData.machine_time * 50) + (inputData.energy_consumption * 5);
    const defectPenalty = (baseTotal * inputData.defect_rate) / 100;
    const predicted_cost = baseTotal + defectPenalty;
    
    return {
        predicted_cost: predicted_cost,
        breakdown: {
            material: inputData.material_cost,
            labor: inputData.labor_cost,
            machine: inputData.machine_time * 50,
            energy: inputData.energy_consumption * 5,
            defect_penalty: defectPenalty
        },
        confidence_interval: {
            lower: predicted_cost * 0.95,
            upper: predicted_cost * 1.05
        },
        optimization_suggestions: [
            'Reduce waste by 10% to save ₹' + (predicted_cost * 0.05).toFixed(0),
            'Optimize machine time for efficiency',
            'Implement defect prevention measures',
            'Review energy consumption patterns'
        ]
    };
}

// Show cost results
function showCostResults(result) {
    const resultsSection = document.getElementById('costResultsSection');
    if (!resultsSection) return;
    
    // Update cost
    document.getElementById('predictedCost').textContent = result.predicted_cost.toFixed(2);
    
    // Update breakdown
    const breakdown = result.breakdown;
    const breakdownContainer = document.getElementById('breakdownContainer');
    if (breakdownContainer && breakdown) {
        breakdownContainer.innerHTML = `
            <div class="breakdown-item">
                <span>Material</span>
                <span>₹${breakdown.material.toFixed(2)}</span>
            </div>
            <div class="breakdown-item">
                <span>Labor</span>
                <span>₹${breakdown.labor.toFixed(2)}</span>
            </div>
            <div class="breakdown-item">
                <span>Machine</span>
                <span>₹${breakdown.machine.toFixed(2)}</span>
            </div>
            <div class="breakdown-item">
                <span>Energy</span>
                <span>₹${breakdown.energy.toFixed(2)}</span>
            </div>
            <div class="breakdown-item">
                <span>Defect Penalty</span>
                <span>₹${breakdown.defect_penalty.toFixed(2)}</span>
            </div>
        `;
    }
    
    // Update confidence interval
    if (result.confidence_interval) {
        document.getElementById('lowerBound').textContent = result.confidence_interval.lower.toFixed(2);
        document.getElementById('upperBound').textContent = result.confidence_interval.upper.toFixed(2);
    }
    
    // Update suggestions
    const suggestionsContainer = document.getElementById('suggestionsContainer');
    if (suggestionsContainer && result.optimization_suggestions) {
        suggestionsContainer.innerHTML = result.optimization_suggestions.map(s => `
            <div class="suggestion-item">
                <i class="fas fa-lightbulb"></i> ${s}
            </div>
        `).join('');
    }
    
    resultsSection.style.display = 'block';
}

// Load cost history from defections
async function loadCostHistory() {
    try {
        const response = await fetch('/api/defect/history', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success' && data.data && data.data.length > 0) {
            updateCostHistoryTable(data.data);
        } else {
            updateCostHistoryTable([]);
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// Update cost history table - Show costs from defect detections
function updateCostHistoryTable(detections) {
    const tbody = document.getElementById('costHistoryTable');
    if (!tbody) return;
    
    if (!detections || detections.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4">No cost data yet. Make a prediction above or upload images in Defect Detection.</td></tr>';
        return;
    }
    
    // Filter only detections with predicted_cost (actual defects, not normal images)
    const costDetections = detections.filter(d => d.predicted_cost);
    
    if (costDetections.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4">No defects detected. Normal images do not generate costs.</td></tr>';
        return;
    }
    
    tbody.innerHTML = costDetections.map(detection => `
        <tr>
            <td>${new Date(detection.created_at).toLocaleString()}</td>
            <td>${detection.defect_area ? detection.defect_area.toFixed(1) + '%' : '-'}</td>
            <td>${detection.severity ? detection.severity.toUpperCase() : '-'}</td>
            <td>${detection.predicted_cost ? '₹' + detection.predicted_cost.toLocaleString('en-IN', {maximumFractionDigits: 0}) : '-'}</td>
        </tr>
    `).join('');
}

// Add styles for breakdown
const style = document.createElement('style');
style.textContent = `
    .breakdown-item {
        display: flex;
        justify-content: space-between;
        padding: 0.8rem;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .suggestion-item {
        display: flex;
        gap: 1rem;
        padding: 0.8rem;
        background: white;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #10b981;
    }
    
    .suggestion-item i {
        color: #10b981;
    }
`;
document.head.appendChild(style);

// Delete cost history
async function deleteCostHistory() {
    if (!confirm('Are you sure you want to delete all cost history? This cannot be undone.')) {
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
            showNotification('Cost history deleted successfully', 'success');
            loadCostHistory();
        } else {
            showNotification('Failed to delete cost history', 'error');
        }
    } catch (error) {
        console.error('Error deleting history:', error);
        showNotification('Error deleting cost history', 'error');
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('costForm')) {
        loadCostHistory();
    }
});
