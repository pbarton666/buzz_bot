<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Welcome to the Synovate Web Analysis Tool</title>
</head>
  <body>
      <div>      
        <table id="results">
         <tbody >
          <tr>
            <th >ID</th>
            <th >Date</th>
          </tr>                 
          <tr>
            <td  width="100"> <img src="${tg.url('/static/images/b_clear.gif')}"  height="1" /> </td>
            <td width="300"> <img src="${tg.url('/static/images/b_clear.gif')}" height="1"/> </td>
          </tr>
          <tr py:for="p in pageData">
            <td class = "active" width="20%"> <span py:content = "p.urlText">Placeholder for URL ID </span> </td>
            <td class = "inactive" width="80%"> <span py:content = "p.urlText">Placeholder for Date </span> </td>
          </tr>
         </tbody> 
        </table>
      </div>
</body>
</html>
