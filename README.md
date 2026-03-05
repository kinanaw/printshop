# 🗺️ Blueprint Roll Organizer

A Streamlit web app for print shops that automates PDF blueprint sorting, trimming, and paper usage calculation.

## Features

- **Upload multiple PDFs** of blueprints at once
- **Auto-categorize** by roll width:
  - PDFs ≤ 60 cm wide → merged into `60cm_roll.pdf`
  - PDFs > 60 cm wide → merged into `91cm_roll.pdf`
- **Smart rotation** — if a PDF is landscape and rotating it fits the 60 cm roll, it's rotated automatically
- **Bleed trimming** — white margins are trimmed from each PDF before processing (falls back gracefully if ambiguous)
- **Paper calculation** — shows total meters of paper needed per roll
- **Download** the merged PDFs directly from the browser

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/blueprint-roll-organizer.git
cd blueprint-roll-organizer
pip install -r requirements.txt
streamlit run app.py
```

## Libraries Used

| Library | Purpose |
|--------|---------|
| `streamlit` | Web interface |
| `pypdf` | PDF merging & page manipulation |
| `PyMuPDF (fitz)` | Bleed trimming via pixel analysis |
| `Pillow` | Image processing for trim detection |
| `numpy` | Pixel array math for bounding box |
| `pandas` | File summary table display |

## How It Works

1. Upload any number of PDF blueprint files
2. The app reads each PDF's MediaBox dimensions
3. White bleed areas are trimmed by rendering the page at low resolution, finding non-white pixel bounds, and setting a new CropBox
4. Each PDF is sorted: width ≤ 60 cm (either orientation) → narrow roll; otherwise → wide roll
5. Files are merged into two output PDFs (one per roll)
6. Total paper meters are calculated by summing the length dimension of all pages per roll

## Deployment (Streamlit Community Cloud)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set `app.py` as the entry point
5. Click **Deploy**

No additional configuration needed — `requirements.txt` handles all dependencies.

## Notes

- All PDFs are assumed to be single-page blueprints (first page is used for dimension detection)
- Rotation is applied only when it helps a PDF fit the 60 cm roll
- Trimming is conservative: if savings < 5% of area, original dimensions are preserved
