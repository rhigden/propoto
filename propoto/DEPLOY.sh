#!/bin/bash
# Propoto Production Deployment Script
# This script guides you through deploying to production

set -e

echo "🚀 Propoto Production Deployment"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found${NC}"
    exit 1
fi
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}❌ Vercel CLI not found${NC}"
    exit 1
fi
if ! command -v npx &> /dev/null; then
    echo -e "${RED}❌ npx not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ All prerequisites met${NC}"
echo ""

# Step 1: Deploy Convex
echo "📦 Step 1: Deploy Convex to Production"
echo "--------------------------------------"
read -p "Deploy Convex now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd propoto/web
    echo "Deploying Convex..."
    npx convex deploy --prod
    echo -e "${GREEN}✅ Convex deployed${NC}"
    echo ""
    echo "⚠️  IMPORTANT: Copy the production deployment URL and set it as NEXT_PUBLIC_CONVEX_URL"
    cd ../..
else
    echo "Skipping Convex deployment"
fi
echo ""

# Step 2: Deploy Backend
echo "🔧 Step 2: Deploy Backend API"
echo "-----------------------------"
echo "Choose deployment platform:"
echo "1) Railway (recommended)"
echo "2) Render"
echo "3) Fly.io"
echo "4) Skip (deploy manually)"
read -p "Choice (1-4): " choice

case $choice in
    1)
        echo "Deploying to Railway..."
        cd propoto/api
        if ! command -v railway &> /dev/null; then
            echo "Installing Railway CLI..."
            npm i -g @railway/cli
        fi
        railway login
        railway init
        railway up
        echo -e "${GREEN}✅ Backend deployed to Railway${NC}"
        cd ../..
        ;;
    2)
        echo "Deploy to Render manually:"
        echo "1. Go to https://render.com"
        echo "2. Create new Web Service"
        echo "3. Connect GitHub repo"
        echo "4. Set root directory to: propoto/api"
        echo "5. Build command: pip install -r requirements.txt"
        echo "6. Start command: uvicorn main:app --host 0.0.0.0 --port \$PORT"
        ;;
    3)
        echo "Deploying to Fly.io..."
        cd propoto/api
        if ! command -v fly &> /dev/null; then
            echo "Install Fly.io CLI: https://fly.io/docs/getting-started/installing-flyctl/"
            exit 1
        fi
        fly launch
        echo -e "${GREEN}✅ Backend deployed to Fly.io${NC}"
        cd ../..
        ;;
    4)
        echo "Skipping backend deployment"
        ;;
esac
echo ""

# Step 3: Deploy Frontend
echo "🌐 Step 3: Deploy Frontend to Vercel"
echo "-------------------------------------"
read -p "Deploy frontend now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd propoto/web
    vercel --prod
    echo -e "${GREEN}✅ Frontend deployed to Vercel${NC}"
    cd ../..
else
    echo "Skipping frontend deployment"
fi
echo ""

# Final checklist
echo "✅ Deployment Complete!"
echo ""
echo "📝 Next Steps:"
echo "1. Set environment variables in your deployment platforms"
echo "2. Test health endpoint: GET /health"
echo "3. Test proposal generation endpoint"
echo "4. Verify frontend can connect to backend and Convex"
echo ""
echo "See DEPLOYMENT.md for detailed environment variable setup"

