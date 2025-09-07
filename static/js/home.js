document.addEventListener("DOMContentLoaded", function () {
  const lockCheckbox = document.querySelector("#id_is_locked");
  const passwordField = document.getElementById("lockPasswordField");

  if (lockCheckbox && passwordField) {
    function togglePasswordField() {
      if (lockCheckbox.checked) {
        passwordField.classList.remove("hidden");
        document.querySelector("#id_lock_password").required = true;
      } else {
        passwordField.classList.add("hidden");
        document.querySelector("#id_lock_password").required = false;
      }
    }

    togglePasswordField();

    lockCheckbox.addEventListener("change", togglePasswordField);
  }
});
