// input-spinner.js
$(document).on('htmx:afterSettle', function () {
    $('.input-spinner').remove();

    $('.qty').each(function () {
        $(this).inputSpinner({
            decrementButton: '<i class="icon-minus"></i>',
            incrementButton: '<i class="icon-plus"></i>',
            groupClass: 'input-spinner',
            buttonsClass: 'btn-spinner',
            buttonsWidth: '26px'
        });
    });
});

$(window).on("popstate", function () {
    $(document).ready(function () {
        $(".input-spinner").remove(); // or $(".input-spinner").hide();
        location.reload(true);
    });
});