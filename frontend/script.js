async function uploadPDF() {
    const fileInput = document.getElementById("pdfFile");
    const status = document.getElementById("uploadStatus");

    if (!fileInput.files.length) {
        status.innerText = "Please choose a PDF file.";
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    status.innerText = "Uploading and indexing PDF...";

    try {
        const response = await fetch("http://127.0.0.1:8000/upload-pdf", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            status.innerText = data.error;
        } else {
            status.innerText = `${data.message} | Chunks: ${data.chunks}`;
        }
    } catch (error) {
        status.innerText = "Error uploading PDF.";
    }
}

async function askQuestion() {
    const question = document.getElementById("question").value.trim();
    const answerBox = document.getElementById("answerBox");

    if (!question) {
        answerBox.innerHTML = "<p>Please enter a question.</p>";
        return;
    }

    answerBox.innerHTML = "<p>Thinking...</p>";

    try {
        const response = await fetch("http://127.0.0.1:8000/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question: question })
        });

        const data = await response.json();

        answerBox.innerHTML = `
            <h3>Answer</h3>
            <p>${data.answer}</p>
        `;
    } catch (error) {
        answerBox.innerHTML = "<p>Error getting answer.</p>";
    }
}