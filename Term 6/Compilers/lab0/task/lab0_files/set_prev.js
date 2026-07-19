function setPrev(mID) {
    prev = document.getElementById("prev");
    prev.value = mID;
    alrt = document.getElementById("prev_alert");
    alrt.innerHTML = ("Сообщение будет связано с сообщением " + mID);
}
