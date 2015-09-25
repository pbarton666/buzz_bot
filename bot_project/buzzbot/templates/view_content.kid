<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    >
<head>
  <meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
  <link href="/static/css/style.css" media="screen" rel="Stylesheet" type="text/css" />
<SCRIPT TYPE="text/javascript">
<!--
function popup(mylink, windowname)
{
if (! window.focus)return true;
var href;
if (typeof(mylink) == 'string')
   href=mylink;
else
   href=mylink.href;
window.open(href, windowname, 'width=800,height=600,scrollbars=yes, resizable=yes');
return false;
}
//-->
</SCRIPT>  
  
</head>
<body>
  <form xmlns:py="http://purl.org/kid/ns#"
    class="tableform"
    form = "${form}"
    action = "${action}"
    is_search = "${is_search}"
    checks ="${checks}"
    cont = "${cont}"
    date = "${date}"
    score = "${score}"
    link = "${link}"
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
	Examine Search Content 
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
			  <td id  = 'checkcol_content'><h1></h1></td>
			  <td id  = 'scorecol'><h1>Score </h1></td>
			  <td id  = 'datecol'><h1>Date </h1></td>
			  <td id  = 'contcol'><h1>Content </h1></td>
			  <td id  = 'linkcol'></td>
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
 			<span py:for="c, s, d, t, L  in zip(checks, score, date, cont, link)">
			  <tr>
			    <td id = "checkcol_content">  </td>
			    <td id = "scorecol"> <span py:content =  "s"> Score</span> </td>	
			    <td id = "datecol"> <span py:content =  "d"> Date</span> </td>
			    <td id = "contcol"> <span py:content =  "t"> Content</span> </td>
			    <td id = "linkcol"> <a href= "${L}" onClick="return popup(this, 'notes')"> link </a></td>
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
    
    