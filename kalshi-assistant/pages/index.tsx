import React, { useState } from 'react';
import Head from 'next/head';
import { useUser } from '@auth0/nextjs-auth0/client';

export default function Home() {
  const { user, isLoading, error: authError } = useUser();
  const [strategy, setStrategy] = useState("");
  const [recommendations, setRecommendations] = useState<any>(null);
  const [useAI, setUseAI] = useState(true);  // true = use main AI (Python agent), false = use fallback OpenAI
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRecommendations = async () => {
    if (!strategy) return;
    setLoading(true);
    setError(null);
    try {
      // Determine which backend source to use based on toggle
      const mode = useAI ? "agent" : "openai";
      const res = await fetch(`/api/py/recommendations?mode=${mode}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ strategy })
      });
      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }
      const data = await res.json();
      setRecommendations(data);
    } catch (err: any) {
      console.error("Error fetching recommendations:", err);
      setError(err.message || "Unexpected error");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchRecommendations();
  };

  return (
    <div>
      <Head>
        <title>Kalshi Trading Assistant</title>
        <meta name="description" content="AI-powered Kalshi trading assistant" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <header style={{ display: 'flex', justifyContent: 'flex-end', padding: '1rem 2rem', borderBottom: '1px solid #eaeaea' }}>
        {isLoading ? (
          <p>Loading...</p>
        ) : authError ? (
          <p>Error: {authError.message}</p>
        ) : user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            {user.picture && (
              <img 
                src={user.picture} 
                alt={user.name || 'User'} 
                style={{ width: '32px', height: '32px', borderRadius: '50%' }} 
              />
            )}
            <span>Welcome, {user.name}!</span>
            <a 
              href="/api/auth/logout" 
              style={{ 
                padding: '0.5rem 1rem', 
                backgroundColor: '#f44336', 
                color: 'white', 
                borderRadius: '4px', 
                textDecoration: 'none'
              }}
            >
              Logout
            </a>
          </div>
        ) : (
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
        )}
      </header>

      <main style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{ textAlign: 'center', fontSize: '2.5rem', marginBottom: '1rem' }}>
          Kalshi Trading Assistant
        </h1>
        
        <p style={{ textAlign: 'center', fontSize: '1.2rem', marginBottom: '2rem' }}>
          Your AI-powered tool for market analysis and trading strategies
        </p>

        {/* Strategy Input Form */}
        <div style={{ maxWidth: '800px', margin: '0 auto', marginBottom: '2rem', padding: '1.5rem', border: '1px solid #eaeaea', borderRadius: '10px' }}>
          <h2 style={{ marginBottom: '1rem' }}>Get Trading Recommendations</h2>
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                Describe your trading strategy:
              </label>
              <textarea 
                value={strategy} 
                onChange={e => setStrategy(e.target.value)} 
                placeholder="E.g. focus on interest rate events or economic announcements" 
                style={{ 
                  width: '100%', 
                  padding: '0.75rem', 
                  borderRadius: '4px', 
                  border: '1px solid #ccc',
                  minHeight: '100px'
                }}
              />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                  <input 
                    type="checkbox" 
                    checked={useAI} 
                    onChange={e => setUseAI(e.target.checked)} 
                    style={{ marginRight: '0.5rem' }}
                  />
                  Use AI Agent (uncheck for OpenAI fallback)
                </label>
              </div>
              <button 
                type="submit" 
                disabled={loading || !strategy}
                style={{ 
                  padding: '0.75rem 1.5rem', 
                  backgroundColor: '#0070f3', 
                  color: 'white', 
                  border: 'none', 
                  borderRadius: '4px', 
                  cursor: loading || !strategy ? 'not-allowed' : 'pointer',
                  opacity: loading || !strategy ? 0.7 : 1
                }}
              >
                {loading ? "Loading..." : "Get Recommendations"}
              </button>
            </div>
          </form>
        </div>

        {/* Error message */}
        {error && (
          <div style={{ 
            maxWidth: '800px', 
            margin: '0 auto', 
            marginBottom: '2rem', 
            padding: '1rem', 
            backgroundColor: '#ffebee', 
            color: '#c62828', 
            borderRadius: '4px'
          }}>
            Error: {error}
          </div>
        )}

        {/* Recommendations Output */}
        {recommendations && !loading && (
          <div style={{ 
            maxWidth: '800px', 
            margin: '0 auto', 
            marginBottom: '2rem', 
            padding: '1.5rem', 
            border: '1px solid #eaeaea', 
            borderRadius: '10px'
          }}>
            <h2 style={{ marginBottom: '1rem' }}>Hourly Trading Strategy</h2>
            {typeof recommendations.recommendations === 'string' ? (
              // If backend returned raw text (OpenAI fallback case)
              <pre style={{ 
                whiteSpace: 'pre-wrap', 
                backgroundColor: '#ffffff', 
                padding: '1rem', 
                borderRadius: '4px',
                color: '#000000',
                border: '2px solid #666',
                fontWeight: 'bold',
                fontSize: '16px'
              }}>
                {recommendations.recommendations}
              </pre>
            ) : (
              <>
                <table style={{ width: '100%', borderCollapse: 'collapse', color: '#000000', border: '2px solid #666' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#e0e0e0' }}>
                      <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '2px solid #666', fontWeight: 'bold' }}>Market</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '2px solid #666', fontWeight: 'bold' }}>Action</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '2px solid #666', fontWeight: 'bold' }}>Probability</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '2px solid #666', fontWeight: 'bold' }}>Position</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '2px solid #666', fontWeight: 'bold' }}>Contracts</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '2px solid #666', fontWeight: 'bold' }}>Cost</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '2px solid #666', fontWeight: 'bold' }}>Target Exit</th>
                      <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '2px solid #666', fontWeight: 'bold' }}>Stop Loss</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Array.isArray(recommendations.recommendations) && recommendations.recommendations.map((rec: any, idx: number) => (
                      <tr key={idx} style={{ backgroundColor: idx % 2 === 0 ? '#ffffff' : '#f0f0f0' }}>
                        <td style={{ padding: '0.75rem', borderBottom: '1px solid #666', fontWeight: 'bold' }}>{rec.market}</td>
                        <td style={{ padding: '0.75rem', borderBottom: '1px solid #666', fontWeight: 'bold' }}>{rec.action}</td>
                        <td style={{ padding: '0.75rem', borderBottom: '1px solid #666', fontWeight: 'bold' }}>{rec.probability || 'N/A'}</td>
                        <td style={{ padding: '0.75rem', borderBottom: '1px solid #666', fontWeight: 'bold' }}>{rec.position || 'N/A'}</td>
                        <td style={{ padding: '0.75rem', borderBottom: '1px solid #666', fontWeight: 'bold' }}>{rec.contracts || 'N/A'}</td>
                        <td style={{ padding: '0.75rem', borderBottom: '1px solid #666', fontWeight: 'bold' }}>{rec.cost || 'N/A'}</td>
                        <td style={{ padding: '0.75rem', borderBottom: '1px solid #666', fontWeight: 'bold' }}>{rec.target_exit || 'N/A'}</td>
                        <td style={{ padding: '0.75rem', borderBottom: '1px solid #666', fontWeight: 'bold' }}>{rec.stop_loss || 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {Array.isArray(recommendations.recommendations) && recommendations.recommendations.map((rec: any, idx: number) => (
                  <div key={`rationale-${idx}`} style={{ 
                    marginTop: '1rem', 
                    padding: '0.75rem', 
                    backgroundColor: '#ffffff', 
                    borderRadius: '4px', 
                    color: '#000000',
                    border: '2px solid #666',
                    fontWeight: 'bold',
                    fontSize: '16px'
                  }}>
                    <strong>{rec.market}:</strong> {rec.reason || 'No rationale provided'}
                  </div>
                ))}

                <div style={{ 
                  marginTop: '2rem', 
                  padding: '1rem', 
                  backgroundColor: '#ffffff', 
                  borderRadius: '4px', 
                  color: '#000000',
                  border: '2px solid #666',
                  fontWeight: 'bold',
                  fontSize: '16px'
                }}>
                  <h3 style={{ marginBottom: '0.75rem', color: '#000000' }}>Fund Allocation Summary</h3>
                  <p style={{ marginBottom: '0.5rem' }}><strong>Total Allocated:</strong> {recommendations.allocation?.total_allocated || 'N/A'}</p>
                  <p style={{ marginBottom: '0.5rem' }}><strong>Remaining Balance:</strong> {recommendations.allocation?.remaining_balance || 'N/A'}</p>
                  <p><strong>Reserved Base Amount:</strong> {recommendations.allocation?.reserved_base || 'N/A'}</p>
                </div>
              </>
            )}
            <p style={{ marginTop: '1rem', fontStyle: 'italic', color: '#757575' }}>
              Source: {recommendations.source}
            </p>
          </div>
        )}
      </main>

      <footer style={{ textAlign: 'center', padding: '2rem', borderTop: '1px solid #eaeaea' }}>
        <p>Powered by Next.js, FastAPI, and OpenAI</p>
      </footer>
    </div>
  );
} 