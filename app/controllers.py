from fastapi import FastAPI, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.models.schemas import QueryRequest, QueryResponse, UploadRequest, UploadResponse
from app.conf.config import Config
from app.conf.llm_conf import LLMConf
from app.conf.db_conf import ChromaDBConf
from app.conf.log_conf import LogConf
from app.services.query_service import QueryService
from llm_service.chatOAagent import ChatOpenAIAgent
from db.chroma_db import ChromaDB
from db.log_db import LogData
from pipeline_service.ingest import Ingest
from pipeline_service.process import Process
from pipeline_service.store import Store
from pipeline_service.pipeline import Pipeline
from app.services.upload_service import UploadService
from llm_service.query import Query

API_VERSION = "v1"

app = FastAPI(
    title="RAG System API",
    description="API for querying LLM with RAG and uploading documents",
    version=API_VERSION
)

config = Config

llm_conf = LLMConf(config)
chat_openai_agent = ChatOpenAIAgent(llm_conf)

chroma_db_conf = ChromaDBConf(config)
chroma_db = ChromaDB(chroma_db_conf)

log_conf = LogConf(config)
log_data = LogData(log_conf)

# Static and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Root renders Home page
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get(f"/add-document")
async def add_document(request: Request):
    return templates.TemplateResponse("add_document.html", {"request": request})

@app.post(f"api/{API_VERSION}/query")
async def query_llm(request: QueryRequest, stream_mode: bool = False):
    query = Query(chat_openai_agent, chroma_db, config)
    query_service = QueryService(query, log_data)
    return query_service.query_svc(request.query, stream_mode)

@app.post(f"api/{API_VERSION}/upload")
async def upload_document(file: UploadFile = File(...)):
    ingestor = Ingest()
    processor = Process(config)
    store = Store(chroma_db)
    pipeline = Pipeline(ingestor, processor, store, log_data)
    upload_service = UploadService(pipeline, log_data)
    run_id = await upload_service.upload_svc(file)

    return UploadResponse(run_id=run_id)

@app.get(f"/health")
def health_check():
    return {"status": "ok"}