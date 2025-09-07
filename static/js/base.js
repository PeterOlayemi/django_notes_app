function themeApp() {
    return {
        darkMode: false,
        initTheme() {
            const saved = localStorage.getItem("theme");
            this.darkMode = saved === "dark";
            document.documentElement.classList.toggle("dark", this.darkMode);
        },
        toggleTheme() {
            this.darkMode = !this.darkMode;
            localStorage.setItem("theme", this.darkMode ? "dark" : "light");
            document.documentElement.classList.toggle("dark", this.darkMode);
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("searchInput");
  const suggestionsBox = document.getElementById("searchSuggestions");

  let debounceTimer;

  searchInput.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    const query = searchInput.value.trim();

    if (!query) {
      suggestionsBox.style.display = "none";
      return;
    }

    debounceTimer = setTimeout(() => {
      fetch(`/search-suggestions/?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
          suggestionsBox.innerHTML = "";

          if (!data.notes || data.notes.length === 0) {
            suggestionsBox.innerHTML =
              `<div class="px-4 py-2 text-gray-500 dark:text-gray-300 text-sm">No results found</div>`;
          } else {
            suggestionsBox.innerHTML += `<div class="px-4 py-2 bg-indigo-100 dark:bg-indigo-900 font-semibold text-indigo-700 dark:text-indigo-200 text-sm rounded-t-lg">Related Notes</div>`;
            
            data.notes.forEach(note => {
              suggestionsBox.innerHTML += `
                <a href="${note.url}" 
                   class="block px-4 py-2 hover:bg-indigo-100 dark:hover:bg-indigo-700 dark:text-gray-100 text-gray-800 text-sm">
                  ${note.title}
                </a>`;
            });
          }

          suggestionsBox.style.display = "block";
        })
        .catch(err => {
          console.error("Search suggestions error:", err);
        });
    }, 300);
  });

  document.addEventListener("click", (e) => {
    if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
      suggestionsBox.style.display = "none";
    }
  });
});
