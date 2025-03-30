// This middleware bypasses authentication for specific API routes
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;
  
  // Allow these routes to bypass authentication
  if (path === '/api/execute' || path === '/api/feed') {
    return NextResponse.next();
  }
  
  // Continue with normal auth flow for other routes
  return NextResponse.next();
} 