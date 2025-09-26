import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function App() {
  const [file, setFile] = useState(null);
  const [filename, setFilename] = useState('');
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [history, setHistory] = useState([]);
  const [chartData, setChartData] = useState(null);

  // Upload CSV
  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8001/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();

      if (res.ok) {
        setFilename(data.filename);  // ativa o formulário de perguntas
        alert('Arquivo enviado com sucesso!');
      } else {
        alert('Erro ao enviar arquivo: ' + data.message);
      }
    } catch (err) {
      alert('Erro ao enviar arquivo: ' + err.message);
    }
  };

  // Fazer pergunta à LLM
  const handleAsk = async () => {
    if (!question) return;

    try {
      const res = await fetch('http://localhost:8001/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ pergunta: question }),
      });

      const data = await res.json();
      const ans = data.response.output;
      setResponse(ans);
      setHistory(prev => [...prev, { q: question, a: ans }]);
      setQuestion('');

      // Tenta interpretar JSON para gráficos
      try {
        const parsed = JSON.parse(ans);
        if (Array.isArray(parsed)) {
          setChartData(parsed);
        } else {
          setChartData(null);
        }
      } catch {
        setChartData(null);
      }

    } catch (err) {
      alert('Erro ao fazer pergunta: ' + err.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center p-6">
      <h1 className="text-2xl font-bold mb-4">EDA CSV com LangChain + Groq</h1>

      {/* Upload CSV */}
      <div className="bg-white p-4 rounded-2xl shadow-md w-full max-w-lg mb-6 flex items-center">
        <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} />
        <button onClick={handleUpload} className="ml-2 px-4 py-2 bg-blue-600 text-white rounded-2xl shadow">
          Upload CSV
        </button>
      </div>

      {/* Formulário de perguntas (aparece só depois do upload) */}
      {filename && (
        <div className="bg-white p-4 rounded-2xl shadow-md w-full max-w-lg mb-6">
          <p className="mb-2">Arquivo atual: <strong>{filename}</strong></p>
          <textarea
            className="w-full p-2 border rounded mb-2"
            placeholder="Digite sua pergunta sobre os dados..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <button onClick={handleAsk} className="px-4 py-2 bg-green-600 text-white rounded-2xl shadow">
            Perguntar
          </button>
        </div>
      )}

      {/* Resposta */}
      {response && (
        <div className="bg-white p-4 rounded-2xl shadow-md w-full max-w-lg mb-6">
          <h2 className="text-xl font-semibold mb-2">Resposta:</h2>
          <p>{response}</p>
        </div>
      )}

      {/* Gráfico se houver dados tabulares */}
      {chartData && (
        <div className="bg-white p-4 rounded-2xl shadow-md w-full max-w-2xl mb-6">
          <h2 className="text-xl font-semibold mb-2">Visualização</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={Object.keys(chartData[0])[0]} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey={Object.keys(chartData[0])[1]} stroke="#8884d8" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Histórico de perguntas/respostas */}
      {history.length > 0 && (
        <div className="bg-white p-4 rounded-2xl shadow-md w-full max-w-lg">
          <h2 className="text-xl font-semibold mb-2">Histórico</h2>
          {history.map((h, idx) => (
            <div key={idx} className="mb-2">
              <p className="font-semibold">Pergunta: {h.q}</p>
              <p>Resposta: {h.a}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
