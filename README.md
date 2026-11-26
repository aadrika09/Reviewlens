# ReviewLens

ReviewLens tells you whether a product is right for **your** needs, not the average buyer's. Enter a product, what you need from it and why you're buying it. The app analyses online reviews and returns a feature-by-feature breakdown with a final buy / maybe / skip verdict.

## Features

- **Two-page flow:** a home page with the input form and a result page with the analysis.
- **Personalised verdict:** a fit score and a clear answer on whether the product matches your requirement and reason to buy.
- **Feature breakdown:** scores and one-line summaries for the features that matter to you.
- **Pros and cons:** what reviewers love and what they complain about.
- **Dark icy-blue design** with an animated background, a progress ring and score bars.

## Tech stack

| Layer | Technology |
| --- | --- |
| Frontend | HTML, CSS, vanilla JavaScript |
| Gateway server | Node.js, Express |
| Analysis service | Python, FastAPI |
| AI | Google Gemini API (with Google Search grounding) |

## How it works

```
Browser  ->  Node/Express (port 3000)  ->  FastAPI (port 8000)  ->  Gemini API
             serves the frontend           builds the prompt,
             validates /api/analyze        parses the JSON result
```

## Project structure

```
reviewlens
├── frontend
│   ├── index.html        # home page (input form)
│   ├── result.html       # result page
│   └── style.css
├── node-server
│   ├── server.js         # Express gateway + static file server
│   └── package.json
├── fastapi-service
│   ├── main.py           # analysis service
│   ├── requirements.txt
│   └── .env.example
├── .gitignore
└── README.md
```

## Getting started

### Requirements

- Node.js 18 or newer
- Python 3.9 or newer
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/reviewlens.git
cd reviewlens
```

### 2. Start the FastAPI service

```bash
cd fastapi-service
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

Copy `.env.example` to a new file named `.env` and add your key:

```
GEMINI_API_KEY=your_real_key_here
```

Then run the service:

```bash
uvicorn main:app --port 8000
```

Open http://127.0.0.1:8000 to check it. You should see `"gemini_key_loaded": true`.

### 3. Start the Node server

In a second terminal:

```bash
cd node-server
npm install
npm start
```

### 4. Open the app

Go to **http://localhost:3000**, fill in the form and click **Analyse reviews**. The analysis takes about 10 to 30 seconds.

## API

| Method | Endpoint | Service | Description |
| --- | --- | --- | --- |
| `POST` | `/api/analyze` | Node | Validates the form and forwards it to FastAPI |
| `POST` | `/analyze` | FastAPI | Runs the review analysis and returns JSON |
| `GET` | `/health` | FastAPI | Reports whether the service and API key are loaded |

Example request body:

```json
{
  "brand": "Sony",
  "name": "WH-1000XM5",
  "requirement": "Strong noise cancelling for commuting",
  "reason": "My earphones broke and I am on calls all day"
}
```

You can also try the analysis directly at http://127.0.0.1:8000/docs.

## Configuration

| Variable | Where | Default | Purpose |
| --- | --- | --- | --- |
| `GEMINI_API_KEY` | `fastapi-service/.env` | none | Your Gemini API key (required) |
| `GEMINI_MODEL` | environment | `gemini-2.5-flash` | Gemini model to use |
| `FASTAPI_URL` | environment | `http://127.0.0.1:8000` | Where the Node server finds FastAPI |
| `PORT` | environment | `3000` | Port for the Node server |

## Notes and limitations

- Results depend on what Gemini finds. If live search is unavailable on your plan, the service falls back to the model's general knowledge, and the result page says so.
- The free Gemini tier has rate limits. If you see a quota error, wait a minute and try again.
- Scores are AI-generated estimates and are not a substitute for reading reviews yourself.
- Never commit your `.env` file. It is listed in `.gitignore`.

## Roadmap

- Saved analysis history
- Side-by-side comparison of two products
- Support for more review sources

## License

Add a license of your choice, for example MIT, before sharing the project publicly.
