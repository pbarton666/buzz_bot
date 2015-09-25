<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    >
<head>
  <meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
  <link href="/static/css/style.css" media="screen" rel="Stylesheet" type="text/css" />
  
</head>
<body>
  <form xmlns:py="http://purl.org/kid/ns#"
    class="tableform"
    form = "${form}"
    action = "${action}"
    checks ="${checks}"
    data = "${data}"
      >
    <!-- Pass in the hidden fields.--> 	
	  <div py:for="field in form.fields">
		<div py:if="field.field_class=='hiddenfield'">
		  <span py:replace="field.display(form.value_for(field, value))">
		  </span>
		</div>     
	      </div>

      <h3> 
	<img border="0" src="/static/images/spacer_khaki.JPG" width="2" height="1" />
	<img border="0" src="/static/images/computerKhaki.png" width="50" height="50" /> 
	<img border="0" src="/static/images/spacer_khaki.JPG" width="65" height="1" />
	View URLS 
	<img border="0" src="/static/images/spacer_khaki.JPG" width="60" height="1" />
	<img border="0" src="/static/images/computerKhaki.png" width="50" height="50" /> 
      </h3>

    <!-- Outer container table --> 
    <table class = 'lp_frame'>
      <tbody>
	  <!-- first row contains header table --> 
	    <tr width = "100%"> 
		<td>
		      <table class="content_header_table" > <tbody >
			<tr id='content_header'>
			  <td id  = 'urlcol'><h1>Urls:</h1></td>
			</tr>   
			<tr></tr>
			</tbody> </table>		
	       </td>  
	    </tr>
	
	<!-- second row lists the contents --> 
	  <tr>
	    <td>
		<div class = 'scrollDiv'>  <!-- div element provides scrolling --> 
		  <table  class = 'search_list'  >
		    <tbody >
 			<span py:for="d in data">
			  <tr>
			    <td id = "urlcol"> $d </td>
			  </tr>
			  <tr></tr><tr></tr>
			</span>  
		     </tbody> 
		    </table>
		  </div>
		</td>
	      </tr>	
	      
	<!-- third row has the buttons -->   
	  <tr>
	    <td>
		<img src="${tg.url('/static/images/spacer_khaki.jpg' )}" width = "20"  height="1"/> 
		<table class="btn_table" >
		  <tbody>
		    <tr>
		      <td id="button_col"><input id = "button" type = "submit" name = "ok" value = "  OK  "> </input>  </td>
		      <td></td>
		      <span py:if= 'value.get("lastbtn") == True'>
			<td id="button_col"><input id = "button" type = "submit" name = "last" value = " last  "> </input>  </td>
			</span>
		      <span py:if ='value.get("lastbtn") == False'>
			<td id="button_col">  </td>
			</span>	
		      <span py:if ='value.get("nextbtn") == True'>		
			<td id="button_col"><input id = "button" type = "submit" name = "next" value = " next  "> </input>  </td>
			</span>
		      <span py:if ='value.get("nextbtn") == False'>
			<td id="button_col">  </td>
			</span>		
			<td id="button_col"><input id = "button" type = "submit" name = "add" value = " add  "> </input>  </td>

		      <td> </td><td> </td><td> </td>
		    </tr>
		  </tbody>
		</table>  
	      </td>
	    </tr>  
		 
       
	</tbody>
       </table>  <!-- end of main container table -->  
    </form>
   
  </body>                  
 </html>                       
    
    