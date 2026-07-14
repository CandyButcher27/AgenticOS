document.addEventListener('DOMContentLoaded', function () {
  var burger = document.getElementById('navBurger');
  var drawer = document.getElementById('navDrawer');

  if (burger && drawer) {
    burger.addEventListener('click', function () {
      drawer.classList.toggle('open');
    });
  }

  var copyBtn = document.getElementById('copyBtn');
  var installSnippet = document.getElementById('installSnippet');

  if (copyBtn && installSnippet) {
    copyBtn.addEventListener('click', function () {
      var code = installSnippet.querySelector('code');
      var text = code ? code.textContent : '';

      var finish = function () {
        copyBtn.classList.add('copied');
        setTimeout(function () {
          copyBtn.classList.remove('copied');
        }, 1500);
      };

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(finish, finish);
      } else {
        var textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        try { document.execCommand('copy'); } catch (e) {}
        document.body.removeChild(textarea);
        finish();
      }
    });
  }
});
