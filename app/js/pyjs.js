const { createConnection } = require("net");

const BUFFER_END = "🤡";

function pyjs(
  port,
  recv_parser = () => {},
  send_decorator = (msg) => msg,
  recv_decorator = (msg) => msg,
  on_ready_promise_resolve = undefined
) {
  const client = createConnection(port, "localhost", () => {});
  var buffer = Buffer.alloc(0);
  client.on("data", (data) => {
    /*

            if data.endswith(BUFFER_END):
                buffer.extend(data.replace(BUFFER_END, b''))
                break
            buffer.extend(data)
        self.recv_parser(self.recv_decorator(buffer))
    */
    data = data.toString();
    if (data.includes(BUFFER_END)) {
      var msgs = data.split(BUFFER_END);
      length = msgs.length;
      var last_chunk = msgs[length - 1];
      if (last_chunk != "") {
        // concat
        buffer = buffer.concat(last_chunk);
      }
      // if first msg is incomplete: then it belongs to the last buffer
      try {
        recv_parser(recv_decorator(msgs[0]));
      } catch (error) {
        buffer + buffer.concat(msgs[0]);
        msgs.shift();
      }
      // parse buffer
      if (buffer) {
        try {
          recv_parser(recv_decorator(buffer));
          buffer = "";
        } catch (error) {}
      }
      msgs.pop();
      // console.log(msgs);
      for (let i = 0; i < msgs.length; i++) {
        recv_parser(recv_decorator(msgs[i]));
      }
    } else {
      // concat
      buffer = buffer.concat(data);
    }
  });

  client.on("error", (error) => {
    console.log(`Error: ${error.message}`);
  });

  client.on("connect", (evt) => {
    if (on_ready_promise_resolve) {
      on_ready_promise_resolve();
    }
  });

  var p = {};
  client.send = async (msg) => {
    if (p.p) await p.p;
    p.p = new Promise((r) => {
      p.r = r;
    });
    await client.write(send_decorator(msg) + BUFFER_END);
    // await client.write(BUFFER_END);
    p.r();
  };
  client.close = client.destroy;
  return client;
  // test
  client = pyjs(5000, console.log, JSON.stringify, JSON.parse);
  client.send({ t: "blabla_bla" });
}

module.exports = { pyjs };
