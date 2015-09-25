<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Welcome to the Synovate Web Analysis Tool</title>
</head>
  <body>
      <p align="left">
        <img border="0" src="/static/images/spacer1.JPG" width="280" height="25"/>
        <h2><u>Welcome to the Synovate Web Analysis Tool</u></h2>
      </p>  
      <div style="width:200px;height:100px;overflow-y:auto;overflow-x:auto;border:1px solid black;">      
        <table id="results">
         <tbody >
          <tr>
            <th >Date</th>
            <th >Polarity</th>
            <th >Content</th>
            <th >Link</th>
            

          </tr>                 
          <tr>
            <td  width = "200" height="1">  </td>
            <td  width = "200" height="1">  </td>
            <td  width = "500" height="1">  </td>
            <td  width = "100" height="1">  </td>
          </tr>
          <tr py:for="p in cont">
            <td class = "inactive" width="25%"> <span py:content = "p.dateaccessed"> Placeholder for Date </span> </td>
            <td class = "inactive" width="10%"> <span py:content = "p.polarity"> Placeholder for Polarity </span> </td>
            <td class = "inactive" width="70%"> <span py:content = "p.cont"> Placeholder for Content </span> </td>
            <td class = "inactive" width="10%"> <u>link</u> </td>
             </tr>
         </tbody> 
        </table>
        

      </div>
</body>
</html>
