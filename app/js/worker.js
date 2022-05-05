this.iWorker = function(options){
  //var funcString = `data:text/javascript;charset=US-ASCII,var __func = self.${options['func']}; postMessage(__func.apply(this, ${arr2str(options['args'])}));`;
  var worker = new Worker("data:text/javascript;charset=US-ASCII, var _;");
  //handle worker return in the main thread
  if (options['get'] != undefined){
    worker.addEventListener("message", function(msg) {
      options['get'](msg);
      worker.terminate();
    });
  }
  //handle msg recieved from the main thread in the worker thread
  worker.onmessage = function(e) {
    self.a = e.data;
    /*
    if(typeof(e.data)=="function"){window.__func__ = e.data;}
    if(typeof(e.data)=="object"){window.__args__ = e.data;}
    else if(e.data == "call"){postMessage(window.__func__.apply(this, window.__args__));}
    */
  }
  //******//
  if(options['err'] != undefined){worker.onerror = options['err'];}
  //worker.postMessage(options['func']);
  //worker.postMessage(options['args']);
  //worker.postMessage("call");
  return worker;

}





function arr2str(arr){
  if(arr == undefined){return "[]"}
  if(arr.length==0){return "[]"}
  var info_return = "[";
  for(i in arr){
    if(typeof(arr[i])=="string"){
      info_return+= `"${arr[i]}", `;
    }else{
      info_return+= `${arr[i]}, `;
    }
  }
  info_return = info_return.slice(0, -2)
  info_return += "]";
  return info_return
}