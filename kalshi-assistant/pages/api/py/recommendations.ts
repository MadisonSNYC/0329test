import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { strategy } = req.body;
  const mode = req.query.mode || 'agent';

  try {
    // Forward the request to our FastAPI backend
    const apiUrl = `${process.env.API_URL || 'http://127.0.0.1:8001'}/recommendations?mode=${mode}`;
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ strategy }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend API error:', errorText);
      return res.status(response.status).json({ 
        message: `Backend API error: ${response.status}`,
        error: errorText
      });
    }

    const data = await response.json();
    return res.status(200).json(data);
  } catch (error) {
    console.error('Error proxying to backend:', error);
    return res.status(500).json({ 
      message: 'Error connecting to backend service',
      error: error instanceof Error ? error.message : String(error)
    });
  }
} 