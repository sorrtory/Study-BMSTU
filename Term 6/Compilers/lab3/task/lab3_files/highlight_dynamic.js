const num_col = document.getElementById("num_col")
const code_wrapper = document.getElementById("code-wrapper")
const submission_input = document.getElementById("code")

let lastMultiIndex = [];
let multiNum = 0;

function load_language(lang_label) {
  CurrentColors = RULES[lang_label]["Color"];
  Multi = RULES[lang_label]["Multi"];
  PlusIndents = RULES[lang_label]["Indent"]["Plus"];
  indentChar = RULES[lang_label]["Indent"]["Sign"];
  indentNum = RULES[lang_label]["Indent"]["Value"];
  Regs = RULES[lang_label]["Regs"];
  codeArea.setAttribute("style", "tab-size: " + indentNum);
}

let currentLang = document.querySelector('input[name="lang"]:checked');
if (currentLang != null) {
  currentLang = currentLang.value;
  label = document.querySelector('label[for=lang' + currentLang + ']').innerText;
  load_language(label);
}

function switchColors(value) {
  value = document.querySelector('label[for=lang' + value + ']').innerText;
  load_language(value);
  codeArea.dispatchEvent(new Event("reload"));
}

let current_width = 30;

async function fill_num_col() {
  textLines = codeArea.innerText.split("\n");
  let newline_str = "";
  for(let i = 0 ; i < textLines.length ; i++) {
    newline_str += (i + 1) + "\n";
  }
  let num_col_width = Math.max(30, 10 * Math.floor(Math.log10(textLines.length) + 1));
  if (num_col_width != current_width) {
      code_wrapper.style.width = 833 + num_col_width + "px";
      num_col.style.width = num_col_width + "px";
      current_width = num_col_width;
  }
  num_col.innerText = newline_str;
}

function colorMatch(tpe, val) {
  for (key in CurrentColors) {
    if (tpe == key) {
      return '<span style="-webkit-text-fill-color:' + CurrentColors[key] + ';">' + val + '</span>';
    }
  }
  for (let i = 0 ; i < Multi["Triggers"].length ; i++) {
    if (val == Multi["Triggers"][i]) {
      if (i % 2 == 1) {
        if (lastMultiIndex[lastMultiIndex.length - 1] != i - 1 || multiNum < 1) return '<span style="-webkit-text-fill-color:red;">' + val + '</span>';
        multiNum -= 1;
        lastMultiIndex.pop();
        return '<span style="-webkit-text-fill-color:' + Multi["Order"][multiNum % Multi["Order"].length] + ';">' + val + '</span>';
      }
      let out = '<span style="-webkit-text-fill-color:' + Multi["Order"][multiNum % Multi["Order"].length] + ';">' + val + '</span>';
      multiNum += 1;
      lastMultiIndex.push(i);
      return out;
    }
  }
  return val;
}

function fullParseOutput(txt) {
  multiNum = 0;
  inp = txt.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  let out = "";
  while (inp.length > 0) {
    let breakout = false;
      for (key in Regs) {
        for (rg in Regs[key]) {
          var mtch = null;
          Regs[key][rg].lastIndex = 0;
          mtch = Regs[key][rg].exec(inp);
          if (mtch) {
            if (mtch.index == 0) {
              out += colorMatch(key, mtch[0]);
              inp = inp.slice(mtch[0].length);
              breakout = true;
              break;
            }
          }
        }
        if (breakout) break;
      }
  }
  return out;
}

function findIndent(str) {
  let out = 0;
  while (str[out] == indentChar) out += 1;
  let ptr = str.length - 1;
  while ([" ", "\t"].includes(str[ptr]) && ptr > 0) ptr--;
  if (PlusIndents.includes(str[ptr])) {
    if (indentChar == "\t") out += 1;
    else out += indentNum;
  }
  return indentChar.repeat(out);
}

const downToTextNode = node => {
  while (node && node.nodeType != 3) node = node.childNodes[0];
  return node;
}

const moveToNextTextNode = node => {
  while (! codeArea.isSameNode(node) && ! node.nextSibling)
    node = node.parentNode;

  node = codeArea.isSameNode(node) ? null : downToTextNode(node.nextSibling);
  return node;
}

