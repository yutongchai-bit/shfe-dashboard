# SHFE Broker OI vs Physical Premium — self-updating dashboard

A static web page (`index.html`) showing SHFE top-20 broker positioning vs a physical-premium
proxy for copper/aluminum/zinc, rebuilt automatically every weekday evening by GitHub Actions.

## One-time setup (about 3 minutes)

1. Sign in to github.com, click **New repository**. Name it anything (e.g. `shfe-dashboard`).
   Choose **Private** if only invited people should see it, or Public for anyone with the link.
   Note: GitHub Pages on a private repo requires a paid plan; on a free plan use a public repo.
2. Upload the entire contents of this folder to the repo (drag-and-drop works on github.com:
   "uploading an existing file"). Make sure the `.github/workflows/daily.yml` file is included
   (enable "show hidden files" when selecting).
3. In the repo: **Settings → Pages → Source: Deploy from a branch → main / (root) → Save.**
4. In the repo: **Actions tab → enable workflows** if prompted, then open "Daily SHFE data
   refresh" and press **Run workflow** once to test.
5. Your dashboard is live at `https://<your-username>.github.io/<repo-name>/`
   and refreshes itself every weekday at 18:45 Beijing time.

## What's inside

- `index.html` — the dashboard (already built with data through the packaging date)
- `update_data.py` — fetches latest rankings/settles/front-month boards from EastMoney's
  public API and rebuilds the page
- `scripts/refresh_pipeline.py`, `scripts/artifact_template.html` — build pipeline
- `data/` — master history (preserves expired contracts), tracked broker list, delivery record
- `.github/workflows/daily.yml` — the daily automation

## Maintenance

- To track another broker: add `"名称": "ORG_CODE"` to `data/tracked_brokers.json` (find the
  code by querying the EastMoney API) and run the workflow.
- Premium overlay: viewers can upload their own premium CSV in the page (stored in their browser).

## Notes

- Data source: EastMoney public mirror of SHFE daily top-20 member rankings. Check your firm's
  compliance policy before making redistributed market data publicly accessible; a private repo
  with invited collaborators (or an internal web server) may be more appropriate.
