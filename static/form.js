var xmlHttp = null;
//var serviceURL="http://localhost:8083"
var serviceURL="http://ucon-server.appspot.com"


function getIcon(id,keyName)
{
    var url = serviceURL+"/icon/byid?JSONP=handleData&id="+id+"&keyName="+keyName;
	jsonp=document.createElement('script');
	jsonp.type='text/javascript';
	jsonp.async='';
	jsonp.src=url;
	h=document.querySelector("head");
	h.appendChild(jsonp);	
}

function handleData(jsonData){
	console.log(jsonData);
	if(jsonData.length){
		f=document.querySelector("form[name=modifyIcon]");
		icon=jsonData[0];
//		document.querySelector("form[name=modifyIcon] input[name=tag]");
		f.querySelector("input[name=id]").value=icon['key'];
		f.querySelector("input[name=keyName]").value=icon['key_name'];
		f.querySelector("input[name=type]").value=icon['type'];
		f.querySelector("input[name=thumb]").value=icon['thumb'];
		f.querySelector("textarea[name=content]").innerHTML=icon['content'];
	}
	
}

/*
function modifyIconByID(placeName){
	var url = serviceURL+"/action/byid?";
    xmlHttp = new XMLHttpRequest(); 
    xmlHttp.onreadystatechange = ProcessRequest;
    xmlHttp.open( "GET", url, true );
    xmlHttp.send();
}

function ProcessRequest() 
{
    if ( xmlHttp.readyState == 4 && xmlHttp.status == 200 ) 
    {
        data=eval(xmlHttp.responseText);
    }
}
*/