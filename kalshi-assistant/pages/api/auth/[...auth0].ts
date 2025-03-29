import { handleAuth } from '@auth0/nextjs-auth0';

// This generates /api/auth/login, /api/auth/logout, /api/auth/callback, and /api/auth/me routes
export default handleAuth(); 