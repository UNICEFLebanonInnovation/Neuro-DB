function loadTables() {
  
    $('table').each( (tb_idx, table) => {
        
        $('#'+$(table).attr('id')+' tr').each( (tr_idx,tr) => {
            var width=0;
            
            $(tr).children('td').each( (td_idx, td) => {
            if(td_idx < parseInt($(table).attr('fixed')))
            {
                width += (td_idx == 0)?0:$('#'+$(table).attr('id')+' th:nth-child('+td_idx+')').outerWidth()  ;
                $(td).css("left",width);
                $(td).addClass('sticky-column');
            }
            
            });
            var width=0; 
            $(tr).children('th').each( (td_idx, td) => {
            if(td_idx < parseInt($(table).attr('fixed')))
            {
                width += (td_idx == 0)?0:$('#'+$(table).attr('id')+' th:nth-child('+td_idx+')').outerWidth() ;
                // console.log(width);
                $(td).css("left",width);
                $(td).addClass('sticky-column');
            }
            
            });
            
        });
        });
    
 
}

window.onresize = loadTables;
