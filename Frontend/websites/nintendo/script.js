document.getElementById('pollSubmit').addEventListener('click', function (e) {
  e.preventDefault();
  var picked = document.querySelector('input[name="poll"]:checked');
  if (!picked) {
    alert('Please choose an option before submitting.');
    return;
  }
  alert('Thanks for voting: ' + picked.parentElement.textContent.trim());
});
