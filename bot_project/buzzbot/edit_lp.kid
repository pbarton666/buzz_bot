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
	    <h3>Edit Listening Post</h3>
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
      searches="${searches}"
      checks="${checks}"	  
      editlink="${editlink}"
      deletelink="${deletelink}"
      owner = "${owner}"
      >

      <!-- Pass in the hidden fields.-->
      <div py:for="field in form.fields" py:if="field.field_class=='hiddenfield'"
	   py:replace="field.display(form.value_for(field, value))"/>

      <fieldset>
	<table>
	  <tbody>
	    <tr py:for="field in form.fields" py:if="field.field_class != 'hiddenfield'">
	      <td class="label">${field.label}</td>
	      <td width="400">
		${field.display(form.value_for(field, value))}
	      </td>
	    </tr>
	  </tbody>
	</table>

	<fieldset>
	  <legend>Available Searches</legend>
	  <table>
	    <thead>
	      <tr>
		<th></th>
		<th>Name</th>
		<th>Owner</th>
		<th>Description</th>
		<th>Edit</th>
		<th>Delete</th>
	      </tr>
	    </thead>
	    <tbody>
	      <tr py:for="s, e, d, c, o in zip(searches, editlink, deletelink, checks, owner)">
		<td>${c.display()}</td>
		<td py:content="s.name">Name</td>
		<td py:content="o">Owner</td>
		<td py:content="s.description">Description</td>
		<!-- link to edit--> 
		<td>
		  <img src="${tg.url('/static/images/spacer_khaki.jpg' )}" width = "20"  height="1"/> 	
		  <a href= "${e}"><img
		  src="${tg.url('/static/images/edit.gif' )}" title = "edit" width = "12"  height="12" border = "0"/></a>
		</td>
		<td>
		  <!-- link to delete, shown only if delete operation is valid for this user -->   
		  <span py:if="len(d) > 0">
		    <img src="${tg.url('/static/images/spacer_khaki.jpg' )}" width = "20"  height="1"/> 
		    <a href= "${d}"><img
		    src="${tg.url('/static/images/delete.gif' )}" title = "delete" width = "12"  height="12" border = "0"/></a>
		  </span>
		</td>	 
	      </tr>
	    </tbody>
	  </table>

	  <div>
	    <input type = "submit" name = "home" value = "  OK  "/>
	    <input type = "submit" name = "newsearch" value = " New Search "/>
	    <input type = "submit" name = "web" value = " Web "/>
	    ("Web" gathers new content and takes a couple minutes.)
	  </div>
	</fieldset>
      </fieldset>
    </form>
  </body>                  
 </html>                       
    
    
