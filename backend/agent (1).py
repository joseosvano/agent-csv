import os
import logging
from typing import List
from langchain_experimental.agents import create_csv_agent
from langchain_openai import OpenAI
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

AGENT_PROMPT = """
Você é um agente fiscal especializado em análise de arquivos CSV.
Responda apenas perguntas relacionadas aos dados do arquivo CSV carregado.
Se a pergunta não for sobre o conteúdo do CSV, responda exatamente:
"Sou exclusivamente um agente fiscal que lê e analisa arquivos CSV. Por favor, faça perguntas relacionadas aos dados carregados."
Sempre responda em português do Brasil.
Ao analisar os dados, seja claro e objetivo.
Se encontrar valores numéricos, apresente-os de forma organizada.
Se precisar fazer cálculos, explique o processo.
O arquivo CSV já está carregado e disponível para análise.
Não tente carregar o arquivo novamente, apenas analise os dados que já estão disponíveis.
"""

class CSVAnalysisAgent:
    def __init__(self):
        load_dotenv()
        try:
            logger.info("Inicializando conexão com OpenAI...")
            self.llm = OpenAI(temperature=0)
            # Testa a conexão fazendo uma chamada simples
            self.llm.invoke("teste")
            logger.info("Conexão com OpenAI estabelecida com sucesso!")
            self.agent = None
            self.current_file = None
        except Exception as e:
            logger.error(f"Erro ao conectar com OpenAI: {str(e)}")
            raise
    
    def _find_file_case_insensitive(self, directory: str, filename: str) -> str:
        """
        Encontra um arquivo no diretório independente de maiúsculas/minúsculas.
        
        Args:
            directory (str): Diretório onde procurar
            filename (str): Nome do arquivo a procurar
            
        Returns:
            str: Caminho completo do arquivo se encontrado, None caso contrário
        """
        try:
            # Lista todos os arquivos no diretório
            files = os.listdir(directory)
            
            # Procura o arquivo ignorando maiúsculas/minúsculas
            for file in files:
                if file.lower() == filename.lower():
                    return os.path.join(directory, file)
            
            return None
        except Exception as e:
            logger.error(f"Erro ao procurar arquivo: {str(e)}")
            return None
    
    def load_file(self, file_path: str) -> bool:
        """
        Carrega um arquivo CSV e prepara o agente para análise.
        
        Args:
            file_path (str): Caminho para o arquivo CSV
            
        Returns:
            bool: True se o arquivo foi carregado com sucesso, False caso contrário
        """
        try:
            # Extrai o diretório e nome do arquivo
            directory = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            
            # Procura o arquivo ignorando maiúsculas/minúsculas
            actual_file_path = self._find_file_case_insensitive(directory, filename)
            
            if actual_file_path is None:
                logger.error(f"Arquivo não encontrado: {file_path}")
                return False
            
            logger.info(f"Carregando arquivo: {actual_file_path}")
            
            # Cria o agente para análise do CSV com o prompt em português
            self.agent = create_csv_agent(
                llm=self.llm,
                path=actual_file_path,
                verbose=True,
                prefix=AGENT_PROMPT
            )
            
            self.current_file = actual_file_path
            logger.info("Arquivo carregado com sucesso!")
            return True
            
        except Exception as e:
            error_msg = f"Erro ao carregar o arquivo: {str(e)}"
            logger.error(error_msg)
            return False
        
    def analyze_csv(self, question: str) -> str:
        """
        Analisa o arquivo CSV carregado e responde uma pergunta sobre seu conteúdo.
        
        Args:
            question (str): Pergunta sobre o conteúdo do CSV
            
        Returns:
            str: Resposta baseada no conteúdo do CSV
        """
        try:
            if self.agent is None:
                return "Erro: Nenhum arquivo CSV foi carregado. Use o comando 'carregar' primeiro."
            
            logger.info(f"Pergunta sobre {self.current_file}: {question}")
            
            # Executa a análise e retorna a resposta
            response = self.agent.invoke(question)
            logger.info("Análise concluída com sucesso!")
            return response
            
        except Exception as e:
            error_msg = f"Erro ao analisar o arquivo: {str(e)}"
            logger.error(error_msg)
            return error_msg 