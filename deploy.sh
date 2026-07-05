#!/usr/bin/env bash
# deploy.sh — one-command deployment for Polyglot AI Studio backend
# Run this on your DigitalOcean / Oracle Cloud server after first-time setup.
#
# First-time setup (run once on a fresh Ubuntu 22.04 droplet):
#   curl -fsSL https://get.docker.com | sh
#   usermod -aG docker $USER   # then log out and back in
#   git clone https://github.com/YOUR_ORG/polyglot-agent.git
#   cd polyglot-agent
#   cp .env.production.example .env.production
#   nano .env.production          # fill in DATABASE_URL_OVERRIDE, SECRET_KEY, FRONTEND_URL
#   ./deploy.sh

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "========================================"
echo "  Polyglot AI Studio — Deploy"
echo "========================================"

# Pull latest code
echo ""
echo "[1/4] Pulling latest code..."
git pull origin main

# Build backend image
echo ""
echo "[2/4] Building backend Docker image..."
docker compose build backend

# Restart services (zero-downtime swap via Docker Compose recreate)
echo ""
echo "[3/4] Restarting services..."
docker compose up -d --remove-orphans

# Show running containers
echo ""
echo "[4/4] Running containers:"
docker compose ps

echo ""
echo "========================================"
echo "  Deploy complete!"
echo "========================================"
echo ""
echo "Useful commands:"
echo "  docker compose logs -f backend   # tail backend logs"
echo "  docker compose logs -f nginx     # tail nginx logs"
echo "  docker compose down              # stop everything"
echo ""
echo "NOTE: On first deploy, HuggingFace models (~3 GB) download"
echo "      automatically. This takes 10-15 min. Watch progress:"
echo "        docker compose logs -f backend"
echo ""
