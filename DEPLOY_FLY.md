# 🚀 Deploy to Fly.io (Free Alternative)

**Free Tier**: 3 VMs with 256MB RAM each (enough for your API)

---

## Step 1: Install Fly.io CLI

### Linux/WSL:
```bash
curl -L https://fly.io/install.sh | sh
```

### Add to PATH:
```bash
export FLYCTL_INSTALL="/home/user/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"
```

---

## Step 2: Sign Up and Login

```bash
fly auth signup
# Or if you have an account:
fly auth login
```

---

## Step 3: Deploy

```bash
cd /home/user/newshii/propoto/api

# Launch app (creates fly.toml)
fly launch --name propoto-api --region iad --no-deploy

# Set secrets (environment variables)
fly secrets set \
  OPENROUTER_API_KEY="sk-or-v1-xxx" \
  AGENT_SERVICE_KEY="your-secret-key" \
  EXA_API_KEY="xxx" \
  FIRECRAWL_API_KEY="fc-xxx" \
  CORS_ORIGINS="https://your-frontend.vercel.app"

# Deploy!
fly deploy
```

---

## Step 4: Get Your URL

After deployment:
```bash
fly status
fly open
```

Your API will be at: `https://propoto-api.fly.dev`

---

## Environment Variables

Set these as secrets:
```bash
fly secrets set OPENROUTER_API_KEY="sk-or-v1-xxx"
fly secrets set AGENT_SERVICE_KEY="your-secret-key"
fly secrets set EXA_API_KEY="xxx"
fly secrets set FIRECRAWL_API_KEY="fc-xxx"
fly secrets set CORS_ORIGINS="https://your-frontend.vercel.app"
```

Public env vars (already in fly.toml):
- `NEXT_PUBLIC_CONVEX_URL`
- `CONVEX_DEPLOYMENT`
- `PORT`

---

## Manage Your App

```bash
# View logs
fly logs

# Scale machines
fly scale count 1

# Check status
fly status

# SSH into machine
fly ssh console

# Destroy app
fly apps destroy propoto-api
```

---

## Cost

**100% FREE** with Fly.io's free tier:
- 3 shared-cpu-1x VMs with 256MB RAM
- 160GB outbound data transfer
- Auto-stop when idle (saves resources)

---

## Comparison: Render vs Fly.io

| Feature | Render Free | Fly.io Free |
|---------|-------------|-------------|
| RAM | 512MB | 256MB (x3 VMs) |
| Always-on | ❌ (spins down) | ✅ (configurable) |
| Cold start | ~30s | ~1-2s |
| Deploy time | 3-5 min | 1-2 min |
| Domain | .onrender.com | .fly.dev |
| **Winner** | Good | **Better** |

---

*Last Updated: January 2026*