const absolutFromNodeOffset = (node, offsetInNode) => {
  let curNode = downToTextNode(codeArea);

  let offset = 0;
  while (curNode && ! node.isSameNode(curNode)) {
    offset += curNode.nodeValue.length;
    curNode = moveToNextTextNode(curNode);
  }
  if (curNode) return offset + offsetInNode;
  else return 0;
}

const nodeOffsetFromAbsolut = offset => {
  let curNode = downToTextNode(codeArea);
  let lastNode = curNode;

  while (curNode && offset >= curNode.nodeValue.length) {
    offset -= curNode.nodeValue.length;
    lastNode = curNode
    curNode = moveToNextTextNode(curNode);
  }
  if (curNode) return [curNode, offset];
  else return [lastNode, lastNode.nodeValue.length];
}

function getCaretPos() {
  let sel = window.getSelection();
  if (! sel.anchorNode || ! sel.focusNode) return [0, 0];
  const anchor = absolutFromNodeOffset(sel.anchorNode, sel.anchorOffset);
  const focus = absolutFromNodeOffset(sel.focusNode, sel.focusOffset);
  return [anchor, focus];
}

function setCaretPos(anchor, focus, shift = 0) {
  sel = document.getSelection();
  sel.removeAllRanges();
  sel.setBaseAndExtent(
    ...nodeOffsetFromAbsolut(anchor),
    ...nodeOffsetFromAbsolut(focus),
  );
  while (shift --> 0)
    sel.modify("move", "forward", "character");
}

codeArea.addEventListener('keydown', (event) => {
  if (event.inputType == "deleteByDrag") return;
  if (event.key == "Enter" || event.keyCode == 13) {
    event.preventDefault();
    let [anchor, focus] = getCaretPos();
    let text = codeArea.innerText;
    let before_lines = text.slice(0, anchor).split("\n");
    const caretLine = before_lines.length;
    let before_line = before_lines[caretLine - 1];
    let indent = findIndent(before_line);

    let after_lines = codeArea.innerText.slice(anchor).split("\n");
    let after_line = "";
    if (after_lines.length > 0) after_line = after_lines[0];

    let html_lines = codeArea.innerHTML.split("\n");

    let full_text = before_line + "\n" + indent + after_line;
    parsedHTML = fullParseOutput(full_text);

    let newl = "";
    if (caretLine > 1) newl = "\n";

    codeArea.innerHTML = html_lines.slice(0, caretLine - 1).join("\n") + newl + parsedHTML + "\n" + html_lines.slice(caretLine).join("\n");
    submission_input.value = codeArea.innerText;
    fill_num_col();
    setCaretPos(anchor, focus, indent.length + 1);
  }
});

codeArea.addEventListener('paste', (event) => {
  if (event.inputType == "deleteByDrag") return;
  event.preventDefault();
  let paste = (event.clipboardData || window.clipboardData).getData("text/plain");
  let [anchor, focus] = getCaretPos();
  let full_text = codeArea.innerText.slice(0, anchor) + paste + codeArea.innerText.slice(anchor);
  let parsedHTML = fullParseOutput(full_text);
  codeArea.innerHTML = parsedHTML;
  submission_input.value = codeArea.innerText;
  fill_num_col();
  setCaretPos(anchor, focus, paste.length);
});

codeArea.addEventListener('reload', (event) => {
  let [anchor, focus] = getCaretPos();
  let parsedHTML = fullParseOutput(codeArea.innerText);
  codeArea.innerHTML = parsedHTML;
  submission_input.value = codeArea.innerText;
  fill_num_col();
  setCaretPos(anchor, focus);
});

codeArea.addEventListener('input', (event) => {
  if (event.inputType == "deleteByDrag") return;
  let [anchor, focus] = getCaretPos();
  let lines = codeArea.innerText.slice(0, anchor).split("\n");
  const caretLine = lines.length;
  let cur_line = codeArea.innerText.split("\n")[caretLine - 1];
  let html_lines = codeArea.innerHTML.split("\n");
  parsedHTML = fullParseOutput(cur_line);
  newl = "";
  if (caretLine > 1) newl = "\n";
  codeArea.innerHTML = html_lines.slice(0, caretLine - 1).join("\n") + newl + parsedHTML + "\n" + html_lines.slice(caretLine).join("\n");
  submission_input.value = codeArea.innerText;
  fill_num_col();
  setCaretPos(anchor, focus);
});

setTimeout(() => codeArea.dispatchEvent(new Event("reload")), 300);
