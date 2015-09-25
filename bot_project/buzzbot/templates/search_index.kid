<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Welcome to the Synovate Web Analysis Tool</title>
<link href="/static/css/style.css" media="screen" rel="Stylesheet" type="text/css" />

</head>
  <body>
      <p align="left">
        <img border="0" src="../static/images/spacer1.JPG" width="280" height="25">
        <u>Web Searches</u>
      </p>
      <div>      
        <table id="results">
         <tbody >
          <tr>
            <th >ID</th>
            <th >Name</th>
            <th >Description</th>

          </tr>                 
          <tr>
          <a href="#Link("body_attribute.html?L_processareaid=$P.ProcessAreaId")">$!P.Label</a>
            <td width="100"> <img src="${tg.url('/static/images/spacer_table.jpg')}" width = "150"  height="1"/> </td>
            <td width="100"> <img src="${tg.url('/static/images/spacer_table.jpg')}" width = "150"  height="1"/> </td>
            <td width="500"> <img src="${tg.url('/static/images/spacer_table.jpg')}" width = "150"  height="1" /> </td>
            <td width="100"> <img src="${tg.url('/static/images/spacer_table.jpg')}" width = "150"  height="1"/> </td>
          </tr>
          <tr> 
            <td><a href="edit_form.kid">new</a><td>
          <tr>  
          <tr py:for="p in cont">
            <td class = "inactive"> <span py:content = "p.id"> Placeholder for id </span> </td>
            <td class = "inactive"> <span py:content = "p.name"> Placeholder for name </span> </td>
            <td class = "inactive"> <span py:content = "p.description">Placeholder for description </span> </td>
            <td class = "inactive">  
		<a href="document.location.href='${tg.url('/edit_search/%s' % p.id)}'" </a>
		</td>		
	  </tr>
         </tbody> 
        </table>
      </div>
</body>
</html>
