# bedrock-agent-starter landing

Static landing page for the portfolio project. It intentionally has no runtime
dependencies, which keeps the public repo easy to audit and deploy.

```bash
npm run lint
npm run build
npm run dev
```

## Deploy on Vercel

The repo includes `.github/workflows/vercel.yml` for GitHub Actions based deploys.
Configure these repository secrets before enabling production deploys:

- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`
