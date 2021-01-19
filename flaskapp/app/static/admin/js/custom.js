$('.swal-confirm').click(function(){
    let bulk = $(this).hasClass('swal-confirm-bulk');
    if (bulk){
        let ids = $("input[name='ids[]']").val();
        if (ids == ""){
            swal({
                title: "Nothing Selected?",
                text: "There are no elements selected",
                icon: "info",
            });
            return false;
        }
    }
    let warn = $(this).attr('swal-warn');
    let e = this;
    swal({
        title: "Are you sure?",
        text: warn + "\n\nOnce done, this action cannot be reverted",
        icon: "warning",
        buttons: true,
        dangerMode: true,
    })
        .then((willDelete) => {
            if (willDelete) {
                let form = $(e).next($('form.swal-submit'));
                form.submit();
            } else {
                return false;
            }
        });
    return false;
});
$('.bulk-checkbox').click(function (){
    let val = $(this).attr('data-value');
    let inp = $(this).prev($('#checkbox-'+val));
    let ids = $("input[name='ids[]']");
    let vals = ids.val();
    if (vals != ""){
        vals = vals.split(',');
    }
    else {
        vals = [];
    }
    if (vals.constructor !== Array){
        vals = [vals];
    }
    if (! inp[0].checked){
        if (!(vals.includes(""+val))){
            vals.push(val);
        }
    }
    else {
        if (vals.includes(val)){
            vals = vals.filter((value, index, arr) => {return parseInt(value) != parseInt(val);});
        }
    }
    ids.val(vals);
});
