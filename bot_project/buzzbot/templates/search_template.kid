<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>

<title>Welcome to the Synovate Web Analysis Tool</title>
<link href="/static/css/style.css" media="screen" rel="Stylesheet" type="text/css" />

</head>

<body>
<form xmlns:py="http://purl.org/kid/ns#"
    action = "${action}"
    class="tableform"
>

        <table class="outer_table">
            <tr>
              <th>Sidebar</th>
              <th>Main</th>
            </tr>
            <tr>
                <td>
                  <table class = "sidebar_table">  
                    <tr>
                        <td>sidebar 1</td>
                    </tr>    
                  </table> <!-- end of sidebar table -->       
                </td>  
                
               <td>
                 <table class = "inner_table" py:attrs="table_attrs">
                    <tr>
                        <th>
                            <label  class="fieldlabel"
                                    for="${field.field_id}"
                                    py:content="field.label"
                            />
                        </th>
                        <td>
                            <span   py:if="error_for(field)"
                                    class="fielderror" py:content="error_for(field)"
                            >
                                <br />
                            </span>    
                            <span   py:replace="field.display(value_for(field), **params_for(field))"
                             />
                            <span   py:if="field.help_text"
                                    class="fieldhelp" py:content="field.help_text"
                            />
                         </td>
                    </tr>
                    <tr>
                        <td>&#160;</td>
                        <td py:content="submit.display(submit_text)"
                        />
                    </tr>
                    
                  </table>               
               </td> <!-- end of inner table -->       
               
             </tr>  
        </table>  <!-- end of outer table -->          
    </form>  
  </body>                  
</html>                        
    
    