import pandas as pd
from langchain_groq import ChatGroq
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.memory import ConversationBufferMemory
import json

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
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", 
            return_messages=True
        )

    def load_file(self, file_path: str):
        try:
            self.df = pd.read_csv(file_path)
            self.current_file = file_path

            # Cria o agente usando apenas o LLM Groq com handle_parsing_errors
            self.agent = create_pandas_dataframe_agent(
                df=self.df,
                llm=self.llm,
                verbose=True,
                agent_executor_kwargs={"memory": self.memory, "handle_parsing_errors": True},
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
            # Invoca o agente com a pergunta
            result = self.agent.invoke(question)

            # Tenta extrair o conteúdo útil da resposta
            if hasattr(result, 'content'):
                output_content = result.content
            elif isinstance(result, dict) and 'output' in result:
                output_content = result['output']
            else:
                output_content = str(result)

            # Validação da saída: remove erros de parsing e metadados
            cleaned_output = self._clean_output(output_content)
            if cleaned_output:
                return {"output": cleaned_output}
            else:
                return {"output": "Resposta não processável. Por favor, faça uma pergunta específica sobre o CSV."}

        except Exception as e:
            # Captura erros e tenta extrair uma mensagem útil
            error_msg = str(e)
            cleaned_error = self._clean_output(error_msg)
            if cleaned_error:
                return {"output": cleaned_error}
            return {"output": f"Erro ao processar a pergunta: {str(e)}"}

    def _clean_output(self, output_str: str):
        """
        Limpa a saída removendo mensagens de erro de parsing e metadados.
        Retorna apenas o conteúdo útil ou None se inválido.
        """
        # Remove mensagens de erro de parsing padrão do LangChain
        if "An output parsing error occurred" in output_str:
            # Extrai o texto após o erro, se presente
            match = re.search(r"Could not parse LLM output: `(.*?)`", output_str, re.DOTALL)
            if match:
                return match.group(1).strip()
            return None
        
        # Remove URLs de troubleshooting
        output_str = re.sub(r"For troubleshooting, visit: https://.*", "", output_str).strip()

        # Remove quebras de linha excessivas e espaços
        output_str = re.sub(r"\s+", " ", output_str).strip()

        # Verifica se há conteúdo significativo
        if output_str and not output_str.startswith("Erro") and len(output_str.split()) > 1:
            return output_str
        return None
