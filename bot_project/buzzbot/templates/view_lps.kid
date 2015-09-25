<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<head>
  <meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
  <meta http-equiv="Pragma" content="no-cache"/>
   
  <link href="/static/css/style.css" media="screen" rel="Stylesheet" type="text/css" />
  <script type="text/javascript">
        function popup(mylink, windowname) {
          if (! window.focus)
            return true;
          var href;
          if (typeof(mylink) == 'string')
            href=mylink;
          else
            href=mylink.href;
          window.open(href, windowname, 'width =500,height=350,scrollbars=no, resizable=yes');
          return false;
        }
  </script>
</head>
<body>
  <div id="header">
    <table>
      <tr>
        <td class="logo">
          <img src="/static/images/computerKhaki.png" />
        </td>
        <td class="title">
          <h3>Build a Custom Listening Post Here</h3>
        </td>
        <td class="logo">
          <img src="/static/images/computerKhaki.png" />
        </td>
      </tr>
      <tr> ${msg} </tr>
    </table>
  </div>

  <form xmlns:py="http://purl.org/kid/ns#"
	class="tableform"
	name="${form}"
	action="${action}">

    <fieldset>
      <table class="grid">
	<thead>
	  <tr>
	    <th>Name</th>
	    <th>Owner</th>
	    <th>Description</th>
	    <th>Edit</th>
	    <th>Delete</th>
	    <th>View</th>
	  </tr>
	</thead>
	<tbody>
	  <!-- Lists the name, description and link to edit  -->         
	  <tr py:for="s, o, e, d, v   in zip(lps, owner, editlink, deletelink, viewlink)">
	    <td py:content="s.name">Name</td>
	    <td py:content="o">Owner</td>
	    <td py:content="s.description">Description</td>
	    <!-- link to edit --> 
	    <td>
	      <a href="${e}"><img src="${tg.url('/static/images/edit.gif' )}" title="edit" width="12"  height="12" border="0"></img></a>
	    </td>
	    <td>
	      <!-- links to delete only if active (there's no link passed in if user lacks permission -->                   
	      <span py:if="len(d) > 0">    
		<a href="${d}"><img src="${tg.url('/static/images/delete.gif' )}" title="delete" width="12"  height="12" border="0"></img></a>     
	      </span>    
	    </td>
	    <td>
	      <!-- link to view -->    
	      <span py:if="len(v) > 0"> 
		<a href="${v}"><img src="${tg.url('/static/images/viewicon.jpg' )}" title="view" width="12"  height="12" border="0"></img></a>        
	      </span> 
	    </td>      
	  </tr>
	</tbody>
      </table>
      <!-- end of main table for the lps-->

      <div>
	<input type="submit" name="home" value="Home"/>
	<input type="submit" name="new" value=" New "/>
	<span py:if="isadmin==True">
	  <input type="submit" name="admin" value=" Admin "/>
	</span>
      </div>
    </fieldset>
  </form>
</body>                  
</html>                       
    
    