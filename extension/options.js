document.addEventListener('DOMContentLoaded', () => {
  const apiUrlInput = document.getElementById('apiUrl');
  const saveButton = document.getElementById('save');

  // Load saved API URL
  chrome.storage.sync.get(['apiUrl'], (result) => {
    apiUrlInput.value = result.apiUrl || '';
  });

  // Save API URL
  saveButton.addEventListener('click', () => {
    const apiUrl = apiUrlInput.value;
    chrome.storage.sync.set({ apiUrl: apiUrl }, () => {
      alert('API URL saved!');
    });
  });
}); 