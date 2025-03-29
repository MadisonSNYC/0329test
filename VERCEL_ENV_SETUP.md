# Setting Up Kalshi Environment Variables in Vercel

To ensure your Kalshi Trading Assistant works correctly in production, you need to set up the following environment variables in your Vercel project:

## Required Environment Variables

### Kalshi API Authentication (Choose one method)

#### Option 1: API Key Authentication
```
KALSHI_API_KEY=your_api_key_here
KALSHI_API_SECRET=your_api_secret_here
```

#### Option 2: Email/Password Authentication
```
KALSHI_EMAIL=your_kalshi_email@example.com
KALSHI_PASSWORD=your_kalshi_password
```

### Environment Selection
```
# Set to true to use the demo API (no real money)
# Set to false for production API (real trading)
IS_DEMO=true
```

## How to Add These to Vercel

1. Go to your Vercel dashboard
2. Select your project
3. Click on "Settings" tab
4. Select "Environment Variables" from the left menu
5. Add each variable with its corresponding value
6. Make sure to select the appropriate environments (Production, Preview, Development)
7. Click "Save" to apply the changes

## Verification Steps

After deployment, you can verify your environment variables are working by:

1. Visit your deployed site
2. Check the "Available Markets" section - it should display real market data from Kalshi
3. If you see markets listed with titles, categories, and prices, your Kalshi API integration is working
4. If you see an error or dummy data, check the browser console for error messages

## Troubleshooting

If your application shows dummy data with `"source": "error"`:

1. Check that your credentials are correct
2. Verify that you have access to the Kalshi API with those credentials
3. For email/password authentication, ensure your Kalshi account is active
4. For API key authentication, make sure the key has not expired

Remember that in production, you should use the actual Kalshi API (IS_DEMO=false) once you've confirmed everything works with the demo API. 