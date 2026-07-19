let st_lastMultiIndex = [];
let st_multiNum = 0;
let st_CurrentColors = null;
let st_Multi = null;
let st_Regs = null;

function load_language(lang_st_label) {
  let rule = RULES[lang_st_label];
  if (rule) {
    st_CurrentColors = RULES[lang_st_label]["Color"];
    st_Multi = RULES[lang_st_label]["Multi"];
    st_Regs = RULES[lang_st_label]["Regs"];
    return true;
  }
  return false;
}

function colorMatch(tpe, val) {
  for (key in st_CurrentColors) {
    if (tpe == key) {
      return '<span style="-webkit-text-fill-color:' + st_CurrentColors[key] + ';">' + val + '</span>';
    }
  }
  for (let i = 0 ; i < st_Multi["Triggers"].length ; i++) {
    if (val == st_Multi["Triggers"][i]) {
      if (i % 2 == 1) {
        if (st_lastMultiIndex[st_lastMultiIndex.length - 1] != i - 1 || st_multiNum < 1) return '<span style="-webkit-text-fill-color:red;">' + val + '</span>';
        st_multiNum -= 1;
        st_lastMultiIndex.pop();
        return '<span style="-webkit-text-fill-color:' + st_Multi["Order"][st_multiNum % st_Multi["Order"].length] + ';">' + val + '</span>';
      }
      let out = '<span style="-webkit-text-fill-color:' + st_Multi["Order"][st_multiNum % st_Multi["Order"].length] + ';">' + val + '</span>';
      st_multiNum += 1;
      st_lastMultiIndex.push(i);
      return out;
    }
  }
  return val;
}

function fullParseOutput(txt) {
  st_multiNum = 0;
  let inp = txt.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  let out = "";
  if (Object.keys(st_Regs).length == 0) return inp;
  while (inp.length > 0) {
    let breakout = false;
    for (key in st_Regs) {
      for (rg in st_Regs[key]) {
        var mtch = null;
        st_Regs[key][rg].lastIndex = 0;
        mtch = st_Regs[key][rg].exec(inp);
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

var to_color = document.querySelectorAll("pre[class^=sourceCode ]");
for (let i = 0 ; i < to_color.length ; i++) {
  let st_label = to_color[i].className.split(" ")[1];
  st_label = st_label.charAt(0).toUpperCase() + st_label.slice(1);
  if (st_label == "Cpp") st_label = "C++";
  if (load_language(st_label)) {
    to_color[i].innerHTML = "<code>" + fullParseOutput(to_color[i].textContent) + "</code>";
  } else {
    console.log("Неизвестный язык: " + st_label + " (class=sourceCode)");
  }
}
to_color = document.querySelectorAll("code[class^=language-]");
for (let i = 0 ; i < to_color.length ; i++) {
  let to_load = to_color[i].className.split("-")[1];
  let st_label = to_load.charAt(0).toUpperCase() + to_load.slice(1);
  if (load_language(st_label)) {
    to_color[i].innerHTML = fullParseOutput(to_color[i].textContent);
  } else {
    console.log("Неизвестный язык: " + st_label + " (class=language-)");
  }
}

