const playPauseBtn = document.getElementById('playPauseBtn');
if (playPauseBtn) {
  playPauseBtn.addEventListener('click', () => {
    const playing = playPauseBtn.getAttribute('aria-pressed') === 'true';
    playPauseBtn.setAttribute('aria-pressed', String(!playing));
    playPauseBtn.textContent = playing ? '▶' : '❚❚';
  });
}

document.querySelectorAll('.play-btn:not(.play-btn--main)').forEach((btn) => {
  btn.addEventListener('click', (e) => {
    e.preventDefault();
    btn.textContent = btn.textContent === '▶' ? '❚❚' : '▶';
  });
});

document.querySelectorAll('.progress-track').forEach((track) => {
  track.addEventListener('click', (e) => {
    const rect = track.getBoundingClientRect();
    const ratio = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width));
    track.querySelector('.progress-track__fill').style.width = `${ratio * 100}%`;
  });
});

document.querySelectorAll('.sidebar__playlist-list li').forEach((item) => {
  item.addEventListener('click', () => {
    document.querySelectorAll('.sidebar__playlist-list li').forEach((li) => li.classList.remove('sidebar__nav-link--active'));
    item.classList.add('sidebar__nav-link--active');
  });
});

document.querySelectorAll('.pill').forEach((pill) => {
  pill.addEventListener('click', (e) => {
    e.preventDefault();
    document.querySelectorAll('.pill').forEach((p) => p.classList.remove('pill--active'));
    pill.classList.add('pill--active');
  });
});
