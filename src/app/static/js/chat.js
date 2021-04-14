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
async function scrollChat(){
    let msg_history = document.getElementById("chat_history")
    msg_history.scrollTop = msg_history.scrollHeight
}

async function getChatMessages(id) {
    let response = await fetch('/chat/' + id)
    return await response.json()
}

async function clearChat() {
    document.getElementsByClassName('incoming_msg').remove()
    document.getElementsByClassName('outgoing_msg').remove()
}

async function addMessage(msg){
    let msg_history = document.getElementById("chat_history")
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
       await addMessage(messages[i])
    }
    await scrollChat()
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
    await scrollChat()

}

chats = document.getElementsByClassName("chat_list")
for(let i = 0; i < chats.length; i++){
    chats[i].addEventListener("click", updateMessages)
}

function joinChat(){
    socket = io.connect('http://127.0.0.1:5000');

	socket.on("connect", function() {
		console.log("connected")
	});

    socket.on("connected", function(username) {
        addToOnlineList([username])
    })

    socket.on("disconnected", function(username){
        removeFromOnlineList(username)
    })

	socket.on("response", async function(response) {
        await addMessage(response)
        await scrollChat()
    })
    socket.on("disconnect", function(resp) {
        console.log("disconnect", resp)
    })
}

function sendMessage(){
    let msg_input = document.getElementById("msg")
    if (msg_input.value !== "") {
        socket.emit('pm',
            {"text": msg_input.value, "sender": username, "id": 1});
        msg_input.value = ""
    }
}

async function getOnlineUsers(){
    let users_online = await fetch("online").then(response => response.json())
    return users_online.online
}
function alreadyInOnlineList(username) {
    let users_online = document.getElementsByClassName("online-user")
    for (let j = 0; j < users_online.length; j++) {
        if (users_online[j].innerHTML === username) {
            return true
        }
    }
    return false
}

function addToOnlineList(users){
    let users_list = document.getElementById("users-list")
    for(let i=0; i<users.length; i++){
        if(!alreadyInOnlineList(users[i])){
            users_list.innerHTML += `<li class="online-user">${users[i]}</li>`
        }
    }
}

function removeFromOnlineList(username){
    let users = document.getElementsByClassName("online-user")
    for(let i=0; i < users.length; i++){
        if(users[i].innerHTML === username){
            users[i].remove()
        }
    }
}

document.addEventListener("DOMContentLoaded", async function () {
    joinChat()
    await scrollChat()
    addToOnlineList(await getOnlineUsers())
})

button = document.getElementById("send")
button.addEventListener("click", sendMessage)