#!/bin/bash

# Remove existing directory if it exists
rm -rf kalshi-assistant

# Create a new Next.js app with TypeScript
echo "Creating Next.js app..."
# Using expect-like approach with echo to answer prompts
(echo "Yes" && echo "Yes" && echo "Yes" && echo "Yes" && echo "src/" && echo "@/*" && echo "No") | npx create-next-app@latest kalshi-assistant --typescript

# Change to the app directory after installation
cd kalshi-assistant
echo "Next.js app created successfully in kalshi-assistant directory" 