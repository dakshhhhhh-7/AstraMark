import { useState } from 'react';
import axios from 'axios';
import { safeErrorMessage } from '@/utils/safeRender';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

export function TestPage() {
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const testAnalyze = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await axios.post(`${BACKEND_URL}/api/analyze`, {
                business_type: 'SaaS',
                target_market: 'Small businesses',
                monthly_budget: '$5000',
                primary_goal: 'Increase leads',
                additional_info: 'Test'
            });
            console.log('Response:', response.data);
            setResult(response.data);
        } catch (err) {
            console.error('Error:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px', color: 'white', backgroundColor: '#1a1a1a', minHeight: '100vh' }}>
            <h1>API Test Page</h1>
            <button 
                onClick={testAnalyze}
                disabled={loading}
                style={{ padding: '10px 20px', fontSize: '16px', cursor: 'pointer' }}
            >
                {loading ? 'Testing...' : 'Test Analyze API'}
            </button>
            
            {error && (
                <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#ff0000', color: 'white' }}>
                    Error: {safeErrorMessage(error)}
                </div>
            )}
            
            {result && (
                <div style={{ marginTop: '20px' }}>
                    <h2>Success!</h2>
                    <pre style={{ backgroundColor: '#2a2a2a', padding: '10px', overflow: 'auto', maxHeight: '500px' }}>
                        {JSON.stringify(result, null, 2)}
                    </pre>
                </div>
            )}
        </div>
    );
}
