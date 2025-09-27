import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from agent import CSVAnalysisAgent

# Cria diretório files se não existir
if not os.path.exists("files"):
    os.makedirs("files")

app = FastAPI(title="CSV Analysis Agent API")
agent = CSVAnalysisAgent()

@app.get("/")
def root():
    return {"message": "API CSV Analysis Agent está funcionando!"}

# Endpoint de upload de CSV
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_path = os.path.join("files", file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if agent.load_file(file_path):
            return {"message": f"Arquivo '{file.filename}' carregado com sucesso!", "filename": file.filename}
        else:
            return JSONResponse(status_code=400, content={"message": "Erro ao carregar o arquivo."})
    except Exception as e:
        return JSONResponse(status_code=400, content={"message": f"Erro: {str(e)}"})

# Endpoint para perguntar sobre o CSV
@app.post("/ask")
def ask(pergunta: str = Form(...)):
    response = agent.analyze_csv(pergunta)
    return {"response": response}

# Endpoint para ver qual arquivo está carregado
@app.get("/current")
def current_file():
    if agent.current_file:
        return {"current_file": agent.current_file}
    return {"current_file": None, "message": "Nenhum arquivo carregado."}
