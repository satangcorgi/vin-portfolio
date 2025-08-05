# Streamlit Portfolio — Exemplary Work

This is a starter Streamlit app for your portfolio's **Exemplary Work** section.

## Quick start
1. Put your project images (PNGs) into `assets/` using the exact filenames referenced in `projects.json`.
2. Edit `projects.json` to tweak titles, blurbs, tags, and links.
3. Run locally:
   ```
   pip install -r requirements.txt
   streamlit run app.py
   ```
4. Deploy on **Streamlit Community Cloud**:
   - Create a GitHub repo and push these files.
   - Go to https://share.streamlit.io, click **New app**, select your repo, set **main file** to `app.py`.
   - Add a **Secrets** variable `EXTRA` only if needed (not required here).
   - Click **Deploy**.

## Tips
- To add a new work, append an object to `projects.json`.
- Keep blurbs to ~2–3 sentences.
- Use 1200px wide images for crisp but light cards.

Generated: 2025-08-05T15:03:17.433713
