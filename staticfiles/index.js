/**
 * Created by huangzehui on 7/7/15.
 */

var focusTag = '' ;

function r_confirm(url){
    if(confirm('are you sure ?')){
        window.location.href=url;
    }
}

function add_enum(){
    html = '<div class="control-group required enum"> <label class="control-label" for="id_name">value, name, description</label> ' +
      '<div class="controls"> <input stype="width:50px" type="text" name="enum_valu"  /> ' +
                ' <input stype="width:50px" type="text" name="enum_name"  />' +
                ' <input stype="width:50px" type="text" name="enum_desc"  />' +
                '&nbsp;&nbsp; <a href="javascript:;" onclick="$(this).parent().parent().remove()"  id="remove-enum" ><i class="icon-minus"></i></a> ' +

      '</div> '
// '<div class="controls"> <input stype="width:50px" type="text" name="enum"  /> </div> ' +
//                '</div>  ';
    $('#id_type').parent().parent().after(html);
}
function remove_enum(){
    $(this).remove()
}


$(function(){
    $('#id_type').change(function(){
        $('.integer').remove()
        $('.enum').each(function(){
            $(this).remove();
        })
        $('#add-enum').remove()
        if($(this).val() == 'enum') {
//            html='<div>Name:<input stype="width:50px" type="text" name="name[]"  /> Value:<input stype="width:50px" type="text" name="value[]"  /> Descript:<input stype="width:50px" type="text" name="desc[]"  /></div>'
//            html='<div class="control-group required"> value:<input stype="width:50px" type="text" name="name[]"  /> </div>'
            html = '<div class="control-group required enum"> ' +
                '<label class="control-label" for="id_name">value, name, description</label>' +
                '<div class="controls"> ' +
                '<input stype="width:50px" type="text" name="enum_valu"  /> ' +
                ' <input stype="width:50px" type="text" name="enum_name"  />' +
                ' <input stype="width:50px" type="text" name="enum_desc"  />' +
                '&nbsp;&nbsp; <a href="javascript:;" onclick="$(this).parent().parent().remove()"  id="remove-enum" ><i class="icon-minus"></i></a> ' +
                '</div> ' +
//                '<div class="controls"> <input stype="width:50px" type="text" name="enum_name"  /> </div> ' +
//                '<div class="controls"> <input stype="width:50px" type="text" name="enum_desc"  /> </div> ' +
                '</div>  ';
            html_add = '&nbsp;&nbsp; <a href="javascript:;" onclick="add_enum()"  id="add-enum" ><i class="icon-plus"></i></a> ';
            $(this).parent().parent().after(html);
            $(this).after(html_add);
        }else if($(this).val() == "integer" || $(this).val() == "real"){
//            $('.enum').each(function(){
//            $(this).remove();
//            })
//            $('#add-enum').remove()


            html = '<div class="control-group required integer"> ' +
                '<label class="control-label" for="id_name1">min, max</label>' +
                '<div class="controls">' +
                ' <input stype="width:50px" type=number step=0.1 name="integer_min"/>' +
                ' <input stype="width:50px" type=number step=0.1 name="integer_max" />' +
                '</div></div>'
            $(this).parent().parent().after(html);
        }else{
//            $('.enum').each(function(){
//                $(this).remove();
//            })
//            $('#add-enum').remove()

        }

    });

    $('input').click(function(){
        focusTag =$(this).attr('id');
    })
    $('textarea').click(function(){
        focusTag =$(this).attr('id');
    })

    $('.badge-success').each(function(){
        $(this).click(function(){
            tag = $(this).text();
//            alert(tag)
            old = $('#'+focusTag).val();
//            alert(focusTag)
            $('#'+focusTag).val(old + tag );

        })

    })

        $('#id_type').parent().parent().after($('.integer'));
        $('#id_type').parent().parent().after($('.real'));
        $('#id_type').parent().parent().after($('.enum'));
        $('#id_type').after($('#add-enum'));
})
