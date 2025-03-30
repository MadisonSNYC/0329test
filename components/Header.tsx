import React from 'react';
import Head from 'next/head';

interface HeaderProps {
  user: any;
  isLoading: boolean;
  authError: any;
}

const Header: React.FC<HeaderProps> = ({ user, isLoading, authError }) => {
  return (
    <Head>
      <title>Kalshi Trading Assistant</title>
      <meta name="description" content="AI-powered Kalshi trading assistant" />
      <link rel="icon" href="/favicon.ico" />
    </Head>
  );
};

export default Header; 