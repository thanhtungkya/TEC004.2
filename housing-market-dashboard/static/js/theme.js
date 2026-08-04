/**
 * @file theme.js
 * @description Theme management module for switching dark/light color schemes.
 *
 * @features
 * - Detects OS system theme preferences and persists user selection in localStorage
 * - Dynamic data-theme document attribute updates and custom event dispatching
 *
 * @exports
 * - window.tecTheme: Global object with get(), set(), apply() methods
 */

(() => {
  const STORAGE_KEY = 'tec004-theme';
  const SIDEBAR_STORAGE_KEY = 'tec004-sidebar-state';

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

  // --- Sidebar Collapse & Expand State ---
  const getPreferredSidebarState = () => {
    return localStorage.getItem(SIDEBAR_STORAGE_KEY) || 'expanded';
  };

  const applySidebarState = (state) => {
    if (state === 'collapsed') {
      document.documentElement.classList.add('sidebar-collapsed');
    } else {
      document.documentElement.classList.remove('sidebar-collapsed');
    }
  };

  window.tecSidebar = {
    get: getPreferredSidebarState,
    set(state) {
      localStorage.setItem(SIDEBAR_STORAGE_KEY, state);
      applySidebarState(state);
      window.dispatchEvent(new CustomEvent('tec-sidebar-change', { detail: { state } }));
    },
    toggle() {
      const next = getPreferredSidebarState() === 'collapsed' ? 'expanded' : 'collapsed';
      this.set(next);
    }
  };

  // Apply both theme & sidebar state immediately to prevent layout flicker
  applyTheme(getPreferredTheme());
  applySidebarState(getPreferredSidebarState());

  const setupSidebarDOM = () => {
    // 1. Setup Collapse Button (<<) in .brand header
    const brand = document.querySelector('.brand');
    if (brand && !document.getElementById('sidebarCollapseBtn')) {
      const collapseBtn = document.createElement('button');
      collapseBtn.id = 'sidebarCollapseBtn';
      collapseBtn.className = 'btn-sidebar-toggle btn-sidebar-collapse';
      collapseBtn.title = 'Collapse Sidebar (<<)';
      collapseBtn.innerHTML = '&lt;&lt;';
      collapseBtn.setAttribute('aria-label', 'Collapse Sidebar');
      collapseBtn.onclick = () => window.tecSidebar.set('collapsed');

      // Restructure .brand if needed
      if (!brand.querySelector('.brand-main')) {
        const brandMain = document.createElement('div');
        brandMain.className = 'brand-main';
        while (brand.firstChild) {
          brandMain.appendChild(brand.firstChild);
        }
        brand.appendChild(brandMain);
      }
      brand.appendChild(collapseBtn);
    }

    // 2. Setup Expand Button (>>) in .topbar header
    const topbar = document.querySelector('.topbar');
    if (topbar && !document.getElementById('sidebarExpandBtn')) {
      const expandBtn = document.createElement('button');
      expandBtn.id = 'sidebarExpandBtn';
      expandBtn.className = 'btn-sidebar-toggle btn-sidebar-expand';
      expandBtn.title = 'Expand Sidebar (>>)';
      expandBtn.innerHTML = '&gt;&gt;';
      expandBtn.setAttribute('aria-label', 'Expand Sidebar');
      expandBtn.onclick = () => window.tecSidebar.set('expanded');

      const firstChild = topbar.firstElementChild;
      if (firstChild && firstChild.tagName === 'DIV') {
        let headerLeft = topbar.querySelector('.topbar-header-left');
        if (!headerLeft) {
          headerLeft = document.createElement('div');
          headerLeft.className = 'topbar-header-left';
          topbar.insertBefore(headerLeft, firstChild);
          headerLeft.appendChild(expandBtn);
          headerLeft.appendChild(firstChild);
        } else {
          headerLeft.insertBefore(expandBtn, headerLeft.firstChild);
        }
      } else {
        topbar.insertBefore(expandBtn, firstChild);
      }
    }
  };

  document.addEventListener('DOMContentLoaded', () => {
    applyTheme(getPreferredTheme());
    applySidebarState(getPreferredSidebarState());
    setupSidebarDOM();

    document.querySelectorAll('[data-theme-toggle]').forEach((toggle) => {
      toggle.addEventListener('change', (event) => {
        window.tecTheme.set(event.target.checked ? 'dark' : 'light');
      });
    });
  });
})();

