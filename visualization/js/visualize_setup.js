function loadJson(relativePath){
    var jsonData = null;
    $.ajax({
    'async': false,
    'global': false,
    'url': relativePath,
    'dataType': "json",
    'success': function (data) {
        jsonData = data;
    }
    });
    return jsonData
}

function toggleCluster(){
        $('#show-cluster-checkbox').change(function () {
            $('#left-cluster-div').fadeToggle()
            $('#right-cluster-div').fadeToggle()
        });
}

function syncScroll(){
        $("#left").scroll(function () {
			$("#right").scrollTop($("#left").scrollTop())
			$("#right").scrollLeft($("#left").scrollLeft())
		});
		$("#right").scroll(function () {
			$("#left").scrollTop($("#right").scrollTop())
			$("#left").scrollLeft($("#right").scrollLeft())
		});
}

function setSelectorOptions(selectorId, optionsJson){
    s = document.getElementById(selectorId);
    s.options.length = 0
    for (index in optionsJson){
        s.options[s.options.length] = new Option(optionsJson[index], index)
    }
    s.options.selectedIndex = 0
}

function getClusterNameList(goldCoref, sysCoref){
    var sysSurfaceMap = getAnnotationJson("surface", currentFileName+ "_surface_sys")
    var goldSurfacemap = getAnnotationJson("surface", currentFileName+ "_surface_gold")
    var goldNames = generateClusterSurfaceName(goldCoref, sysSurfaceMap)
    var sysNames= generateClusterSurfaceName(sysCoref, goldSurfacemap)

    return {
        goldNames:goldNames,
        sysNames:sysNames
    }
}

function generateClusterSurfaceName(coref, surfaceMap){
    corefNames = []

    for (var clusterIndex = 0 ; clusterIndex < coref.length ; clusterIndex ++){
        cluster = coref[clusterIndex]
        clusterNames = []
        for ( var eventIndex = 0; eventIndex < cluster.length; eventIndex ++){
            eventId = cluster[eventIndex]
            clusterNames.push(surfaceMap[eventId])
        }
        corefNames.push(clusterNames.join("=>"))
    }
    return corefNames
}

function setClusterList(goldCoref, sysCoref){
    if (goldCoref && sysCoref){
        clusterOptions = getClusterNameList(goldCoref, sysCoref)
        setSelectorOptions("left-cluster-selector", clusterOptions.goldNames)
        setSelectorOptions("right-cluster-selector", clusterOptions.sysNames)
    }
}

function getSelectorText(selectorId){
    sel = document.getElementById(selectorId)
    return sel.options[sel.selectedIndex].text;
}

function getSelectorValue(selectorId){
    sel = document.getElementById(selectorId)
    return sel.options[sel.selectedIndex].value;
}

function getMultipleSelectorValue(selectorId){
      var sel=document.getElementById(selectorId);
      var selectedValues = []
      for (var i = 0; i < sel.options.length; i++) {
         if(sel.options[i].selected ==true){
             selectedValues.push(sel.options[i].value);
          }
      }
      return selectedValues
}


function getAnnotationJson(subpath, displayDocName){
    return loadJson("json/"+ subpath + "/"+ displayDocName+".json")
}


function loadSelectedFile(){
    currentFileName = getSelectorText("selector")
    goldData = getAnnotationJson("span", currentFileName+"_gold")
    systemData = getAnnotationJson("span",currentFileName+"_sys")
}

function onFileChange(){
    fileChanged = true
    updateData()
}


function loadCoref(){
    goldCoref = getAnnotationJson("coref", currentFileName+"_coref_gold")
    sysCoref = getAnnotationJson("coref", currentFileName+"_coref_sys")
    return {
        goldCoref: goldCoref, sysCoref: sysCoref
    }
}


function loadEventClusterSelected(){
    return {
        goldCluster:getMultipleSelectorValue("left-cluster-selector"), sysCluster:getMultipleSelectorValue("right-cluster-selector")
    }
}

function getEventSubset(coref, indices){
    var subsetMap = {}
    for (var i = 0; i < indices.length; i++) {
        cluster = coref[indices[i]]
        for (var eventIndex = 0; eventIndex < cluster.length; eventIndex++){
            subsetMap[cluster[eventIndex]] = 1
        }
    }
    return subsetMap
}


function filterEvents(data, coref, indices){
    eventSubsetMap = getEventSubset(coref, indices)
    var newData = JSON.parse(JSON.stringify(data));
    var events = newData.events
    var resultEvents = []
    for (var eventIndex = 0; eventIndex < events.length; eventIndex ++){
       event = events[eventIndex]
       var eventId  = event[0]
       if (eventId in eventSubsetMap){
           resultEvents.push(event)
       }
    }
    newData.events = resultEvents
    return newData
}


function selectSubset(){
    if (fileChanged){
        coref = loadCoref()
        setClusterList(coref.goldCoref, coref.sysCoref)
        fileChanged = false
    }

    if(document.getElementById("show-cluster-checkbox").checked){
        var clusterSelected = loadEventClusterSelected()
        console.log(coref)
        console.log(goldData)
        goldDataDisplay = filterEvents(goldData, coref.goldCoref, clusterSelected.goldCluster)
        systemDataDisplay = filterEvents(systemData, coref.sysCoref, clusterSelected.sysCluster)
    }else{
        goldDataDisplay = goldData
        systemDataDisplay = systemData
    }
}

function loadDisplayData(){
    if (fileChanged){
        loadSelectedFile()
        console.log(currentFileName)
    }
    selectSubset()
}

function updateData() {
    try {
        loadDisplayData();
        leftDispatcher.post('requestRenderData', [$.extend({}, goldDataDisplay)]);
        rightDispatcher.post('requestRenderData', [$.extend({}, systemDataDisplay)]);
    } catch(e) {
        console.error('requestRenderData went down with:', e);
    }
}

function embed() {
    leftDispatcher = Util.embed('left',
        $.extend({'collection': null}, collData),
        $.extend({}, goldDataDisplay), webFontURLs);
    rightDispatcher = Util.embed('right',
        $.extend({'collection': null}, collData),
        $.extend({}, systemDataDisplay), webFontURLs);
}