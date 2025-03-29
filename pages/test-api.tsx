import { useState } from 'react';
import Head from 'next/head';

export default function TestAPI() {
  const [strategy, setStrategy] = useState('Focus on events related to interest rates.');
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const callRecommendationsAPI = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/py/recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strategy }),
      });
      
      if (!response.ok) {
        throw new Error(`API returned ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      console.error('Error calling API:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <Head>
        <title>API Test - Kalshi Assistant</title>
      </Head>

      <h1>Test OpenAI Integration</h1>
      <p>This page tests the recommendations endpoint to verify OpenAI integration.</p>
      
      <div style={{ marginBottom: '1rem' }}>
        <label htmlFor="strategy" style={{ display: 'block', marginBottom: '0.5rem' }}>
          Trading Strategy:
        </label>
        <textarea
          id="strategy"
          value={strategy}
          onChange={(e) => setStrategy(e.target.value)}
          style={{ width: '100%', padding: '0.5rem', minHeight: '100px' }}
        />
      </div>
      
      <button 
        onClick={callRecommendationsAPI}
        disabled={loading}
        style={{
          padding: '0.5rem 1rem',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: loading ? 'not-allowed' : 'pointer'
        }}
      >
        {loading ? 'Loading...' : 'Get Recommendations'}
      </button>
      
      {error && (
        <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f8d7da', color: '#721c24', borderRadius: '4px' }}>
          <strong>Error:</strong> {error}
        </div>
      )}
      
      {results && (
        <div style={{ marginTop: '1rem' }}>
          <h2>Results</h2>
          
          <div style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
            <h3>Source: {results.source}</h3>
            <p><strong>Strategy:</strong> {results.strategy}</p>
            
            <div>
              <strong>Recommendations:</strong>
              <pre style={{ whiteSpace: 'pre-wrap', marginTop: '0.5rem' }}>
                {typeof results.recommendations === 'string' 
                  ? results.recommendations 
                  : JSON.stringify(results.recommendations, null, 2)
                }
              </pre>
            </div>
            
            {results.error && (
              <div style={{ marginTop: '1rem' }}>
                <strong>Error:</strong> {results.error}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
} 