from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from api.routes import brand, generate, history, playbooks, tracker

WEB_DIST = Path(__file__).resolve().parents[2] / "web" / "dist"

app = FastAPI(title="Reddit Comment Console", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brand.router)
app.include_router(playbooks.router)
app.include_router(generate.router)
app.include_router(history.router)
app.include_router(tracker.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


if WEB_DIST.exists():
    app.mount("/", StaticFiles(directory=WEB_DIST, html=True), name="web")
else:

    @app.get("/")
    def dev_console_notice():
        return HTMLResponse(
            """
            <!doctype html>
            <html>
              <head><title>Reddit Comment Console</title></head>
              <body style="font-family: system-ui; max-width: 520px; margin: 2rem auto;">
                <h1>API is running</h1>
                <p>The web UI is a separate dev server. In a second terminal:</p>
                <pre style="background:#f4f4f0;padding:1rem;border-radius:8px;">cd web && npm run dev</pre>
                <p>Then open <a href="http://localhost:5173">http://localhost:5173</a></p>
                <p class="muted">Or build once and use a single URL:<br>
                <code>cd web && npm run build</code> then reload this page.</p>
              </body>
            </html>
            """
        )


def run():
    import uvicorn

    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)