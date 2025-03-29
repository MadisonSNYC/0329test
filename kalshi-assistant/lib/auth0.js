// lib/auth0.js
const { auth } = require('@auth0/nextjs-auth0');

exports.auth0 = auth({
  baseURL: process.env.AUTH0_BASE_URL,
  issuerBaseURL: process.env.AUTH0_ISSUER_BASE_URL,
  clientID: process.env.AUTH0_CLIENT_ID,
  clientSecret: process.env.AUTH0_CLIENT_SECRET,
  secret: process.env.AUTH0_SECRET,
  routes: {
    callback: '/auth/callback',
    login: '/auth/login',
    logout: '/auth/logout',
  },
}); 