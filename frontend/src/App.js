import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const BASE_URL = window.location.hostname === "localhost" 
  ? "http://localhost:8000" 
  : "http://13.232.86.221:8000"; 

  const uploadFile = async () => {

    if (!file) {
      alert("Please select a file first");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {

      const res = await axios.post(
        `${BASE_URL}/upload`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      alert(res.data.message);

    } catch (err) {

      console.error(err);

      alert(
        err.response?.data?.error ||
        "File upload failed"
      );
    }
  };

  const askQuestion = async () => {

    if (!question.trim()) return;

    const userMessage = {
      type: "user",
      text: question,
    };

    setMessages((prev) => [...prev, userMessage]);

    setLoading(true);

    try {

      const res = await axios.post(
        `${BASE_URL}/query`,
        {
          question: question,
        }
      );

      const aiMessage = {
        type: "ai",
        text: res.data.answer,
      };

      setMessages((prev) => [...prev, aiMessage]);

    } catch (err) {

      console.error(err);

      setMessages((prev) => [
        ...prev,
        {
          type: "ai",
          text:
            err.response?.data?.error ||
            "Error connecting to FastAPI backend",
        },
      ]);
    }

    setQuestion("");
    setLoading(false);
  };

  return (
    <div className="app">

      {/* Sidebar */}
      <div className="sidebar">

        <div className="logo">
          AI Assistant
        </div>

        <div className="uploadBox">

          <input
            type="file"
            onChange={(e) => setFile(e.target.files[0])}
          />

          <button onClick={uploadFile}>
            Upload File
          </button>

        </div>

      </div>

      {/* Main Content */}
      <div className="main">

        <div className="header">

          <h1>AI Student Assistant</h1>

          <p>
            Upload documents and ask questions
          </p>

        </div>

        {/* Chat */}
        <div className="chatContainer">

          {messages.map((msg, index) => (

            <div
              key={index}
              className={`message ${msg.type}`}
            >
              {msg.text}
            </div>

          ))}

          {loading && (
            <div className="message ai">
              Thinking...
            </div>
          )}

        </div>

        {/* Input */}
        <div className="inputArea">

          <textarea
            placeholder="Ask anything..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />

          <button onClick={askQuestion}>
            Send
          </button>

        </div>

      </div>
    </div>
  );
}

export default App;