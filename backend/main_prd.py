
from dotenv import load_dotenv
import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from agent import CSVAnalysisAgent
import matplotlib.pyplot as plt
import io

# Load environment variables from the .env file
load_dotenv()

# Criar pasta para arquivos se não existir
if not os.path.exists("files"):
    os.makedirs("files")

# Inicializar agente com Groq API Key
api_key = os.getenv('GROQ_API_KEY')

print("API key")
print(api_key)
agent = CSVAnalysisAgent(key=api_key)

app = FastAPI(title="CSV Analysis Agent API")

# Configuração CORS para permitir requests do React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # porta do React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API CSV Analysis Agent funcionando!"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_path = os.path.join("files", file.filename)
    print("Upload do arquivo")
    try:
        # Salvar arquivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print("Carregar o arquivo")
        # Carregar CSV no agente
        if agent.load_file(file_path):
            return {"message": f"Arquivo '{file.filename}' carregado com sucesso!", "filename": file.filename}
        else:
            return JSONResponse(status_code=400, content={"message": "Erro ao carregar o arquivo."})
    except Exception as e:
        return JSONResponse(status_code=400, content={"message": f"Erro: {str(e)}"})

@app.post("/ask")
async def ask(pergunta: str = Form(...)):
    response = agent.analyze_csv(pergunta)
    print("Resposta do agente:")
    print(response)
    return {"response": response}

@app.get("/current")
def current_file():
    if agent.current_file:
        return {"current_file": agent.current_file}
    return {"current_file": None, "message": "Nenhum arquivo carregado."}

@app.post("/ask_grafico")
def responder(pergunta: str = Form(...)):
    resultado = agente_csv_responder(pergunta)
    print("Resultado do agente:")
    print(resultado)

    if resultado["tipo"] == "texto":
        return JSONResponse(content={"resposta": resultado["resposta"]})
    
    elif resultado["tipo"] == "grafico":
        # 1️⃣ Criar gráfico
        fig, ax = plt.subplots()
        ax.plot(resultado["x"], resultado["y"], marker='o')
        ax.set_title(resultado["titulo"])
        ax.set_xlabel("Eixo X")
        ax.set_ylabel("Eixo Y")

        # 2️⃣ Salvar em memória
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        plt.close(fig)

        # 3️⃣ Retornar imagem para download
        return StreamingResponse(
            buf,
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=grafico.png"}
        )

# Simulação do agente CSV (substitua pela lógica real do seu agente)
def agente_csv_responder(pergunta: str):
    # Se a pergunta contiver "grafico", retornamos dados para gráfico
    if "grafico" in pergunta.lower():
        # Exemplo de dados
        x = [1, 2, 3, 4]
        y = [10, 20, 25, 30]
        titulo = "Exemplo de gráfico de vendas"
        return {"tipo": "grafico", "x": x, "y": y, "titulo": titulo}
    
    # Caso contrário, retornamos texto
    return {"tipo": "texto", "resposta": "Aqui está a resposta do LLM para sua pergunta."}