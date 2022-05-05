
function emptyDef(){}
function addStyle(styleString) {
  const style = document.createElement('style');
  style.textContent = styleString;
  document.head.append(style);
}
function createElementFromHTML(htmlString) { var div = document.createElement('div'); div.innerHTML = htmlString.trim(); return div.firstChild; };
function scroll_to_item(element){
  var topPos = element.offsetTop;
  element.parentNode.scrollTop = topPos - element.parentNode.clientHeight/2 + 57;
}
function onVisible(element, callback) {
  new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if(entry.intersectionRatio > 0) {
        callback(element);
        observer.disconnect();
      }
    });
  }).observe(element);
}
function elmnt(id) { return document.getElementById(id.toString());}
function reload(){ window.location.reload(true);};
function gen_uid(){
  var navigator_info = window.navigator;
  var screen_info = window.screen;
  var uid = navigator_info.mimeTypes.length;
  // uid += navigator_info.userAgent.replace(/\D+/g, '');
  uid += navigator_info.plugins.length;
  uid += screen_info.height || '';
  uid += screen_info.width || '';
  uid += screen_info.pixelDepth || '';
  uid += (new Date()).getTime();
  return uid;
}


function try_def(def){
  try {
    def();
  } catch (error) {
    console.error(error);
  }
}

function init_progress(id){
  //wrapper for bootstrap progress box to make it easier to use => high level
  var el = document.getElementById(id);
  var bar = el.children[0];
  var label = bar.children[0];
  bar = $(bar);
  el = $(el);
  el.old_show = el.show;
  el.old_hide = el.hide;
  el.show = ()=>{
    var parent = el.parent();
    if (parent.children().length === 1){
      parent.show();
      parent.attr('hidden', false);
      try {
        if (parent.children().length === 1){
          parent.show();
          parent.attr('hidden', false);
        }
      } catch (error) {}
    }
    el.old_show();
  }
  el.hide = ()=>{
    var parent = el.parent();
    if (parent.children().length === 1){
      parent.hide();
      parent.attr('hidden', true);
    }
    el.old_hide();
  }
  eval(`window.${id} = el`);
  var bgs = ['bg-primary', 'bg-secondary', 'bg-info', 'bg-success', 'bg-danger'];
  //set color
  function get_bg(_class=null){
    var bg = null;
    if (!_class){
       _class = bar.attr('class');
    }
    for (var i=0; i<bgs.length; i++){
      if (_class.includes(bgs[i])){
        bg = bgs[i];
        break;
      }
    }
    return bg;
  }
  function set_bg(bg){
    var _class = bar.attr('class');
    var old_bg = get_bg(_class);
    if (old_bg){
      _class = _class.replaceAll(old_bg , bg);
    }else{
      _class += ` ${bg}`;
    }
    bar.attr('class', _class);
  }
  el.primary = ()=>{
    set_bg('bg-primary');
  }
  el.secondary = ()=>{
    set_bg('bg-secondary');
  }
  el.info = ()=>{
    set_bg('bg-info');
  }
  el.success = ()=>{
    set_bg('bg-success');
  }
  el.danger = ()=>{
    set_bg('bg-danger');
  }
  //set text
  el.setText = (txt)=>{
    label.innerHTML = txt;
  }
  //get text
  el.text = ()=>{
    return label.innerHTML;
  }
  //universal status function
  el.status = (status=null)=>{
    if (status) {
      el.setText(status);
      return status;
    }else{
      return el.text();
    }
  }
  //set percent
  el.setPercent = (num)=>{
    bar.style.width = `${num}%`;
  }
  //get percent
  el.percent = ()=>{
    return Number(bar.style.width.replace('%', ''))/100;
  }

  return el;
}

function init_modal(id){
  var modal = $(`#${id}`);
  eval(`window.${id} = modal`);
  modal.show = ()=>{
    modal.modal('show');
  }
  modal.hide = ()=>{
    modal.modal('hide');
  }
  modal.toggle = ()=>{
    modal.modal('toggle');
  }
  return modal;
}

function get_date(){
  var date = new Date();
  var month = date.getMonth()+1;
  if (month<10){month = "0"+month;}
  var day = date.getDate();
  if (day<10){day = "0"+day;}
  return {year: date.getFullYear(), month: month, day: day}
}
function get_GMT_datetime(){ //DATETIME - format: YYYY-MM-DD HH:MI:SS
  return (new Date()).toISOString().replace('T', ' ').split('.')[0];
}
window.date = get_date();

function get_GMT_diff(){
  var 
    date = new Date(),
    GMT_hours = parseInt(date.toISOString().split('T')[1].split(':')[0]);
  return date.getHours() - GMT_hours;
}
window.GMT_diff = get_GMT_diff();

function GMT_datetime_to_local(GMT_datetime){ //DATETIME - format: YYYY-MM-DD HH:MI:SS
  GMT_datetime = GMT_datetime.split(' ');
  var
    date = GMT_datetime[0].split('-'),
    year = date[0],
    month = parseInt(date[1]),
    day = date[2],
    time = GMT_datetime[1].split(':'),
    hour = parseInt(time[0]),
    minute = time[1],
    second = time[2],
    new_date = new Date(year, month-1, day, hour+window.GMT_diff, minute, second);
  return new_date.toISOString().replace('T', ' ').split('.')[0]
}

async function sleep(ms=1000){
  await new Promise(resolve => setTimeout(resolve, ms));
}
// hotkeys.setScope('all');
// hotkeys('alt+f6', function (event, handler){
//   event.preventDefault();
//   alert(this);
// });

function download_file(url, fileName) {
  console.log(url)
  var link = document.createElement("a");
	link.href = url;
	//set the visibility hidden so it will not effect on your web-layout
	link.style = "visibility:hidden";
	link.download = fileName;
	//this part will append the anchor tag and remove it after automatic click
	document.body.appendChild(link);
	link.click();
	document.body.removeChild(link);
}