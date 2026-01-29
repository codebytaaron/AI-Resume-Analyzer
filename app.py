from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from analyzer.pdf_extract import extract_text
from analyzer.report import analyze_resume

app = FastAPI(title="AI Resume Analyzer")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    resume: UploadFile,
    job_description: str = Form(default="")
):
    text = extract_text(await resume.read())
    report = analyze_resume(text, job_description)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "report": report
        }
    )
