import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [documents, setDocuments] = useState([]);
  const [selectedDocs, setSelectedDocs] = useState([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);

  // -------------------------
  // Upload PDF
  // -------------------------

  const uploadFile = async (file) => {
    if (!file) return;

    if (file.type !== "application/pdf") {
      alert("Only PDF files are allowed.");
      return;
    }

    setUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      const newDocument = {
        id: Date.now(),
        name: file.name,
        size: formatFileSize(file.size),
        status: "Active",
      };

      setDocuments((prev) => [...prev, newDocument]);

      setSelectedDocs((prev) => [
        ...prev,
        newDocument.id,
      ]);

    } catch (error) {
      console.error(error);
      alert("Failed to upload document.");
    } finally {
      setUploading(false);
    }
  };

  // -------------------------
  // File input
  // -------------------------

  const handleFileInput = (event) => {
    const file = event.target.files[0];

    if (file) {
      uploadFile(file);
    }
  };

  // -------------------------
  // Drag & Drop
  // -------------------------

  const handleDragOver = (event) => {
    event.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = () => {
    setDragActive(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragActive(false);

    const file = event.dataTransfer.files[0];

    if (file) {
      uploadFile(file);
    }
  };

  // -------------------------
  // Select document
  // -------------------------

  const toggleDocument = (id) => {
    setSelectedDocs((prev) => {
      if (prev.includes(id)) {
        return prev.filter((docId) => docId !== id);
      }

      return [...prev, id];
    });
  };

  // -------------------------
  // Delete document
  // -------------------------

  const deleteDocument = (id) => {
    setDocuments((prev) =>
      prev.filter((doc) => doc.id !== id)
    );

    setSelectedDocs((prev) =>
      prev.filter((docId) => docId !== id)
    );
  };

  // -------------------------
  // Ask RAG
  // -------------------------

  const askQuestion = async () => {
    if (!question.trim()) return;

    if (selectedDocs.length === 0) {
      alert("Please select at least one document.");
      return;
    }

    setAsking(true);
    setAnswer("");

    try {
      const response = await fetch(`${API_URL}/Home`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          querry: question,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Question failed");
      }

      setAnswer(data.answer || data);

    } catch (error) {
      console.error(error);
      setAnswer("Something went wrong while generating the answer.");
    } finally {
      setAsking(false);
    }
  };

  // -------------------------
  // Helpers
  // -------------------------

  const formatFileSize = (bytes) => {
    if (bytes < 1024) {
      return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="app">

      {/* ================= SIDEBAR ================= */}

      <aside className="sidebar">

        <div className="logo">
          <div className="logo-icon">✦</div>
          <span>RAG Assistant</span>
        </div>

        <nav>

          <button className="nav-item active">
            <span>⌂</span>
            Home
          </button>

          <button className="nav-item">
            <span>▤</span>
            Documents
          </button>

          <button className="nav-item">
            <span>◯</span>
            Chat
          </button>

          <button className="nav-item">
            <span>⚙</span>
            Settings
          </button>

        </nav>

        <div className="sidebar-bottom">
          <div className="online">
            <span></span>
            System Online
          </div>

          <small>v1.0.0</small>
        </div>

      </aside>

      {/* ================= MAIN ================= */}

      <main className="main">

        <div className="main-header">
          <h1>Welcome to RAG Assistant</h1>

          <p>
            Upload your documents, select what to use,
            and ask questions.
          </p>
        </div>

        <div className="content-grid">

          {/* ================= LEFT ================= */}

          <section className="left-section">

            {/* Upload */}

            <div
              className={`drop-zone ${
                dragActive ? "drag-active" : ""
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >

              <div className="upload-icon">
                ↑
              </div>

              <h2>
                {uploading
                  ? "Processing document..."
                  : "Drag & Drop your PDF here"}
              </h2>

              <p>or</p>

              <label className="browse-button">

                Browse Files

                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileInput}
                  hidden
                />

              </label>

              <small>
                Supports PDF files only • Max size: 10MB
              </small>

            </div>

            {/* Documents */}

            <div className="documents-card">

              <div className="documents-header">

                <div>
                  <h2>📄 Your Documents</h2>

                  <p>
                    Select or unselect documents to include
                    in the RAG search.
                  </p>
                </div>

                <label className="add-button">

                  + Add Document

                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileInput}
                    hidden
                  />

                </label>

              </div>

              {/* Table header */}

              <div className="table-header">

                <span></span>
                <span>File Name</span>
                <span>Size</span>
                <span>Status</span>
                <span>Actions</span>

              </div>

              {/* Documents */}

              {documents.length === 0 ? (

                <div className="empty-documents">

                  <div>📂</div>

                  <p>
                    No documents uploaded yet.
                  </p>

                </div>

              ) : (

                documents.map((doc) => (

                  <div
                    className="document-row"
                    key={doc.id}
                  >

                    <input
                      type="checkbox"
                      checked={selectedDocs.includes(doc.id)}
                      onChange={() =>
                        toggleDocument(doc.id)
                      }
                    />

                    <div className="file-name">

                      <span className="pdf-icon">
                        PDF
                      </span>

                      {doc.name}

                    </div>

                    <span>
                      {doc.size}
                    </span>

                    <span className="status">
                      {doc.status}
                    </span>

                    <div className="actions">

                      <button
                        title="Preview"
                        onClick={() =>
                          alert("Preview coming soon")
                        }
                      >
                        👁
                      </button>

                      <button
                        title="Delete"
                        onClick={() =>
                          deleteDocument(doc.id)
                        }
                      >
                        🗑
                      </button>

                    </div>

                  </div>

                ))

              )}

            </div>

          </section>

          {/* ================= CHAT ================= */}

          <section className="chat-card">

            <div className="chat-header">

              <div className="chat-icon">
                💬
              </div>

              <h2>Ask a Question</h2>

            </div>

            <div className="info-box">

              ✨

              <span>
                You can now ask questions about your
                selected documents. The assistant will use
                the information from the uploaded files.
              </span>

            </div>

            <div className="chat-area">

              {!answer && !asking && (

                <div className="chat-empty">

                  <div className="bot-icon">
                    🤖
                  </div>

                  <p>
                    Select your documents and
                    ask a question to get started!
                  </p>

                </div>

              )}

              {asking && (

                <div className="loading">

                  <div className="loader"></div>

                  <p>
                    Searching documents and generating
                    answer...
                  </p>

                </div>

              )}

              {answer && !asking && (

                <div className="answer">

                  <div className="answer-title">
                    🤖 RAG Assistant
                  </div>

                  <p>{answer}</p>

                </div>

              )}

            </div>

            {/* Question input */}

            <div className="question-area">

              <textarea
                placeholder="Type your question here..."
                value={question}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                onKeyDown={(event) => {

                  if (
                    event.key === "Enter" &&
                    !event.shiftKey
                  ) {
                    event.preventDefault();
                    askQuestion();
                  }

                }}
              />

              <button
                className="send-button"
                onClick={askQuestion}
                disabled={asking}
              >
                ↑
              </button>

            </div>

            <div className="selected-info">

              📎

              <span>
                Selected documents:
                <strong>
                  {" "}
                  {selectedDocs.length}
                </strong>
              </span>

            </div>

          </section>

        </div>

      </main>

    </div>
  );
}

export default App;