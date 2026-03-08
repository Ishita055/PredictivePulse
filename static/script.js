document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('assessment-form');
    const resultContainer = document.getElementById('result-container');
    const submitBtn = document.getElementById('submit-btn');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // UI Loading State
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> ANALYZING DATA...';
        submitBtn.disabled = true;
        resultContainer.classList.add('hidden');
        resultContainer.innerHTML = '';

        // Gather form data
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (result.success) {
                displayResult(result.prediction, result.confidence);
            } else {
                throw new Error(result.error || 'Failed to get prediction');
            }

        } catch (error) {
            console.error('Error:', error);
            resultContainer.innerHTML = `
                <div class="error-state">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                    <p>An error occurred while analyzing the data. Please try again.</p>
                </div>
            `;
            resultContainer.classList.remove('hidden');
        } finally {
            // Restore button state
            submitBtn.innerHTML = '<i class="fa-solid fa-chart-line"></i> GENERATE RISK ASSESSMENT';
            submitBtn.disabled = false;
        }
    });

    function displayResult(prediction, confidence) {
        
        let config = {};

        switch(prediction) {
            case 'NORMAL':
                config = {
                    title: 'Normal Blood Pressure',
                    icon: 'fa-check',
                    iconColor: 'success-icon',
                    bgColor: 'bg-success-light',
                    borderColor: 'border-success',
                    riskBadge: '<span class="badge risk-low">LOW RISK</span>',
                    description: 'Your cardiovascular risk assessment indicates normal blood pressure levels.',
                    recommendations: [
                        'Maintain current healthy lifestyle',
                        'Regular physical activity (150 minutes/week)',
                        'Continue balanced, low-sodium diet',
                        'Annual blood pressure monitoring',
                        'Regular health check-ups'
                    ]
                };
                break;
            case 'STAGE_1':
                config = {
                    title: 'Stage 1 Hypertension',
                    icon: 'fa-heart-pulse',
                    iconColor: 'warning-icon',
                    bgColor: 'bg-warning-light',
                    borderColor: 'border-warning',
                    riskBadge: '<span class="badge risk-moderate">MODERATE RISK</span>',
                    description: 'Mild elevation detected requiring lifestyle modifications and medical consultation.',
                    recommendations: [
                        'Schedule appointment with healthcare provider',
                        'Implement DASH diet plan',
                        'Increase physical activity gradually',
                        'Monitor blood pressure bi-weekly',
                        'Reduce sodium intake (<2300mg/day)',
                        'Consider stress management techniques'
                    ]
                };
                break;
            case 'STAGE_2':
                config = {
                    title: 'Stage 2 Hypertension',
                    icon: 'fa-heart-crack',
                    iconColor: 'danger-icon',
                    bgColor: 'bg-danger-light',
                    borderColor: 'border-danger',
                    riskBadge: '<span class="badge risk-high">HIGH RISK</span>',
                    description: 'Significant hypertension requiring immediate medical intervention and treatment.',
                    recommendations: [
                        'URGENT: Consult physician within 1-2 days',
                        'Likely medication therapy required',
                        'Comprehensive cardiovascular assessment',
                        'Daily blood pressure monitoring',
                        'Strict dietary sodium restriction',
                        'Lifestyle modification counseling'
                    ]
                };
                break;
            case 'CRISIS':
                config = {
                    title: 'Hypertensive Crisis',
                    icon: 'fa-triangle-exclamation',
                    iconColor: 'critical-icon',
                    bgColor: 'bg-critical-light',
                    borderColor: 'border-critical',
                    riskBadge: '<span class="badge risk-critical">EMERGENCY</span>',
                    description: 'CRITICAL: Dangerously elevated blood pressure requiring emergency medical care.',
                    recommendations: [
                        'EMERGENCY: Seek immediate medical attention',
                        'Call 911 if experiencing symptoms',
                        'Do not delay treatment',
                        'Monitor for stroke/heart attack signs',
                        'Prepare current medication list',
                        'Avoid physical exertion'
                    ]
                };
                break;
            default:
                config = {
                    title: 'Analysis Inconclusive',
                    icon: 'fa-circle-question',
                    iconColor: 'neutral-icon',
                    bgColor: 'bg-neutral-light',
                    borderColor: 'border-neutral',
                    riskBadge: '<span class="badge risk-neutral">UNKNOWN</span>',
                    description: 'We could not confidently determine your risk category.',
                    recommendations: [
                        'Please verify the entered information',
                        'Consult a healthcare provider for a professional assessment'
                    ]
                };
        }

        // Generate HTML
        const recList = config.recommendations.map(rec => `
            <li><i class="fa-solid fa-chevron-right"></i> ${rec}</li>
        `).join('');

        const html = `
            <div class="result-card ${config.borderColor} fade-in">
                <div class="result-header">
                    <div class="result-icon-box ${config.iconColor} ${config.bgColor}">
                        <i class="fa-solid ${config.icon}"></i>
                    </div>
                    <div class="result-title-area">
                        <h3>${config.title}</h3>
                        <div class="result-meta">
                            <span class="confidence"><i class="fa-solid fa-chart-simple"></i> Confidence: ${confidence}</span>
                            ${config.riskBadge}
                        </div>
                    </div>
                </div>
                
                <p class="result-desc">${config.description}</p>
                
                <div class="recommendations">
                    <h4><i class="fa-solid fa-clipboard-list"></i> Clinical Recommendations</h4>
                    <ul class="rec-list">
                        ${recList}
                    </ul>
                </div>
            </div>
        `;

        resultContainer.innerHTML = html;
        resultContainer.classList.remove('hidden');
        
        // Scroll to results smoothly
        resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
});
