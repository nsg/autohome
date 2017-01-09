$(document).ready(function() {
    $(".lamp_hue").each(function(index) {
        $(this).spectrum({
            change: function(color) {
                hsl = color.toHsl();

                phue_h = parseInt(65535 * (hsl.h / 360.0));
                phue_s = parseInt(254 * hsl.s);
                phue_l = parseInt(254 * hsl.l);

                name = $(this).parent().parent().children(".light_name").text();
                url = "/set-hue/" + name + "/" + phue_h + "/" + phue_s + "/" + phue_l;

                $.get(url, function(data) {});
            }
        });
    });

    $(".lamp_lock").each(function(index) {
        $(this).click(function() {
            name = $(this).parent().parent().children(".light_name").text();
            if (this.checked) {
                url = "/set-hue/" + name + "/lock/1";
            } else {
                url = "/set-hue/" + name + "/lock/0";
            }
            $.get(url, function(data) {});
        });
    });
});
