# Deploying Commitment Broker to Vercel

## Prerequisites

1. **Install Vercel CLI globally:**
   ```bash
   npm install -g vercel
   # OR
   yarn global add vercel
   # OR
   pnpm add -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```
   This will open a browser window to authenticate.

## Frontend Deployment (Next.js)

### Option 1: Deploy via CLI (Recommended)

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Link your project (first time only):**
   ```bash
   vercel link
   ```
   - Select your Vercel account
   - Choose "Link to existing project" or "Create new project"
   - If creating new, name it `commitment-broker` or similar

3. **Set environment variables:**
   ```bash
   vercel env add NEXT_PUBLIC_API_URL
   ```
   - Enter your backend API URL (e.g., `https://your-backend.railway.app/api`)
   - Select all environments (Production, Preview, Development)

4. **Deploy to preview:**
   ```bash
   vercel
   ```
   This creates a preview deployment.

5. **Deploy to production:**
   ```bash
   vercel --prod
   ```

### Option 2: Deploy from Root (Monorepo)

1. **Create `vercel.json` in project root:**
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "frontend/package.json",
         "use": "@vercel/next"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "frontend/$1"
       }
     ],
     "installCommand": "cd frontend && npm install",
     "buildCommand": "cd frontend && npm run build",
     "outputDirectory": "frontend/.next"
   }
   ```

2. **From project root, run:**
   ```bash
   vercel --prod
   ```

## Environment Variables

Set these in Vercel Dashboard or via CLI:

```bash
vercel env add NEXT_PUBLIC_API_URL production
```

**Required Environment Variables:**
- `NEXT_PUBLIC_API_URL` - Your backend API URL (e.g., `https://your-backend.railway.app/api`)

**Note:** Update `frontend/lib/api.ts` to use this environment variable (already configured).

## Backend Deployment Options

Since Vercel is optimized for serverless functions and your backend is FastAPI, you have these options:

### Option 1: Deploy Backend Separately (Recommended)

**Railway:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize
cd backend
railway init

# Deploy
railway up
```

**Render:**
- Connect your GitHub repo
- Set service type to "Web Service"
- Build command: `cd backend && pip install -r requirements.txt`
- Start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Add environment variables

**Fly.io:**
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch (from backend directory)
cd backend
fly launch
```

### Option 2: Convert FastAPI to Vercel Serverless Functions

1. Create `api/` directory in `frontend/`
2. Convert FastAPI routes to serverless functions
3. More complex, but keeps everything on Vercel

## Quick Deploy Commands

```bash
# Preview deployment
vercel

# Production deployment
vercel --prod

# View deployment URL
vercel ls

# View logs
vercel logs

# Remove deployment
vercel remove [deployment-url]
```

## Configuration Files

### Recommended `vercel.json` (in frontend directory):

```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "installCommand": "npm install",
  "env": {
    "NEXT_PUBLIC_API_URL": "@next_public_api_url"
  }
}
```

### Or create `.vercelignore` (optional):

```
node_modules
.next
.env.local
.env*.local
```

## Troubleshooting

1. **Build fails:** Check Node.js version in `package.json` (Vercel uses Node 18 by default)
2. **API errors:** Ensure `NEXT_PUBLIC_API_URL` is set correctly
3. **Environment variables:** Use Vercel dashboard for easier management
4. **Monorepo issues:** Ensure `vercel.json` points to correct directories

## Post-Deployment

1. Update your backend CORS settings to allow your Vercel domain
2. Test all API endpoints
3. Set up custom domain (optional) via Vercel dashboard
