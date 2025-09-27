import pandas as pd
from langchain_groq.chat_models import ChatGroq
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage
import pandas as pd

class CSVAnalysisAgent:
    def __init__(self, key: str):
        self.current_file = None
        self.df = None
        self.agent = None

        # Inicializando ChatOpenAI para Groq
        self.llm_groq = ChatGroq(
            model="llama-3.3-70b-versatile",                    # modelo Groq
            temperature=0,
            api_key=key,
            base_url="https://api.groq.com"
        )

        self.llm = ChatOpenAI(
            model="gpt-4.1-nano",
            temperature=0,
            api_key=key,
            base_url="https://api.openai.com/v1"
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", 
            return_messages=True
        )

        self.llm_awa = ChatOpenAI(
            model="Meta-Llama-3-8B-Instruct",                    # modelo Groq
            temperature=0,
            api_key=key,
            base_url="https://api.awanllm.com/v1"
        )

    def load_file(self, file_path: str):
        import pandas as pd
        try:
            self.df = pd.read_csv(file_path)
            self.current_file = file_path

            # ⚠️ df primeiro, llm segundo, sem nomear
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
            return {"output": f"Erro ao processar a pergunta: {str(e)}"}
