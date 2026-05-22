import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const BASE_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:5000";

  const uploadFile = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      // Swapped hardcoded path with operational backend variable
      const res = await axios.post(`${BASE_URL}/upload`, formData);
      alert(res.data.message || "File uploaded successfully");
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    }
  };

  const askQuestion = async () => {
    if (!question.trim()) return;

    const userMessage = {
      type: "user",
      text: question
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const res = await axios.post(`${BASE_URL}/query`, {
        question
      });

      const aiMessage = {
        type: "ai",
        text: res.data.answer
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [
        ...prev,
        {
          type: "ai",
          text: "Error getting response"
        }
      ]);
    }

    setQuestion("");
    setLoading(false);
  };

  return (
    <div className="app">
      <div className="sidebar">
        <div className="logo">AI Assistant</div>
        <div className="uploadBox">
          <input type="file" onChange={(e) => setFile(e.target.files[0])} />
          <button onClick={uploadFile}>Upload File</button>
        </div>
        <div className="history">
          <h3>Recent Topics</h3>
          <div className="historyItem">NLP</div>
          <div className="historyItem">Regex</div>
          <div className="historyItem">Tokenization</div>
        </div>
      </div>

      <div className="main">
        <div className="header">
          <h1>AI Student Assistant</h1>
          <p>Upload documents and ask questions</p>
        </div>

        <div className="chatContainer">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.type}`}>
              {msg.text}
            </div>
          ))}
          {loading && <div className="message ai">Thinking...</div>}
        </div>

        <div className="inputArea">
          <textarea
            placeholder="Ask anything..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <button onClick={askQuestion}>Send</button>
        </div>
      </div>
    </div>
  );
}

export default App;