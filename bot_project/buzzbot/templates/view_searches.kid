<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">

<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>

<link href="/static/css/style.css" media="screen" rel="Stylesheet" type="text/css" />

</head>

<body>

<form xmlns:py="http://purl.org/kid/ns#"
    action = "${action}"
    class="tableform"
    name = "${form}"
>
     <div id = "bundleBox">
      <h1> Build a Custom Listening Post Here </h1>
      ${form.fields.display()}
        <table id="searches" height = "10">
         <tbody >
          <tr>
	    <th>Use </th>
            <th >Name </th>
            <th >Description </th>
	    <th >Edit/Delete </th>
          </tr>   
	  <!-- Lists the name, description, number of content entrys, and link to edit page --> 	  
	  	  
	    <tr py:for="s, e, d, f  in zip(searches, editlink, deletelink, form.fields)">
	      
	      <td width = "10"> ${f.display()} </td>
	      <td width = "100"> <span py:content = "s.name"> Name </span> </td>
	      <td width = "200"> <span py:content = "s.description"> Description </span> </td>

	      <!-- links to edit and delete--> 
		<td width = "65">
		  <img src="${tg.url('/static/images/spacer_khaki.jpg' )}" width = "10"  height="1"/> 
		  
		  <a href= "${e}">
		    <img src="${tg.url('/static/images/edit.gif' )}" title = "edit" width = "12"  height="12" border = "0"> </img>
		    </a>
		  <img src="${tg.url('/static/images/spacer_khaki.jpg' )}" width = "20"  height="1"/> 
		  <a href= "${d}">
		    <img src="${tg.url('/static/images/delete.gif' )}" title = "delete" width = "12"  height="12" border = "0"> </img>
		    </a>			
		
		</td>
		     
	    </tr>
         </tbody> 
        </table>
	<th > <a href= "/editsearch/0"><span style="font-weight: 400">Build a new one</span></a> </th>
	<th> <input type = "submit" action = "${action}" text = "x"> </input> </th>
      </div> 
 
</form>

<!-- 
${form(action=action)}
${tab1.display()} 
${form( searches = searches, editlink = editlink, deletelink=deletelink,widgetName = widgetName, action=action)}
-->  
  </body>                  
 </html>                       
    
    