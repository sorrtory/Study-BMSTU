const filePicker = document.getElementById("file-picker")
const codeArea = document.getElementById("code-area")
const submitForm = document.getElementById("submit-form")
const submitButton = document.getElementById("submit-button")
const messageForm =  document.getElementById("message-form")
const picsList = document.getElementById("pics-list")
const picsPicker = document.getElementById("pics-picker")
const picsVolume = document.getElementById("pics-volume")

function readFile(event) {
  const file = event.target.files[0]
  if (file.size > MAX_ALLOWED_SIZE) {
    alert("Максимальный размер файла: 160 Кб");
    filePicker.value = "";
  } else {
    const reader = new FileReader()
    reader.readAsText(file)
    reader.onload = () => { 
      codeArea.innerHTML =
        reader.result
	  .replace(/&/g, "&amp;")
	  .replace(/</g, "&lt;")
	  .replace(/>/g, "&gt;");
      codeArea.dispatchEvent(new Event("reload"))
      document.getElementById("code").value = reader.result
    }
  }
}

function trySubmitForm() {
  const form = document.forms["submit-form"]
  console.log(form.lang)
  if (form.lang.value === "") {
    alert("Выберите язык реализации")
  } else {
    form.submit()
  }
}

filePicker?.addEventListener("change", readFile)
submitButton?.addEventListener("click", trySubmitForm)

function copyToCodeArea(subid, langid) {
  codeArea.innerHTML =
    document.getElementById(subid).innerText
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  if (langid) {
    document.getElementById("lang" + langid).checked = true;
  }
  codeArea.dispatchEvent(new Event("reload"))
}


function sendMessage(event) {
    event.preventDefault();
    const params = new FormData(messageForm);

    fetch('/mail', {
        method: 'POST',
        body: params
    });

    location.reload();
}

messageForm.addEventListener("submit", sendMessage);

function addImage() {
    if (picsPicker.files.length == 0) return;

    const files = picsPicker.files;
    const file = files[0];
    const li = document.createElement("li");

    li.innerHTML = `
        Файл <tt>${file.name}</tt>, размер ${file.size}&nbsp;байт
        <input type="button" value="\u274C"/><br/>
        Для вставки в&nbsp;Markdown: <tt>![](pics/${file.name})</tt>
        <input type="file" name="picture" hidden/>
    `;
    li.querySelector("input[type=file]").files = files;
    li.querySelector("input[type=button]").onclick = (event) => {
        picsList.removeChild(event.target.parentNode);
        updatePicturesSize();
    };
    for (let otherLi of picsList.children) {
        const otherFile = otherLi.querySelector("input[type=file]");
        if (otherFile.files[0].name == file.name) {
            picsList.removeChild(otherLi);
        }
    }
    picsList.appendChild(li);
    updatePicturesSize();
}

function updatePicturesSize() {
    let size = 0;
    for (let li of picsList.children) {
        size += li.querySelector("input[type=file]").files[0].size;
    }
    picsVolume.innerText = size;
    picsVolume.style.color = size > MAX_PICTURES_SIZE ? "red" : "";
}

picsPicker?.addEventListener("change", addImage);
