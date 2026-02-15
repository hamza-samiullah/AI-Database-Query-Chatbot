#!/bin/bash

echo "🚀 Preparing for Vercel Deployment..."

# 1. Install Vercel CLI if not present
if ! command -v vercel &> /dev/null; then
    echo "Installing Vercel CLI..."
    npm install -g vercel
fi

# 2. Login to Vercel
echo "Please login to Vercel..."
vercel login

# 3. Deploy
echo "Deploying to Vercel..."
# The --prod flag deploys to production
vercel --prod

echo "✅ Deployment initiated!"
echo "NOTE: Remember to set your Environment Variables in the Vercel Dashboard:"
echo "      - GROQ_API_KEY"
echo "      - GROQ_BASE_URL (Optional)"
echo "      - MODEL_NAME (Default: llama-3.3-70b-versatile)"
