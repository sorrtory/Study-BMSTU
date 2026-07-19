const scheme = localStorage.getItem("hw-iu9-color-scheme") || "0";
document.documentElement.style.setProperty("--darkmode", scheme);


window.addEventListener("load", (event) => {
  const colorScheme = document.getElementById("colorScheme");

  colorScheme.addEventListener("change", (event) => {
    const scheme = event.target.value;
    localStorage.setItem("hw-iu9-color-scheme", scheme);
    document.documentElement.style.setProperty("--darkmode", scheme);
  });

  const selected = [...colorScheme.elements].filter(
    (element) => element.value === scheme,
  );

  if (selected) {
    selected[0].checked = true;
  }
});


