import pandas as pd
from langchain_groq.chat_models import ChatGroq  # Substitui ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage

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
        self.agent = create_pandas_dataframe_agent(
                df=self.df,
                llm=self.llm,
                verbose=True,
                max_iterations=3000,
                agent_executor_kwargs={
                    "memory": self.memory,
                    "handle_parsing_errors": True
                },
                allow_dangerous_code=True
            )

    def analyze_csv(self, question: str):
        if not self.agent:
            return {"output": "Nenhum arquivo carregado."}
        try:
            result = self.agent.invoke(question)
            return {"output": result}
        except Exception as e:
            return {"output": f"Erro ao processar a pergunta: {str(e)}"}