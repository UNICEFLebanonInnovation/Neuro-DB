/* Project specific Javascript goes here. */

/*
Formatting hack to get around crispy-forms unfortunate hardcoding
in helpers.FormHelper:

    if template_pack == 'bootstrap4':
        grid_colum_matcher = re.compile('\w*col-(xs|sm|md|lg|xl)-\d+\w*')
        using_grid_layout = (grid_colum_matcher.match(self.label_class) or
                             grid_colum_matcher.match(self.field_class))
        if using_grid_layout:
            items['using_grid_layout'] = True

Issues with the above approach:

1. Fragile: Assumes Bootstrap 4's API doesn't change (it does)
2. Unforgiving: Doesn't allow for any variation in template design
3. Really Unforgiving: No way to override this behavior
4. Undocumented: No mention in the documentation, or it's too hard for me to find
*/
$('.form-group').removeClass('row');

var $el, $ps, $up, totalHeight;

$(".sidebar-box button").click(function() {

  totalHeight = 0

  $el = $(this);
  $p  = $el.parent();
  $up = $p.parent();
  $ps = $up.find("p:not('.read-more')");

  // measure how tall inside should be by adding together heights of all inside paragraphs (except read-more paragraph)
  $ps.each(function() {
    totalHeight += $(this).outerHeight();
  });

  $up
    .css({
      // Set height to prevent instant jumpdown when max height is removed
      "height": $up.height(),
      "max-height": 9999
    })
    .animate({
      "height": totalHeight
    });

  // fade out read-more
  $p.fadeOut();

  // prevent jump-down
  return false;

});

$('.expanded-all').click(function(){
    $('.panel-collapse').addClass('in');
    $('.panel-collapse').attr('aria-expanded', 'true');
});

$('.collapse-all').click(function(){
    $('.panel-collapse').removeClass('in');
    $('.panel-collapse').attr('aria-expanded', 'false');
});

function getHeader()
{
    var header = {
        'Authorization': 'Token '+user_token,
        'HTTP_REFERER': href_full_path,
        'Cookie': 'token=Token '+user_token,
        'X-CSRFToken': csrftoken
    };
    return header;
}

function update_data_server(url, data)
{
    $.ajax({
        type: "PUT",
        url: url,
        data: data,
        cache: false,
        headers: getHeader(),
        dataType: 'json',
        success: function (response, result, jqXHR) {
            if(jqXHR.status == 200){
            }
        },
        error: function (response) {
            console.log(response);
        }
    });
}
