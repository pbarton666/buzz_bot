<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<head>
  <meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''" />
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
  window.open(href, windowname, 'width=800,height=600,scrollbars=yes, resizable=yes');
  return false;
}
  </script>  
  <script src="/static/javascript/MochiKit.js" type="text/javascript"></script>
  <script src="/static/javascript/content.js?" type="text/javascript"></script>
</head>
<body>
    <div id="header">
      <table>
	<tr>
	  <td class="logo">
	    <img src="/static/images/computerKhaki.png" />
	  </td>
	  <td class="title">
	    <h3>Examine Search Content</h3>
	  </td>
	  <td class="logo">
	    <img src="/static/images/computerKhaki.png" />
	  </td>
	</tr>
      </table>
    </div>

  <form xmlns:py="http://purl.org/kid/ns#"
    class="tableform"
    action="" method="post">
    <fieldset>
      <div class="scrolling">
	<table class="searchresults">
	  <thead>
	    <tr>
	      <th>Score</th>
	      <th>Date</th>
	      <th>Content</th>
	      <th/>
	    </tr>
	  </thead>
	  <tbody id="pane">
	    <tr id="placeholder">
	      <td colspan="4">Processing...</td>
	    </tr>
	  </tbody>
	</table>
      </div>
      <div>
	<button onclick="window.location='${back}'; return false">Done</button>
      </div>
    </fieldset>
    <input type="hidden" id="queue_url" name="queue_url" value="${queue_url}"/>
  </form>
</body>
</html>

    
    