/**
 * Created by huangzehui on 7/13/15.
 */
$(function()
{
       if($("#id_ref_mark").is(':checked')){
        $("#id_ref_file").removeAttr("readonly");
    }else{
        $("#id_ref_file").attr("readonly","readonly");
    }


    $('#id_ref_mark').change(
        function(){
            if($("#id_ref_mark").is(':checked')){
                $("#id_ref_file").removeAttr("readonly");
            }else{
                $("#id_ref_file").attr("readonly","readonly");
            }
        }
    )

})   
