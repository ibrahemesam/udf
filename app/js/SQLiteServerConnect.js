async function SQLiteServerConnect(ip, port, secret){
    // convert python datatypes to js
    var None = null;
    var False = false;
    var True = true;
    var nan = NaN;
    var ws = await (new Promise((resolve, decline)=>{
        var ws = new WebSocket(`ws://${ip}:${port}/`);
        ws.onopen = e=>{ws.send(secret); resolve(ws)}
        ws.onerr = e=>{decline(e.target.readyState)}
    }))
    if ((typeof ws)!='object'){
        throw `Connection Error: ${ws}`;
    }
    var queue = [];
    ws.onmessage = e=>{
        queue.shift()(e.data);
    }
    var obj = {}
    obj.query = async(query)=>{
        var promise = new Promise((resolve, decline)=>{queue.push(resolve);});
        ws.send(query);
        var data = await promise;
        if (data.startsWith('[Error]:')){
            throw data;
        }
        return eval('('+data+')');
    }
    return obj.query;
}