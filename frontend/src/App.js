import React, { useState } from "react";
import axios from "axios";
import "./App.css";

const API = "http://127.0.0.1:8000/api/";

function App() {
  const [file, setFile] = useState(null);
  const [filename, setFilename] = useState("");
  const [query, setQuery] = useState("");
  const [output, setOutput] = useState("");
  const [page, setPage] = useState("");
  const [loading, setLoading] = useState(false);

  // ================= UPLOAD =================
  const uploadPDF = async () => {
    if (!file) return alert("Select PDF");

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      const res = await axios.post(API + "upload/", formData);
      setFilename(res.data.filename);
      alert("PDF uploaded successfully");
    } catch {
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  // ================= BUILD FAISS =================
  const buildIndex = async () => {
    if (!filename) return alert("Upload PDF first");

    try {
      setLoading(true);
      await axios.post(API + "index-pdf/", { filename });
      alert("FAISS index built");
    } catch {
      alert("FAISS build failed");
    } finally {
      setLoading(false);
    }
  };

  // ================= AI SUMMARY =================
  const aiSummary = async () => {
    if (!filename) return alert("Upload PDF first");

    try {
      setLoading(true);
      const res = await axios.post(API + "ai-summary/", { filename });
      setOutput(res.data.ai_summary || res.data.error);
    } catch {
      alert("AI summary failed");
    } finally {
      setLoading(false);
    }
  };

  // ================= SEMANTIC SEARCH =================
  const semanticSearch = async () => {
    if (!query.trim()) return alert("Enter a question");

    try {
      setLoading(true);
      const res = await axios.post(
        API + "semantic-search/",
        { query },
        { headers: { "Content-Type": "application/json" } }
      );

      let text = "🔍 MATCHED CONTENT:\n\n";

      res.data.results.forEach((item, i) => {
        text += `${i + 1}. ${item}\n\n`;
      });

      text += "\n🧠 SUMMARY:\n\n" + res.data.summary;

      setOutput(text);
    } catch {
      alert("Semantic search failed");
    } finally {
      setLoading(false);
    }
  };

  // ================= SPLIT PDF =================
  const splitPDF = async () => {
    if (!filename) return alert("Upload PDF first");
    if (!page) return alert("Enter page number");

    try {
      setLoading(true);
      const res = await axios.post(API + "split/", {
        filename: filename,
        page: page
      });

      setOutput(
        "✅ PDF SPLIT SUCCESSFULLY\n\n" +
        "Part 1: " + res.data.file_part_1 + "\n" +
        "Part 2: " + res.data.file_part_2
      );
    } catch {
      alert("Split failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="dashboard-card">

        <h2 className="dashboard-title">
          📘 AI PDF Analyzer
        </h2>

        {/* Upload */}
        <div className="upload-center">
          <label className="upload-box">
            Click to upload PDF
            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => setFile(e.target.files[0])}
            />
          </label>

          {file && <div className="file-name">{file.name}</div>}

          <button className="primary-btn" onClick={uploadPDF}>
            Upload PDF
          </button>
        </div>

        {/* Buttons */}
        <div className="action-grid">
          <button onClick={aiSummary}>AI Summary</button>
          <button onClick={buildIndex}>Build FAISS</button>
        </div>

        <hr />

        {/* Semantic Search */}
        <div className="semantic-section">
          <h3>🔍 Semantic Search</h3>

          <div className="semantic-row">
            <input
              type="text"
              placeholder="Ask question from document..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button onClick={semanticSearch}>Search</button>
          </div>
        </div>

        <hr />

        {/* Split PDF */}
        <div className="split-section">
          <input
            type="number"
            placeholder="Split after page number"
            value={page}
            onChange={(e) => setPage(e.target.value)}
          />
          <button onClick={splitPDF}>Split PDF</button>
        </div>

        {/* Output */}
        <div className="output-box">
          <h3>📄 Output</h3>
          {loading ? <p>Processing...</p> : <pre>{output}</pre>}
        </div>

      </div>
    </div>
  );
}

export default App;
