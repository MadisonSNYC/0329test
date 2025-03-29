import React from 'react';
import Head from 'next/head';
import { useUser } from '@auth0/nextjs-auth0/client';

export default function Home() {
  const { user, isLoading } = useUser();

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
              href="/auth/logout" 
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
            href="/auth/login" 
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
          Welcome to Kalshi Trading Assistant
        </h1>
        
        <p style={{ textAlign: 'center', fontSize: '1.2rem', marginBottom: '2rem' }}>
          Your AI-powered tool for market analysis and trading strategies
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          <div style={{ padding: '1.5rem', border: '1px solid #eaeaea', borderRadius: '10px' }}>
            <h2>Market Analysis</h2>
            <p>Get AI-powered insights on specific markets or categories</p>
          </div>
          
          <div style={{ padding: '1.5rem', border: '1px solid #eaeaea', borderRadius: '10px' }}>
            <h2>Trading Strategies</h2>
            <p>Discover potential trading opportunities and strategies</p>
          </div>
          
          <div style={{ padding: '1.5rem', border: '1px solid #eaeaea', borderRadius: '10px' }}>
            <h2>Portfolio Management</h2>
            <p>Track and manage your trading portfolio efficiently</p>
          </div>
        </div>
      </main>

      <footer style={{ textAlign: 'center', padding: '2rem', borderTop: '1px solid #eaeaea' }}>
        <p>Powered by Next.js, FastAPI, and OpenAI</p>
      </footer>
    </div>
  );
} 