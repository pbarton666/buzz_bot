<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<head>
  <meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
  <meta http-equiv="Pragma" content="no-cache"/>
   
  <link href="/static/css/style.css" media="screen" rel="Stylesheet" type="text/css" />

</head>
<body>
  <div id="header">
    <table>
      <tr>
        <td class="logo">
          <img src="/static/images/computerKhaki.png" />
        </td>
        <td class="title">
          <h3>Administrative Options</h3>
        </td>
        <td class="logo">
          <img src="/static/images/computerKhaki.png" />
        </td>
      </tr>
    </table>
  </div>

  <form xmlns:py="http://purl.org/kid/ns#"
	class="tableform"
	name="${form}"
	action="${action}">	<fieldset>
	  <legend>Choose Sites To Query</legend>
	  <?python id_fields = [ f for f in form.fields ] ?>
	  <table>
	    <tr py:for="field in id_fields">
	      <th class="label" py:content="field.label"/>
	      <td py:content="field.display(form.value_for(field, value))"/>
	    </tr>
	  </table>    
	
	<div>
	  <input type="submit" name="ok" value="Run Now"/>
	  <input type="submit" name="cancel" value="Cancel"/> 
      </div>
    </fieldset>
  </form>
</body>                  
</html>                       
    
    