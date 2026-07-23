document.getElementById("checkHealth").addEventListener("click", async () => {
  const resultEl = document.getElementById("result");
  resultEl.textContent = "Checking...";

  try {
    const response = await fetch("http://localhost:5000/health");
    const data = await response.json();
    resultEl.textContent = `Backend says: ${data.status}`;
  } catch (error) {
    resultEl.textContent = "Could not reach backend. Is app.py running?";
  }
});