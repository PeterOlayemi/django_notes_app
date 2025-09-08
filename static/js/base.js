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
  const searchBoxes = [
    { input: document.getElementById("searchInput"), box: document.getElementById("searchSuggestions") },
    { input: document.getElementById("mobileSearchInput"), box: document.getElementById("mobileSearchSuggestions") }
  ];

  let debounceTimer;

  searchBoxes.forEach(({ input, box }) => {
    if (!input || !box) return;

    input.addEventListener("input", () => {
      clearTimeout(debounceTimer);
      const query = input.value.trim();

      if (!query) {
        box.style.display = "none";
        return;
      }

      debounceTimer = setTimeout(() => {
        fetch(`/search-suggestions/?q=${encodeURIComponent(query)}`)
          .then(res => res.json())
          .then(data => {
            box.innerHTML = "";

            if (!data.notes || data.notes.length === 0) {
              box.innerHTML =
                `<div class="px-4 py-2 text-gray-500 dark:text-gray-300 text-sm">No results found</div>`;
            } else {
              box.innerHTML += `<div class="px-4 py-2 bg-indigo-100 dark:bg-indigo-900 font-semibold text-indigo-700 dark:text-indigo-200 text-sm rounded-t-lg">Related Notes</div>`;

              data.notes.forEach(note => {
                box.innerHTML += `
                  <a href="${note.url}"
                     class="block px-4 py-2 hover:bg-indigo-100 dark:hover:bg-indigo-700 dark:text-gray-100 text-gray-800 text-sm">
                    ${note.title}
                  </a>`;
              });
            }

            box.style.display = "block";
          })
          .catch(err => {
            console.error("Search suggestions error:", err);
          });
      }, 300);
    });

    document.addEventListener("click", (e) => {
      if (!input.contains(e.target) && !box.contains(e.target)) {
        box.style.display = "none";
      }
    });
  });
});
