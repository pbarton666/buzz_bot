<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<head>
  <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
  <title>Login</title>
  <link href="/static/css/style.css" media="screen" rel="Stylesheet" type="text/css" />
</head>
<body class="login">
  <div id="header">
    <table>
      <tr>
        <td class="logo">
          <img src="/static/images/computerKhaki.png" />
        </td>
        <td class="title">
          <h3>Welcome to Buzz</h3>
        </td>
        <td class="logo">
          <img src="/static/images/computerKhaki.png" />
        </td>
      </tr>
    </table>
    <form action="${previous_url}" method="post">
      <fieldset>
	<legend>Please Login</legend>
	<table>
	  <tr>
	    <th><label for="user_name">User Name:</label></th>
	    <td><input class="loginField" type="text" id="user_name" name="user_name"/></td>
	  </tr>
	  <tr>
	    <th><label for="password">Password:</label></th>
	    <td><input class="loginField" type="password" id="password" name="password"/></td>
	  </tr>
	  <tr>
	    <td colspan="2" >
	      <input type="submit" name="login" value="Login"/>
	      <input py:if="forward_url" type="hidden" name="forward_url"
		     value="${forward_url}"/>
	      <div py:for="name,values in original_parameters.items()" py:strip="1">
		<input py:for="value in isinstance(values, list) and values or [values]"
		       type="hidden" name="${name}" value="${value}"/>    
	      </div>
	    </td>
	  </tr>
	</table>
      </fieldset>
    </form>
  </div>
</body>
</html>
