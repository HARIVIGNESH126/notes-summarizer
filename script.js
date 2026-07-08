async function uploadFile() {
  const fileInput = document.getElementById('fileInput');
  const file = fileInput.files[0];

  if (!file) {
    alert('Please select a file first.');
    return;
  }

  const formData = new FormData();
  formData.append('file', file);
  const backendUrl = 'http://127.0.0.1:5000/summarize';

  try {
    const response = await fetch(backendUrl, {
      method: 'POST',
      body: formData
    });

    let data;
    try {
      data = await response.json();
    } catch (parseError) {
      alert('Server returned invalid JSON. Check the backend server logs.');
      console.error('Response parse error:', parseError);
      return;
    }

    if (!response.ok) {
      const err = data.error || JSON.stringify(data) || 'Failed to summarize notes.';
      alert(err);
      return;
    }

    const summaryList = document.getElementById('summaryList');
    summaryList.innerHTML = '';

    data.summary.forEach(sentence => {
      const li = document.createElement('li');
      li.textContent = sentence;
      summaryList.appendChild(li);
    });
  } catch (error) {
    console.error('Error:', error);
    alert('Failed to summarize notes. Is the backend server running on http://127.0.0.1:5000?');
  }
}
