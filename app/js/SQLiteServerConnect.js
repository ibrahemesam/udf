range = (start, stop, step = 1) =>
  Array(Math.ceil((stop - start) / step)).fill(start).map((x, y) => x + y * step)
SQLiteServer = {
    connect: async function SQLiteServerConnect(ip, port, secret){
        var ws = await (new Promise((resolve, decline)=>{
            var ws = new WebSocket(`ws://${ip}:${port}/`);
            ws.onopen = e=>{ws.send(secret); resolve(ws)}
            ws.onerr = e=>{decline(e.target.readyState)}
        }))
        if ((typeof ws)!='object'){
            throw `Connection Error: ${ws}`;
        }
        // convert python datatypes to js
        var None = null;
        var False = false;
        var True = true;
        var nan = NaN;
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
}

