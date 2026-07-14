# Contributing to Autonomous System Kernel (A.S.K.)

Thanks for contributing.

## Development setup

```bash
git clone https://github.com/askmy-stack/Autonomous-System-Kernel
cd Autonomous-System-Kernel

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env   # if present

# Frontend
cd ../frontend
npm ci
```

## Running checks

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm run lint && npx tsc --noEmit && npm run build
```

## Pull request guidelines

- Keep changes focused and tested
- Do not commit secrets or `.env` files
- Prefer small PRs that reference an issue (`Fixes #N`)
- For security-sensitive changes, see [SECURITY.md](SECURITY.md)

## Good first issues

Browse issues labeled `good first issue`.
