<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    >
<head>
  <meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
  <link href="/static/css/style.css" media="screen" rel="Stylesheet" type="text/css" />
  
</head>
<body>
  <form xmlns:py="http://purl.org/kid/ns#"
      action = "${action}"
      class="tableform"
      value="${value}" 
      >
    <!-- Pass in the hidden fields.--> 	
	  <div py:for="field in form.fields">
		<div py:if="field.field_class=='hiddenfield'">
		  <span py:replace="field.display(form.value_for(field, value))">
		  </span>
		</div>     
	      </div>
	<tr class = 'edit_search_header'>
	  <td >
	    <h3> 
	      <img border="0" src="/static/images/computerKhaki.png" width="50" height="50" /> 
	      <img border="0" src="/static/images/spacer_khaki.JPG" width="100" height="1" /> 
	      Edit Listening Post 
	      <img border="0" src="/static/images/spacer_khaki.JPG" width="100" height="1" /> 
	      <img border="0" src="/static/images/computerKhaki.png" width="50" height="50" /> 
	    </h3>
	  </td>
	</tr>  

    <!-- Outer container table --> 
    <table class = 'lp_frame'>
      <tbody>

	<!-- First row has general lp options --> 
	      <table class = "lp options" >
	       <tbody >  
		<!-- We'll pass in all the fields that are not hidden and
		    don't begin with "ck_ (these are used to toggle searches).--> 	  	  
		  <div py:for="field in form.fields">	      
		     <span py:if="field.field_class!='hiddenfield'">
			  <tr>
			    <td width = "150"> ${field.label}</td>
			    <td  width = "400">
			     <span py:content="field.display(form.value_for(field, value))"></span>
			     </td>		   		  
			  </tr>
		      </span>  	
		  </div>
		</tbody> 
	      </table>
	
	<!-- Second row has topic heading --> 	      
	<tr><td><h2>Available searches</h2></td></tr>
	
      <div class = 'edit_lp_all_searches_div'>
	<!-- Third row has headers table --> 
	    <tr width = "100%"> 
	       
		<td>
		      <table class="search_header_table" > <tbody >
			<tr id='lp_header'>
			  <td id = 'checkcol'>   </td>
			  <td id = 'namecol_searchs'><h1> Name </h1></td>
			  <td id = 'ownercol_searchs'><h1>Owner </h1></td>
			  <td id = 'desccol_searchs'><h1>Description </h1></td>
			  <td id = 'actionscol_searchs'><h1>Edit| Delete  </h1></td>
			</tr>   
			</tbody> </table>		
	       </td>  
	    </tr>	
	<!-- Fourth row lists the available searches --> 
	  <tr>
	    <td>
		<div class = 'search_scroll_div'>  <!-- div element provides scrolling --> 
		  <table  class = 'search_list'  >
		    <tbody >
 			<tr py:for="s, e, d, c, o   in zip(searches, editlink, deletelink, checks, owner)">
			  <td id = "checkcol"  > ${c.display()} </td>
			  <td id = "namecol_searchs" > <span py:content = "s.name"> Name </span> </td>
			  <td id = "ownercol_searchs"> <span py:content = "o"> Owner </span> </td>
			  <td id = "desccol_searchs"> <span py:content = "s.description"> Description </span> </td>
			  <!-- link to edit--> 
			    <td id = "actionscol_searchs">
			      <img src="${tg.url('/static/images/spacer_khaki.jpg' )}" width = "20"  height="1"/> 	
				<a href= "${e}">
				  <img src="${tg.url('/static/images/edit.gif' )}" title = "edit" width = "12"  height="12" border = "0"></img></a>  
			  <!-- link to delete, shown only if delete operation is valid for this user -->   
			      <span py:if="len(d) > 0">
				<img src="${tg.url('/static/images/spacer_khaki.jpg' )}" width = "20"  height="1"/> 
				  <a href= "${d}">
				    <img src="${tg.url('/static/images/delete.gif' )}" title = "delete" width = "12"  height="12" border = "0"></img></a>	
				</span>  		
			  </td>	 
			</tr>
		     </tbody> 
		    </table>
		  </div>
		</td>
	      </tr>	
	    </div>    <!-- end of edit_lp_all_searches_div (headers and searches rows) --> 
	
	<!-- Fifth row lists has the buttons -->   
	  <tr>
	    <td>
		<img src="${tg.url('/static/images/spacer_khaki.jpg' )}" width = "20"  height="1"/> 
		<table class="btn_table" >
		  <tbody>
		    <tr>
		      <td id="button_col"><input type = "submit" name = "home" value = "  OK  "> </input>  </td>
		      <td id="button_col"><input type = "submit" name = "newsearch" value = "New Search"> </input>  </td>
		      <td id="button_col"><input type = "submit" name = "run" value = "Run Options"> </input>  </td>

		      <td> </td><td> </td><td> </td>
		    </tr>
		  </tbody>
		</table>  
	      </td>
	    </tr>  
		 
       
	</tbody>
       </table>  <!-- end of main container table -->  
    </form>
   
  </body>                  
 </html>                       
    
    