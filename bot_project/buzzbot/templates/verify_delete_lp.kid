<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
  <head>
    <meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
    <title>Welcome to the Synovate Web Analysis Tool</title>   
    <link href="/static/css/style.css" media="screen" rel="Stylesheet" type="text/css" />
 
    
  </head>
  <body  onUnload="javascript:destroy()">
  <form xmlns:py="http://purl.org/kid/ns#"
    action = "${action}"
    value = "${value}"
    class="tableform"
    method = "post"
>

   <!-- Outer container table --> 
    <table class = 'verify_delete_frame'>
      <tbody>	
	<!-- First row has topic heading --> 	      
	<tr class = 'edit_search_header'>
	  <td >
	    <h3> 
	      <img border="0" src="/static/images/computerKhaki.png" width="50" height="50" /> 
	      <img border="0" src="/static/images/spacer_khaki.JPG" width="25" height="1" /> 
	      Delete Listening Post? 
	      <img border="0" src="/static/images/spacer_khaki.JPG" width="20" height="1" /> 
	      <img border="0" src="/static/images/computerKhaki.png" width="55" height="50" /> 
	    </h3>
	  </td>
	</tr>
	<!-- Second row has topic heading --> 
	  <tr><td> <h1>You have chosen to delete Listening Post "$value.name"</h1> </td>  </tr>
	 <tr><td><h1>This will delete this search and all content associated with it.</h1> </td></tr>
	  <tr>
		<table class="btn_table" >
		  <tbody>
		    <tr>
		      <td id="button_col"><input type = "submit" name = "submit" value = "   OK   " > </input>  </td>
		      <td id="button_col"><input type = "submit" name = "cancel" value="Cancel" href = "edit_search" /></td>
		      <td> </td><td> </td><td> </td>
		    </tr>
		  </tbody>
		</table> 
	  </tr>
	   
	</tbody> 
      </table>	
      <p></p>
    </form> 
  </body>
</html>
