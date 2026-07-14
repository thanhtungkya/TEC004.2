(() => {
  const STORAGE_KEY = 'tec004-theme';
  const getPreferredTheme = () => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === 'light' || stored === 'dark') return stored;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  };

  const applyTheme = (theme) => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.colorScheme = theme;
    document.querySelectorAll('[data-theme-label]').forEach((node) => {
      node.textContent = theme === 'dark' ? 'Dark mode' : 'Light mode';
    });
    document.querySelectorAll('[data-theme-toggle]').forEach((node) => {
      node.checked = theme === 'dark';
      node.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    });
  };

  window.tecTheme = {
    get: getPreferredTheme,
    set(theme) {
      localStorage.setItem(STORAGE_KEY, theme);
      applyTheme(theme);
      window.dispatchEvent(new CustomEvent('tec-theme-change', { detail: { theme } }));
    },
    apply: applyTheme,
  };

  applyTheme(getPreferredTheme());

  document.addEventListener('DOMContentLoaded', () => {
    applyTheme(getPreferredTheme());
    document.querySelectorAll('[data-theme-toggle]').forEach((toggle) => {
      toggle.addEventListener('change', (event) => {
        window.tecTheme.set(event.target.checked ? 'dark' : 'light');
      });
    });
  });
})();
