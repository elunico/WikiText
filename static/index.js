const urlField = document.getElementById('url');
const submitButton = document.getElementById('fetch');
const formatSelect = document.getElementById('format');
const statusArea = document.getElementById('status');

function nameFromUrl(url) {
  const urlParts = url.split('/');
  const lastPart = urlParts[urlParts.length - 1];
  const nameParts = lastPart.split('.');
  console.log(nameParts);
  return nameParts[0].split('').filter(char => /\w/gi.test(char)).join('');
}

function extensionForFormat(format) {
  return { 'markdown': '.md', 'text': '.txt', 'pdf': '.pdf' }[format];
}

function mimeForFormat(format) {
  return { 'markdown': 'text/markdown', 'text': 'text/plain', 'pdf': 'application/pdf' }[format];
}

window.onload = function () {
  formatSelect.value = localStorage.getItem('format') || 'text';
};

submitButton.addEventListener('click', () => {

  if (!urlField.value.startsWith('http')) {
    urlField.value = 'https://' + urlField.value;
  }
  const url = urlField.value;

  localStorage.setItem('format', formatSelect.value);

  submitButton.setAttribute('disabled', true);
  formatSelect.setAttribute('disabled', true);
  statusArea.style.display = 'block';
  fetch(`/api/extract?url=${encodeURIComponent(url)}&format=${encodeURIComponent(formatSelect.value)}`)
    .then(response => {
      if (!response.ok) {
        throw new Error(response.statusText);
      } else {
        return response.blob();
      }
    })
    .then(blob => {
      blob = blob.slice(0, blob.size, mimeForFormat(formatSelect.value));
      let fileURL = window.URL.createObjectURL(blob);
      let a = document.createElement('a');
      a.href = fileURL;
      a.download = nameFromUrl(url) + extensionForFormat(formatSelect.value);
      document.body.appendChild(a);
      a.click();
      a.remove();
      submitButton.removeAttribute('disabled');
      formatSelect.removeAttribute('disabled');
      statusArea.style.display = 'none';
      URL.revokeObjectURL(fileURL);
    }).catch(error => {
      console.error(error);
      submitButton.removeAttribute('disabled');
      formatSelect.removeAttribute('disabled');
      alert(error);
      statusArea.style.display = 'none';
    });

});
