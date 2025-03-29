// Catch-all route handler for API requests that should be proxied to the backend
export default function handler(req, res) {
  const { path } = req.query;
  const fullPath = path.join('/');
  
  console.log(`API request received for path: ${fullPath}`);
  console.log(`Method: ${req.method}`);
  console.log(`Query params:`, req.query);
  
  // This catch-all route should only be used for requests that aren't handled
  // by the Next.js rewrite to FastAPI. All py/ requests should be
  // proxied directly to the FastAPI backend by the rewrite in next.config.js

  // Default response for any paths that somehow reach this handler
  return res.status(404).json({ 
    message: `API route not found: ${fullPath}. This request should be handled by the FastAPI backend.`,
    query: req.query,
    method: req.method
  });
} 