import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function App() {
  const [file, setFile] = useState(null);
  const [filename, setFilename] = useState('');
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [history, setHistory] = useState([]);
  const [chartData, setChartData] = useState(null);
  const API_URL = import.meta.env.VITE_URL_AGENT_API;
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const loadBackend = async () => {
      try {
        const res = await fetch(`${API_URL}`);
        if (!res.ok) throw new Error('Backend não está acessível');
        console.log('Backend está acessível');
      } catch (err) {
        console.error('Erro ao acessar backend:', err);
        alert('Erro ao acessar backend: ' + err.message);
      }
    };
    loadBackend();
  }, []);

  const handleUpload = async () => {
    if (!file) return;
    setIsLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_URL}/upload`, { method: "POST", body: formData });
      const data = await res.json();

      if (res.ok) {
        setFilename(data.filename);
        alert("Arquivo enviado com sucesso!");
      } else {
        alert("Erro ao enviar arquivo: " + data.message);
      }
    } catch (err) {
      alert("Erro ao enviar arquivo: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAsk = async () => {
    if (!question) return;
    setIsLoading(true);
    const formData = new URLSearchParams();
    formData.append("pergunta", question);

    try {
      const res = await fetch(`${API_URL}/ask`, {
        method: "POST",
        body: formData,
      });

      const contentType = res.headers.get("content-type");

      if (contentType === "image/png") {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "grafico.png";
        document.body.appendChild(link);
        link.click();
        link.remove();
      } else {
        const data = await res.json();
        const ans = data.response;

        let finalAnswer;
        if (ans && typeof ans === "object" && "output" in ans) {
          finalAnswer = ans.output;
        } else {
          finalAnswer = String(ans);
        }

        setResponse(finalAnswer);
        setHistory((prev) => [...prev, { q: question, a: finalAnswer }]);

        try {
          const parsed = JSON.parse(finalAnswer);
          if (Array.isArray(parsed)) setChartData(parsed);
          else setChartData(null);
        } catch {
          setChartData(null);
        }
      }
    } catch (err) {
      alert('Erro ao fazer pergunta: ' + err.message);
    } finally {
      setQuestion("");
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-8 text-center">
          Agent CSV com LangChain + Groq
        </h1>

        {/* Upload CSV */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6 transition-all duration-300 hover:shadow-xl">
          <div className="flex items-center gap-4">
            <input
              type="file"
              accept=".csv"
              className="flex-1 border border-gray-300 rounded-lg p-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              onChange={(e) => setFile(e.target.files[0])}
            />
            <button
              className={`px-6 py-2 rounded-lg font-semibold text-white bg-blue-600 hover:bg-blue-700 transition-colors duration-200 ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              onClick={handleUpload}
              disabled={isLoading}
            >
              {isLoading ? 'Enviando...' : 'Upload CSV'}
            </button>
          </div>
        </div>

        {/* Formulário de perguntas */}
        {filename && (
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-6 transition-all duration-300 hover:shadow-xl">
            <p className="text-gray-700 mb-4">
              <strong>Arquivo atual:</strong> {filename}
            </p>
            <textarea
              className="w-full border border-gray-300 rounded-lg p-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              placeholder="Digite sua pergunta sobre os dados..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              rows={4}
            />
            <button
              className={`mt-4 px-6 py-2 rounded-lg font-semibold text-white bg-green-600 hover:bg-green-700 transition-colors duration-200 ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              onClick={handleAsk}
              disabled={isLoading}
            >
              {isLoading ? 'Aguarde retorno da pesquisa...' : 'Perguntar'}
            </button>
          </div>
        )}

        {/* Resposta */}
        {response && (
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-6 transition-all duration-300 hover:shadow-xl">
            <h5 className="text-lg font-semibold text-gray-800 mb-2">Resposta:</h5>
            <p className="text-gray-600">{response}</p>
          </div>
        )}

        {/* Gráfico */}
        {chartData && (
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-6 transition-all duration-300 hover:shadow-xl">
            <h5 className="text-lg font-semibold text-gray-800 mb-4">Visualização</h5>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey={Object.keys(chartData[0])[0]} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey={Object.keys(chartData[0])[1]} stroke="#2563eb" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Histórico */}
        {history.length > 0 && (
          <div className="bg-white rounded-2xl shadow-lg p-6 transition-all duration-300 hover:shadow-xl">
            <h5 className="text-lg font-semibold text-gray-800 mb-4">Histórico de Perguntas/Respostas</h5>
            {history.map((h, idx) => (
              <div key={idx} className="mb-4 p-4 border border-gray-200 rounded-lg bg-gray-50 transition-all duration-200 hover:bg-gray-100">
                <p className="text-gray-700 mb-1"><strong>P:</strong> {h.q}</p>
                <p className="text-gray-600"><strong>R:</strong> {h.a}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}