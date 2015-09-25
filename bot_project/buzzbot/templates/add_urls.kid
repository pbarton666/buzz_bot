<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    >
<head>
  <meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
  <link href="/static/css/style.css" media="screen" rel="Stylesheet" type="text/css" />
</head>
<body>
  <form xmlns:py="http://purl.org/kid/ns#"
      action = "${action}"
      class="tableform"
      value="${value}" 
      form="${form}"
      >
    <!-- Pass in the hidden fields.--> 	
	  <div py:for="field in form.fields">
		<div py:if="field.field_class=='hiddenfield'">
		  <span py:replace="field.display(form.value_for(field, value))">
		  </span>
		</div>     
	      </div>
	      
 <!-- Outer container table--> 
    <table class = 'search_spec_frame'>
      <tbody>
	<!-- First row is the header--> 
	<tr class = 'edit_search_header'>
	  <td >
	    <h3> 
	      <img border="0" src="/static/images/computerKhaki.png" width="50" height="50" /> 
	      <img border="0" src="/static/images/spacer_khaki.JPG" width="150" height="1" /> 
	      Add URLs 
	      <img border="0" src="/static/images/spacer_khaki.JPG" width="150" height="1" /> 
	      <img border="0" src="/static/images/computerKhaki.png" width="50" height="50" /> 
	    </h3>
	  </td>
	</tr>  
	
	<!--  Options --> 	
	<tr>
	  <td>
	      <table class = "add_url_options">
		 <tr><div py:for="field in form.fields">
			 <div py:if="field.name=='deleteexisting'">
			    <td id="add_url_left_col"> <h1><span py:replace="field.label"> </span></h1></td>
			    <td id="add_url_right_col"> <span py:replace="field.display(form.value_for(field, value))"> </span></td>	   
			</div> </div>  </tr>
		      
	       </table> 
	    </td>
	  </tr>
	<!--  Field into which we can past new urls -->   
		 <tr><div py:for="field in form.fields">
			 <div py:if="field.name=='rawurls'">
			    <td id = 'url_add_field'> <span py:replace="field.display(form.value_for(field, value))"> </span></td>	   
			</div> </div>  </tr>

	<!-- Last row lists has the buttons -->   
	  <tr>
	    <td>
		<img src="${tg.url('/static/images/spacer_khaki.jpg' )}" width = "20"  height="1"/> 
		<table class="btn_table" >
		  <tbody>
		    <tr>
		      <td id="button_col"><input type = "submit" name = "home" value = " OK "> </input>  </td>
		      <td id="button_col"><input type = "submit" name = "cancel" value = "Cancel"> </input>  </td>
		      <td>  </td>
		    </tr>
		  </tbody>
		</table>  
	      </td>
	    </tr> 
	    
   	<!-- end of container table--> 	 
	</tbody>
      </table>	
      <p> </p>
    </form>
  </body>                  
 </html>                       
    
    