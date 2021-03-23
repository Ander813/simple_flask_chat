function getCookie(name) {
  let matches = document.cookie.match(new RegExp(
    "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
  ));
  return matches ? decodeURIComponent(matches[1]) : undefined;
}

Element.prototype.remove = function() {
    this.parentElement.removeChild(this);
}
NodeList.prototype.remove = HTMLCollection.prototype.remove = function() {
    for(let i = this.length - 1; i >= 0; i--) {
        if(this[i] && this[i].parentElement) {
            this[i].parentElement.removeChild(this[i]);
        }
    }
}

async function getChatMessages(id) {
    let response = await fetch('/chat/' + id)
    return await response.json()
}

async function clearChat() {
    document.getElementsByClassName('incoming_msg').remove()
    document.getElementsByClassName('outgoing_msg').remove()
}

async function addMessages(id) {
    let messages = await getChatMessages(id)
    let msg_history = document.getElementsByClassName("msg_history")[0]
    console.log(msg_history)
    for (let i = 0; i<messages.length; i++){
        if(messages[i].sender === getCookie("user")){
            console.log(messages[i].sender)
            msg_history.innerHTML += `<div class="outgoing_msg"><div class="sent_msg">
                                <p>${messages[i].text}</p>
                                <span class="time_date">${messages[i].sent}</span></div></div>`
        }
        else{
            msg_history.innerHTML += `<div class="incoming_msg"><div class="incoming_msg_img"><img src="https://ptetutorials.com/images/user-profile.png"\n' 
                                                                                   alt="sunil"></div>
                                                <div class="received_msg">
                                                    <div class="received_withd_msg">
                                                        <p>${ messages[i].text }</p> 
                                                        <span class="time_date">${ messages[i].sent }</span></div></div>`
            console.log(msg_history.innerHTML)
        }
    }
}

async function updateMessages(event) {
    let id = this.id
    await clearChat()
    await addMessages(id)
}

chats = document.getElementsByClassName("chat_list")
for(let i = 0; i < chats.length; i++){
    console.log(chats[i])
    chats[i].addEventListener("click", updateMessages)
}