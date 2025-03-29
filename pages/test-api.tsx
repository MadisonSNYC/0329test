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
    <div style={{ 
      backgroundColor: '#f8f9fa', 
      minHeight: '100vh',
      color: '#333333'
    }}>
      <Head>
        <title>API Test - Kalshi Assistant</title>
        <meta name="description" content="Test the OpenAI integration API" />
      </Head>

      <header style={{ 
        display: 'flex', 
        justifyContent: 'flex-end', 
        padding: '1rem 2rem', 
        borderBottom: '1px solid #333',
        backgroundColor: '#ffffff'
      }}>
        <a 
          href="/api/auth/login" 
          style={{ 
            padding: '0.5rem 1rem', 
            backgroundColor: '#0070f3', 
            color: 'white', 
            borderRadius: '4px', 
            textDecoration: 'none'
          }}
        >
          Login
        </a>
      </header>

      <nav style={{ 
        display: 'flex',
        justifyContent: 'center',
        padding: '0.75rem',
        backgroundColor: '#f0f8ff', 
        borderBottom: '1px solid #e0e0e0',
        boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
      }}>
        <ul style={{ 
          display: 'flex',
          listStyle: 'none',
          gap: '2rem',
          margin: 0,
          padding: 0
        }}>
          <li>
            <a 
              href="/"
              style={{ 
                color: '#0070f3', 
                textDecoration: 'none',
                fontWeight: 'bold',
                fontSize: '1.1rem'
              }}
            >
              Home
            </a>
          </li>
          <li>
            <a 
              href="/dashboard"
              style={{ 
                color: '#0070f3', 
                textDecoration: 'none',
                fontWeight: 'bold',
                fontSize: '1.1rem'
              }}
            >
              Dashboard
            </a>
          </li>
          <li>
            <a 
              href="/test-api"
              style={{ 
                color: '#0070f3', 
                textDecoration: 'none',
                fontWeight: 'bold',
                fontSize: '1.1rem',
                padding: '0.5rem 1rem',
                borderRadius: '4px',
                backgroundColor: 'rgba(0, 112, 243, 0.1)'
              }}
            >
              Test API
            </a>
          </li>
        </ul>
      </nav>

      <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
        <h1 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '1rem' }}>Test OpenAI Integration</h1>
        <p style={{ textAlign: 'center', marginBottom: '2rem' }}>This page tests the recommendations endpoint to verify OpenAI integration.</p>
        
        <div style={{ 
          padding: '1.5rem', 
          border: '1px solid #eaeaea', 
          borderRadius: '10px',
          marginBottom: '2rem',
          backgroundColor: 'white' 
        }}>
          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="strategy" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
              Trading Strategy:
            </label>
            <textarea
              id="strategy"
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              style={{ 
                width: '100%', 
                padding: '0.75rem', 
                minHeight: '100px',
                borderRadius: '4px',
                border: '1px solid #ccc'
              }}
            />
          </div>
          
          <button 
            onClick={callRecommendationsAPI}
            disabled={loading}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#0070f3',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: 'bold'
            }}
          >
            {loading ? 'Loading...' : 'Get Recommendations'}
          </button>
        </div>
        
        {error && (
          <div style={{ 
            marginBottom: '2rem', 
            padding: '1rem', 
            backgroundColor: '#ffebee', 
            color: '#c62828', 
            borderRadius: '4px',
            border: '1px solid #ef9a9a'
          }}>
            <strong>Error:</strong> {error}
          </div>
        )}
        
        {results && (
          <div style={{ 
            padding: '1.5rem', 
            border: '1px solid #eaeaea', 
            borderRadius: '10px',
            backgroundColor: 'white'
          }}>
            <h2 style={{ marginBottom: '1rem' }}>Results</h2>
            
            <div style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '4px', border: '1px solid #e0e0e0' }}>
              <h3>Source: {results.source}</h3>
              <p><strong>Strategy:</strong> {results.strategy}</p>
              
              <div>
                <strong>Recommendations:</strong>
                <pre style={{ 
                  whiteSpace: 'pre-wrap', 
                  marginTop: '0.5rem',
                  padding: '1rem',
                  backgroundColor: '#ffffff',
                  border: '1px solid #ccc',
                  borderRadius: '4px'
                }}>
                  {typeof results.recommendations === 'string' 
                    ? results.recommendations 
                    : JSON.stringify(results.recommendations, null, 2)
                  }
                </pre>
              </div>
              
              {results.error && (
                <div style={{ 
                  marginTop: '1rem',
                  padding: '0.75rem',
                  backgroundColor: '#ffebee',
                  color: '#c62828',
                  borderRadius: '4px',
                  border: '1px solid #ef9a9a'
                }}>
                  <strong>Error:</strong> {results.error}
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
} 