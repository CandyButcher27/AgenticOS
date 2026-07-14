// Dell.com 1996 reproduction — minimal period-appropriate behavior

document.addEventListener('DOMContentLoaded', function () {
  var searchInput = document.getElementById('search');
  var goButton = document.querySelector('.button-primary');

  function runSearch() {
    var query = searchInput ? searchInput.value.trim() : '';
    if (query.length > 0) {
      alert('Searching Dell.com for: ' + query);
    }
  }

  if (goButton) {
    goButton.addEventListener('click', runSearch);
  }

  if (searchInput) {
    searchInput.addEventListener('keydown', function (event) {
      if (event.key === 'Enter') {
        event.preventDefault();
        runSearch();
      }
    });
  }

  // Give the NEW! bursts a subtle pinned-on wobble on hover, evoking
  // the hand-applied GIF sticker feel without any soft/modern easing.
  var bursts = document.querySelectorAll('.new-burst-sticker');
  bursts.forEach(function (burst) {
    burst.addEventListener('mouseenter', function () {
      burst.style.transform = 'rotate(-10deg)';
    });
    burst.addEventListener('mouseleave', function () {
      burst.style.transform = 'rotate(-15deg)';
    });
  });
});
