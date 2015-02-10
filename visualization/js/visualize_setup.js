function loadJson(relativePath){
    var jsonData = null;
    $.ajax({
    'async': false,
    'global': false,
    'url': 'http://localhost:8000/'+relativePath,
    'dataType': "json",
    'success': function (data) {
        jsonData = data;
    }
    });
    return jsonData
}

function sync_scroll(){
        $("#left").scroll(function () {
			$("#right").scrollTop($("#left").scrollTop());
			$("#right").scrollLeft($("#left").scrollLeft());
		});
		$("#right").scroll(function () {
			$("#left").scrollTop($("#right").scrollTop());
			$("#left").scrollLeft($("#right").scrollLeft());
		});
}

function setFileList(selectorId, optionsJson){
    s = document.getElementById(selectorId);
    s.options.length = 0;
    for (index in optionsJson){
        s.options[s.options.length] = new Option(optionsJson[index], index);
    }
    s.options.selectedIndex = 0;
}

function getCurrentFile(selectorId){
    sel = document.getElementById(selectorId)
    return sel.options[sel.selectedIndex].text;
}

function getAnnotationJson(displayDocName){
    return loadJson("json/"+displayDocName+".json");
}

function loadSelected(){
    goldData = getAnnotationJson(getCurrentFile("selector")+"_gold");
    systemData = getAnnotationJson(getCurrentFile("selector")+"_sys");
}

function embed() {
    try {
        loadSelected();
        leftDispatcher.post('requestRenderData', [$.extend({}, goldData)]);
        rightDispatcher.post('requestRenderData', [$.extend({}, systemData)]);
    } catch(e) {
        console.error('requestRenderData went down with:', e);
    }
}