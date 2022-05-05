window.substringMatcher = (strs)=>{
    return function findMatches(q, cb) {
    var matches, substringRegex;

    // an array that will be populated with substring matches
    matches = [];

    // regex used to determine if a string contains the substring `q`
    substrRegex = new RegExp(q, 'i');

    // iterate through the pool of strings and for any string that
    // contains the substring `q`, add it to the `matches` array
    $.each(strs, function(i, str) {
        if (substrRegex.test(str)) {
        matches.push(str);
        }
    });

    cb(matches);
    };
}

window.arabicPhrases = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    local: [
    "الإنجليزية",
    "نعم",
    "لا",
    "مرحبا",
    "أهلا"
    ]
});

function init_inp_search(id, items){
    $(document).ready(function() {
        $(`#${id} .typeahead`).typeahead({
            hint: true,
            highlight: true,
            minLength: 1
        },
        {
            name: 'items',
            source: substringMatcher(items)
        });

        $('#rtl-support .typeahead').typeahead({
            hint: false
        },
        {
            name: 'arabic-phrases',
            source: arabicPhrases
        });
    });
}


window.search = {
    clients: {
        names: [],
        codes: [],
        phones: []
    },
    drugs: ["adol", "beta"]
};
init_inp_search("inp_search_client_name", window.search.clients.names);
init_inp_search("inp_search_client_code", window.search.clients.codes);
init_inp_search("inp_search_client_phone", window.search.clients.phones);
init_inp_search("inp_drug", window.search.drugs);



$(document).ready(()=>{
    //  NOTE: when inp_seach typeahead item is chosen: 
    //      set the other 2 inp_search items corrosponding to the chosen client

    window._inp_search_client_name = $(".tt-input", "#inp_search_client_name");
    window._inp_search_client_code = $(".tt-input", "#inp_search_client_code");
    window._inp_search_client_phone = $(".tt-input", "#inp_search_client_phone");
    
    function search_client_name(){
        var val = _inp_search_client_name.val().trim();
        var idx = window.search.clients.names.indexOf(val);
        if (idx == -1){return;}
        _inp_search_client_code.val(window.search.clients.codes[idx]);
        _inp_search_client_phone.val(window.search.clients.phones[idx]);
    }

    _inp_search_client_name.on('keyup', search_client_name);
    _inp_search_client_name.on('blur', search_client_name);

    function search_client_code(){
        var val = _inp_search_client_code.val().trim();
        var idx = window.search.clients.codes.indexOf(val);
        if (idx == -1){return;}
        _inp_search_client_name.val(window.search.clients.names[idx]);
        _inp_search_client_phone.val(window.search.clients.phones[idx]);
    }

    _inp_search_client_code.on('keyup', search_client_code);
    _inp_search_client_code.on('blur', search_client_code);

    function search_client_phone(){
        var val = _inp_search_client_phone.val().trim();
        var idx = window.search.clients.phones.indexOf(val);
        if (idx == -1){return;}
        _inp_search_client_name.val(window.search.clients.names[idx]);
        _inp_search_client_code.val(window.search.clients.codes[idx]);
    }

    _inp_search_client_phone.on('keyup', search_client_phone);
    _inp_search_client_phone.on('blur', search_client_phone);
});





