// function getActiveForm(){
//     const activeSpecificChat = document.querySelector('.specificChat.is_active');
//     const send_message_form = activeSpecificChat ? activeSpecificChat.querySelector('#send-message-form') : null;
//     return send_message_form
// }
// function getActiveInput(){
//     const activeSpecificChat = document.querySelector('.specificChat.is_active');
//     const input_message = activeSpecificChat ? activeSpecificChat.querySelector('#message-input') : null;
//     return input_message
// }

let message_body = $('.chatContainer')
let input_message = $('#message-input')
let send_message_form = $('#send-message-form')
const USER_ID = $('#logged-in-user').val()
    
let loc = window.location
let wsStart = 'wss://'

if(loc.protocol === 'https') {
    wsStart = 'wss://'
}
let endpoint = `${wsStart}${loc.host}/ws/chat/`


const socket = new WebSocket(endpoint);

socket.onopen = async function(e){
    console.log('open', e)
    send_message_form.on('submit', function (e){
        console.log("submitting form");
        e.preventDefault()
        let message = input_message.val()
        let send_to = get_active_other_user_id()
        let thread_id = get_active_thread_id()

        let data = {
            'message': message,
            'sent_by': USER_ID,
            'send_to': send_to,
            'thread_id': thread_id
        }
        data = JSON.stringify(data)
        socket.send(data)
        $(this)[0].reset()
    })
}

socket.onmessage = async function(e){
    console.log('message', e)
    let data = JSON.parse(e.data)
    let message = data['message']
    let sent_by_id = data['sent_by']
    let thread_id = data['thread_id']
    newMessage(message, sent_by_id, thread_id)
}

socket.onerror = async function(e){
    console.log('error', e)
}

socket.onclose = async function(e){
    console.log('close', e)
}


function newMessage(message, sent_by_id, thread_id) {
	if ($.trim(message) === '') {
		return false;
	}
	let message_element;
	let chat_id = 'chat_' + thread_id
	if(sent_by_id == USER_ID){

        message_element = `
        <div class="sentMsg">
        <div>
            <p class="msg">${message}</p>
            <p class="msgTime">12:56 pm</p>
        </div>
    </div> 
    `
    }
	else{

        message_element = `<div class="receivedMsg">
            <div>
                <p class="msg">${message}</p>
                <p class="msgTime">1:56 pm</p>
            </div>
        </div>
        `           
        
    }

    let message_body = $('.specificChat[chat-id="' + chat_id + '"] .chatContainer')
	message_body.append($(message_element))
    message_body.animate({
        scrollTop: $(document).height()
    }, 100);
	input_message.val(null);
}


// $('.contact-li').on('click', function (){
//     $('.contacts .active').removeClass('active')
//     $(this).addClass('active')

//     // message wrappers
//     let chat_id = $(this).attr('chat-id')
//     $('.messages-wrapper.is_active').removeClass('is_active')
//     $('.messages-wrapper[chat-id="' + chat_id +'"]').addClass('is_active')

// })

function get_active_other_user_id(){
    let other_user_id = $('.specificChat.is_active').attr('other-user-id')
    other_user_id = $.trim(other_user_id)
    return other_user_id
}

function get_active_thread_id(){
    let chat_id = $('.specificChat.is_active').attr('chat-id')
    let thread_id = chat_id.replace('chat_', '')
    return thread_id
}
