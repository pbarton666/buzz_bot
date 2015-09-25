<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<head>
  <meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
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
	  <h3>Edit Search</h3>
	</td>
	<td class="logo">
	  <img src="/static/images/computerKhaki.png" />
	</td>
      </tr>
    </table>
  </div>

  <form xmlns:py="http://purl.org/kid/ns#"
      action = "${action}"
      class="tableform"
      value="${value}" 
      form="${form}"
      message="${message}"
      >
    <?python fields = dict([(f.name, f) for f in form.fields]) ?>
    <!-- Pass in the hidden fields.--> 	
      <div py:for="field in form.fields" py:if="field.field_class=='hiddenfield'"
	   py:replace="field.display(form.value_for(field, value))"/>

      <fieldset>

	<fieldset>
	  <legend>Identification</legend>
	  <?python id_fields = [ f for f in form.fields if f.name in ('name', 'description') ] ?>
	  <table>
	    <tr py:for="field in id_fields">
	      <th class="label" py:content="field.label"/>
	      <td py:content="field.display(form.value_for(field, value))"/>
	    </tr>
	    <?python id_fields = [ f for f in form.fields if f.name in ('is_client_worthy', 'is_public') ] ?>
	    <tr py:for="field in id_fields">
	      <th/>
	      <td><label>${field.label} <span py:replace="field.display(form.value_for(field, value))"/></label></td>
	    </tr>
	  </table>
	</fieldset>

	<fieldset>
	  <legend>URL-level Specifications</legend>
	  <p>
	    (please separate words/phrases with commas)
	  </p>
	  <table>
	    <tr py:for="field in (fields['urlsearchfor'], fields['urleliminate'])">
	      <th class="label" py:content="field.label"/>
	      <td py:content="field.display(form.value_for(field, value))"/>
	    </tr>
	  </table>
	</fieldset>

	<fieldset>
	  <legend>Content-level Specifications</legend>
	  <table>
	    <?python field = fields['targetword'] ?>
	    <tr>
	      <th class="label" py:content="field.label"/>
	      <td py:content="field.display(form.value_for(field, value))"/>
	    </tr>
	    <tr py:for="field in (fields['searchstring'], fields['eliminationwords'])">
	      <th class="label" py:content="field.label"/>
	      <td py:content="field.display(form.value_for(field, value))"/>
	    </tr>
	  </table>
	</fieldset>





	<div>
	  <input type="submit" name="home" value=" OK "/>
	  <input type="submit" name="urls" value=" Urls "/>
	  <input type="submit" name="web" value=" Web "/>
	</div>

	  <table class = "help_table">
	    <tbody>
	      <tr><td><u>Notes:</u></td></tr>
	      <tr><td>You *need* to specify a company/client (this serves to identify meaningful content).</td></tr>
	      <tr><td>The URL-level specifications screen an entire site's contents (just like a Google search).</td></tr>
	      <tr><td>Content-level specifications further screen each block of content</td></tr>
	      <tr><td>The "Urls" button allows you to review the URLS identified with this search or paste in your own.</td></tr>
	      <tr><td>  </td></tr>
	      <tr><td>"Test" acquires some content already on the database. <u>This clears all existing content/URLs</u></td></tr>
	      <tr><td>"Web" gathers new content and takes a couple minutes.  This may take a couple minutes.  <u>This clears all existing content/URLs</u></td></tr>

	     </tbody>
	   </table>  

      </fieldset>
    </form>
  </body>                  
 </html>                       
    
    
