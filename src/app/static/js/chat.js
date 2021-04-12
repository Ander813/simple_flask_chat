function getCookie(name) {
    let matches = document.cookie.match(new RegExp(
    "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}

username = getCookie("user").replace(/"/g, '')

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

function addMessage(msg){
    let msg_history = document.getElementsByClassName("msg_history")[0]
    if(msg.sender === username){
        msg_history.innerHTML += `<div class="outgoing_msg"><div class="sent_msg">
                                <p>${msg.text}</p>
                                <span class="time_date">${msg.sent}</span></div></div>`
        }
    else{
        msg_history.innerHTML += `<div class="incoming_msg"><div class="incoming_msg_img"><img src="https://ptetutorials.com/images/user-profile.png"\n' 
                                                                                   alt="sunil"></div>
                                                <div class="received_msg">
                                                    <div class="received_withd_msg">
                                                        <p>${ msg.text }</p> 
                                                        <span class="time_date">${ msg.sent }</span></div></div>`
        }
}

async function addMessagesFromChat(id) {
    let messages = await getChatMessages(id)
    for (let i = 0; i<messages.length; i++){
        addMessage(messages[i])
    }
}

async function markInactive(){
    document.getElementsByClassName("active_chat")[0].classList.remove("active_chat")
}

async function markActive(id){
    document.getElementById(id).classList.add("active_chat")
}

async function updateMessages(event) {
    await markInactive()
    await markActive(this.id)
    await clearChat()
    await addMessagesFromChat(this.id)

}

chats = document.getElementsByClassName("chat_list")
for(let i = 0; i < chats.length; i++){
    chats[i].addEventListener("click", updateMessages)
}

function joinChat(){
    socket = io.connect('http://127.0.0.1:5000?room=501');

	socket.on("connect", function() {
		console.log("connected")
	});

	socket.on("response", function(response) {
        addMessage(response)
    })
    socket.on("disconnect", function(resp) {
        console.log("wut", resp)
    })
}

function sendMessage(){
    let msg = document.getElementById("msg").value
    if (msg !== "") {
        socket.emit('pm',
            {"text": msg, "sender": username, "id": 1});
    }
}

document.addEventListener("DOMContentLoaded", joinChat)

button = document.getElementById("send")
button.addEventListener("click", sendMessage)