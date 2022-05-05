

function init_ws(){
    window.ws = new WebSocket('ws://127.0.0.1:6060/');
    ws.onmessage = function(event) {
        window.ws_parse(event.data);
    };
    ws.onopen = (event)=>{
        ws.onclose = onClose;
        init_modal('modal_login').show();
    }
}