const urlField = document.getElementById('url');
const submitButton = document.getElementById('fetch');
const formatSelect = document.getElementById('format');

function nameFromUrl(url) {
  const urlParts = url.split('/');
  const lastPart = urlParts[urlParts.length - 1];
  const nameParts = lastPart.split('.');
  console.log(nameParts);
  return nameParts[0].split('').filter(char => /\w/gi.test(char)).join('');
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

  fetch(`/api/extract?url=${encodeURIComponent(url)}&format=${encodeURIComponent(formatSelect.value)}`)
    .then(response => response.blob())
    .then(blob => {
      let fileURL = window.URL.createObjectURL(blob);
      let a = document.createElement('a');
      a.href = fileURL;
      a.download = nameFromUrl(url) + ((formatSelect.value == 'markdown') ? '.md' : '.txt');
      document.body.appendChild(a);
      a.click();
      a.remove();
    });

});
