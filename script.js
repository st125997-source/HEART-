document.addEventListener('DOMContentLoaded', function() {
    console.log('Heart Disease Prediction App Loaded');
    
    const form = document.getElementById('predictionForm');
    const resultSection = document.getElementById('resultSection');
    const predictionIcon = document.getElementById('predictionIcon');
    const predictionResult = document.getElementById('predictionResult');
    const riskLevel = document.getElementById('riskLevel');
    const probabilityFill = document.getElementById('probabilityFill');
    const probabilityValue = document.getElementById('probabilityValue');
    const predictBtn = form.querySelector('.predict-btn');

    // Test server connection
    fetch('/health')
        .then(response => response.json())
        .then(data => console.log('Server health:', data))
        .catch(error => console.error('Server connection failed:', error));

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log('Form submitted');

        // Gather form data
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        console.log('Form data:', data);

        // Show loading state
        predictBtn.classList.add('loading');
        predictBtn.disabled = true;
        predictBtn.textContent = 'Analyzing';

        try {
            console.log('Sending request to /predict...');
            
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            console.log('Response status:', response.status);

            const result = await response.json();
            console.log('Response data:', result);

            if (response.ok) {
                displayResult(result);
            } else {
                console.error('Prediction failed:', result);
                alert('Error: ' + (result.error || 'Prediction failed. Check console for details.'));
            }
        } catch (error) {
            console.error('Network error:', error);
            alert('Network error: ' + error.message);
        } finally {
            // Reset button
            predictBtn.classList.remove('loading');
            predictBtn.disabled = false;
            predictBtn.textContent = 'Predict Heart Disease Risk';
        }
    });

    function displayResult(result) {
        console.log('Displaying result:', result);

        // Show result section
        resultSection.style.display = 'block';

        // Set icon
        if (result.prediction_id === 1) {
            predictionIcon.textContent = '⚠️';
        } else {
            predictionIcon.textContent = '✅';
        }

        // Set prediction text
        predictionResult.textContent = result.prediction;
        predictionResult.className = 'prediction-result ' + 
            (result.prediction_id === 1 ? 'positive' : 'negative');

        // Set risk level
        riskLevel.textContent = result.risk_level;
        riskLevel.className = 'risk-level';
        
        if (result.risk_level === 'High Risk') {
            riskLevel.classList.add('high');
        } else if (result.risk_level === 'Moderate Risk') {
            riskLevel.classList.add('moderate');
        } else {
            riskLevel.classList.add('low');
        }

        // Set probability
        const probability = (result.probability * 100).toFixed(1);
        probabilityValue.textContent = probability + '%';
        probabilityFill.style.width = probability + '%';
        probabilityFill.textContent = probability + '%';

        // Scroll to result
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        console.log('Result displayed successfully');
    }

    // Sample data for testing
    const samplePatients = {
        healthy: {
            Age: 40,
            Sex: 'M',
            ChestPainType: 'ATA',
            RestingBP: 120,
            Cholesterol: 200,
            FastingBS: 0,
            RestingECG: 'Normal',
            MaxHR: 172,
            ExerciseAngina: 'N',
            Oldpeak: 0,
            ST_Slope: 'Up'
        },
        risky: {
            Age: 60,
            Sex: 'M',
            ChestPainType: 'ASY',
            RestingBP: 150,
            Cholesterol: 280,
            FastingBS: 1,
            RestingECG: 'ST',
            MaxHR: 110,
            ExerciseAngina: 'Y',
            Oldpeak: 2.5,
            ST_Slope: 'Flat'
        }
    };

    console.log('Sample test data available:', samplePatients);
});
