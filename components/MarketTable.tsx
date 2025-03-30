import React from 'react';

interface MarketTableProps {
  markets: any[];
  source: string;
}

const MarketTable: React.FC<MarketTableProps> = ({ markets, source }) => {
  return (
    <div style={{ 
      maxWidth: '800px', 
      margin: '0 auto', 
      marginBottom: '2rem', 
      padding: '1.5rem', 
      border: '1px solid #eaeaea', 
      borderRadius: '10px',
      backgroundColor: '#f8f8f8'
    }}>
      <h2 style={{ marginBottom: '1rem' }}>Available Markets</h2>
      <p style={{ fontSize: '0.75rem', color: '#666', marginTop: '0.5rem', marginBottom: '1rem' }}>
        Data source: <strong>{source || 'unknown'}</strong>
      </p>
      <table style={{ width: '100%', borderCollapse: 'collapse', color: '#000000' }}>
        <thead>
          <tr style={{ backgroundColor: '#f0f0f0' }}>
            <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '1px solid #ccc', fontWeight: 'bold' }}>Market</th>
            <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '1px solid #ccc', fontWeight: 'bold' }}>Category</th>
            <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '1px solid #ccc', fontWeight: 'bold' }}>Yes Price</th>
            <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '1px solid #ccc', fontWeight: 'bold' }}>Volume</th>
          </tr>
        </thead>
        <tbody>
          {markets && markets.length > 0 ? (
            markets.map((m, idx) => (
              <tr key={idx} style={{ backgroundColor: idx % 2 === 0 ? '#ffffff' : '#f8f8f8' }}>
                <td style={{ padding: '0.75rem', borderBottom: '1px solid #ddd', fontWeight: 'bold' }}>{m.title || m.market || m.id}</td>
                <td style={{ padding: '0.75rem', borderBottom: '1px solid #ddd', fontWeight: 'bold' }}>{m.category}</td>
                <td style={{ padding: '0.75rem', borderBottom: '1px solid #ddd', fontWeight: 'bold' }}>{(parseFloat(m.yes_price || m.price) * 100).toFixed(2)}%</td>
                <td style={{ padding: '0.75rem', borderBottom: '1px solid #ddd', fontWeight: 'bold' }}>{m.volume?.toLocaleString() || 0}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={4} style={{ textAlign: 'center', padding: '1rem', color: '#666' }}>
                No market data available.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default MarketTable; 