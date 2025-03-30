import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Check if the request is for one of our public API routes
  const url = request.nextUrl.pathname;
  
  // Allow direct access to API endpoints without authentication
  if (url === '/api/execute' || url === '/api/feed') {
    return NextResponse.next();
  }

  // For all other routes, continue with the default middleware chain
  return NextResponse.next();
}

// Configure the middleware to run only on specific paths
export const config = {
  matcher: ['/api/:path*'],
}; 