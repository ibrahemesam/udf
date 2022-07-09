


function init_ws(){

    window.ws = new WebSocket(`ws://127.0.0.1:${window.url_vars.ws_port}/`);
    ws.onmessage = (event)=>{
      // console.warn(msg);
      msg = JSON.parse(event.data);
      // console.info(msg); //dbg
      //recieved here: 
      //sent to there:
      if (msg.p){ // != undefined      so, this msg is a resolve of a promise [ie: send_await]
        var _resolve = ws.ws_promises_resolve[msg.p];
        delete ws.ws_promises_resolve[msg.p];
        _resolve(msg);
      }else{ // regular event
        return recv[msg.type](msg);
      }
    }
  
    ws.onopen = (event)=>{
        ws.onclose = onClose;
        // alert('open (:');
    }
    ws.onerr = (event)=>{
      onClose();
    }
    ws.ws_promises_resolve = {};
    ws.send_await = async(msg)=>{
      if (!msg.constructor === Object){
        console.warn("msg must be JSON object, so that this method can work efficiently");
        msg = JSON.parse(msg);
      }
      return await new Promise((resolve, decline)=>{
        while (true){
          msg.p = String(Date.now()+Math.random());
          if (!ws.ws_promises_resolve[msg.p]){
            ws.ws_promises_resolve[msg.p] = resolve;
            break;
          }
        }
        window.ws.send(JSON.stringify(msg));
      })
    }
  }
  
