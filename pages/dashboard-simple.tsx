import React, { useState, useEffect } from 'react';
import Head from 'next/head';

export default function DashboardSimple() {
  const [marketStats, setMarketStats] = useState({
    totalMarkets: 0,
    totalTradeVolume: 0,
    topCategories: ['CRYPTO', 'STOCKS', 'POLITICS']
  });

  // Simulate fetching dashboard data
  useEffect(() => {
    // This would typically be an API call
    const fetchDashboardData = () => {
      // Simulated data
      setMarketStats({
        totalMarkets: 147,
        totalTradeVolume: 4325789,
        topCategories: ['CRYPTO', 'STOCKS', 'POLITICS']
      });
    };

    fetchDashboardData();
  }, []);

  return (
    <div style={{ 
      backgroundColor: '#f8f9fa', 
      minHeight: '100vh',
      color: '#333333'
    }}>
      <Head>
        <title>Simple Dashboard - Kalshi Trading Assistant</title>
        <meta name="description" content="Trading dashboard with market insights" />
        <link rel="icon" href="/favicon.ico" />
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
              href="/dashboard-simple"
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
              Simple Dashboard
            </a>
          </li>
          <li>
            <a 
              href="/test-api"
              style={{ 
                color: '#0070f3', 
                textDecoration: 'none',
                fontWeight: 'bold',
                fontSize: '1.1rem'
              }}
            >
              Test API
            </a>
          </li>
        </ul>
      </nav>

      <main style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
        <h1 style={{ textAlign: 'center', fontSize: '2.5rem', marginBottom: '1rem' }}>
          Simple Dashboard (No Auth0)
        </h1>
        
        <p style={{ textAlign: 'center', fontSize: '1.2rem', marginBottom: '2rem' }}>
          Your market overview and performance metrics
        </p>

        {/* Dashboard Cards */}
        <div style={{ 
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2rem'
        }}>
          {/* Card 1 */}
          <div style={{ 
            padding: '1.5rem',
            backgroundColor: 'white',
            borderRadius: '10px',
            boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
            border: '1px solid #eaeaea'
          }}>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: '#333' }}>Market Overview</h2>
            <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
              <strong>Total Markets:</strong> {marketStats.totalMarkets.toLocaleString()}
            </p>
            <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
              <strong>Total Trade Volume:</strong> ${marketStats.totalTradeVolume.toLocaleString()}
            </p>
            <p style={{ fontSize: '1.1rem' }}>
              <strong>Top Categories:</strong> {marketStats.topCategories.join(', ')}
            </p>
          </div>

          {/* Card 2 */}
          <div style={{ 
            padding: '1.5rem',
            backgroundColor: 'white',
            borderRadius: '10px',
            boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
            border: '1px solid #eaeaea'
          }}>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: '#333' }}>Your Portfolio</h2>
            <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
              <strong>Open Positions:</strong> 5
            </p>
            <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>
              <strong>Current Value:</strong> $8,450
            </p>
            <p style={{ fontSize: '1.1rem', color: '#4caf50' }}>
              <strong>Performance:</strong> +15.2%
            </p>
          </div>

          {/* Card 3 */}
          <div style={{ 
            padding: '1.5rem',
            backgroundColor: 'white',
            borderRadius: '10px',
            boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
            border: '1px solid #eaeaea'
          }}>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: '#333' }}>Recent Activity</h2>
            <ul style={{ 
              listStyle: 'none',
              margin: 0,
              padding: 0
            }}>
              <li style={{ padding: '0.5rem 0', borderBottom: '1px solid #eee' }}>
                Bought 10 YES contracts on BTCUSD-24MAR
              </li>
              <li style={{ padding: '0.5rem 0', borderBottom: '1px solid #eee' }}>
                Sold 15 NO contracts on ETHUSD-24MAR
              </li>
              <li style={{ padding: '0.5rem 0' }}>
                Started new trading strategy: "Focus on tech earnings"
              </li>
            </ul>
          </div>
        </div>
      </main>

      <footer style={{ textAlign: 'center', padding: '2rem', borderTop: '1px solid #eaeaea' }}>
        <p>Powered by Next.js and FastAPI</p>
      </footer>
    </div>
  );
} 