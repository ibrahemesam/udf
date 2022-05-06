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
    },
    search_local_network: (pong)=>{
        //pong is the msg that must be contained in the ping response [eg: phamily-SQL]
        ports = range(1025, 65536).reverse();
        for (let p = 0; p < ports.length; p++){
            var ws = await (new Promise((resolve, decline)=>{
                var ws = new WebSocket(`ws://${ip}:${ports[p]}/`);
                ws.onopen = e=>{ws.send(secret); resolve(ws)}
                ws.onerr = e=>{decline(e.target.readyState)}

                ws.onmessage = e=>{
                    if (e.data.includes(pong)){
                        resolve(ws);
                    }else{
                        resolve(-1);
                    }
                }
            }))
            if ((typeof ws)==='object'){
                return [ips[i], ports[p]]
            }
        }
    }
}

