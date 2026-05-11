<script>
  const BASE_URL = "https://pdf-ai-backend1.onrender.com";

  async function uploadPDF() {
    const fileInput = document.getElementById("pdfFile");
    const status = document.getElementById("uploadStatus");

    if (!fileInput.files.length) {
      status.innerText = "Please choose a PDF file.";
      return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    status.innerText = "Uploading...";

    try {
      const res = await fetch(`${BASE_URL}/upload-pdf`, {
        method: "POST",
        body: formData
      });

      const data = await res.json();
      status.innerText = data.message || "PDF uploaded successfully!";
    } catch (error) {
      status.innerText = "Upload failed. Please try again.";
      console.error(error);
    }
  }

  async function askQuestion() {
    const questionInput = document.getElementById("question");
    const chatBox = document.getElementById("chatBox");

    const question = questionInput.value.trim();
    if (!question) return;

    chatBox.innerHTML += `
      <div style="text-align:right;">
        <span style="background:#3b82f6;color:white;padding:8px 12px;border-radius:10px;display:inline-block;">
          ${question}
        </span>
      </div>
    `;

    questionInput.value = "";

    chatBox.innerHTML += `<div id="loading">Thinking...</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
      const res = await fetch(`${BASE_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ question: question })
      });

      const data = await res.json();

      document.getElementById("loading").remove();

      chatBox.innerHTML += `
        <div style="text-align:left;">
          <span style="background:#e5e7eb;padding:8px 12px;border-radius:10px;display:inline-block;">
            ${data.answer}
          </span>
        </div>
      `;
    } catch (error) {
      document.getElementById("loading").innerText = "Error...";
      console.error(error);
    }

    chatBox.scrollTop = chatBox.scrollHeight;
  }
</script>