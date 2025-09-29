import pandas as pd
from langchain_groq import ChatGroq  # Substitui ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.memory import ConversationBufferMemory

class CSVAnalysisAgent:
    def __init__(self, key: str):
        self.current_file = None
        self.df = None
        self.agent = None

        # Inicializando ChatGroq como o único LLM
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",  # Modelo Groq, verifique disponibilidade
            temperature=0,
            api_key=key,
            # base_url removido, usa o padrão https://api.groq.com/openai/v1
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", 
            return_messages=True
        )

    def load_file(self, file_path: str):
        try:
            self.df = pd.read_csv(file_path)
            self.current_file = file_path

            # Cria o agente usando apenas o LLM Groq
            self.agent = create_pandas_dataframe_agent(
                df=self.df,
                llm=self.llm,
                verbose=True,
                agent_executor_kwargs={"memory": self.memory},
                allow_dangerous_code=True
            )
            return True
        except Exception as e:
            print("Erro ao carregar CSV:", e)
            return False

    def analyze_csv(self, question: str):
        if not self.agent:
            return {"output": "Nenhum arquivo carregado."}
        try:
            result = self.agent.invoke(question)
            return {"output": result}
        except Exception as e:
            return {"output": f"Erro ao processar a pergunta analyze_csv: {str(e)}"}