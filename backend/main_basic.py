from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
from langchain_groq import ChatGroq  # Substitui ChatOpenAI
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

# Configuração CORS para permitir requests do React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # porta do React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
api_key = os.getenv('GROQ_API_KEY')  # Substitui OPENAI_API_KEY

llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",  # Modelo disponível no Groq em set/2025
    temperature=0,
    api_key=api_key,
    # base_url não é necessário, pois a API do Groq usa o endpoint padrão
)

csv_df = None
csv_filename = None

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    global csv_df, csv_filename
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(path, "wb") as f:
        f.write(await file.read())
    csv_df = pd.read_csv(path)
    csv_filename = file.filename
    return {"filename": file.filename}

def is_graph_request(question: str):
    """Detecta se a pergunta indica gráfico/imagem"""
    q = question.lower()
    keywords = ["gráfico", "grafico", "graphic", "imagem", "image"]
    return any(word in q for word in keywords)

def generate_auto_chart(df: pd.DataFrame):
    """Gera gráfico automático de acordo com colunas numéricas"""
    plt.figure(figsize=(6,4))
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    
    if len(numeric_cols) >= 2:
        x_col, y_col = numeric_cols[:2]
        plt.plot(df[x_col], df[y_col], marker='o', linestyle='-', color='blue')
    elif len(numeric_cols) == 1:
        y_col = numeric_cols[0]
        plt.bar(df.index, df[y_col], color='green')
        x_col = df.index.name if df.index.name else "Index"
    else:
        x_col, y_col = df.columns[:2]
        plt.scatter(df[x_col], df[y_col], color='red')

    plt.title("Gráfico automático")
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.grid(True)

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf

@app.post("/ask")
async def ask(pergunta: str = Form(...)):
    global csv_df
    if csv_df is None:
        return JSONResponse(content={"response": "Nenhum CSV carregado ainda."})

    try:
        # Se a pergunta for sobre gráfico, gera gráfico automático
        if is_graph_request(pergunta):
            buf = generate_auto_chart(csv_df)
            return StreamingResponse(
                buf,
                media_type="image/png",
                headers={"Content-Disposition": "attachment; filename=grafico.png"}
            )

        # Caso contrário, chama Grok diretamente
        prompt = f"""
Você é um assistente que responde perguntas sobre dados de CSV.
Se a pergunta pedir gráfico, responda apenas com JSON no formato:
[{{"x": "Seg", "y": 100}}, {{"x": "Ter", "y": 150}}]
Nunca gere código Python.
Pergunta: {pergunta}
Dados do CSV: {json.dumps(csv_df.to_dict())}  # Inclui dados para contexto
"""

        resposta_texto = llm.invoke(prompt).content  # Usa .invoke() em vez de .predict()

        # Tentar parsear como JSON se for gráfico
        try:
            resposta_json = json.loads(resposta_texto)
            return JSONResponse(content={"response": resposta_texto})
        except json.JSONDecodeError:
            return JSONResponse(content={"response": resposta_texto})

    except Exception as e:
        return JSONResponse(content={"response": f"Erro ao processar a pergunta: {str(e)}"})