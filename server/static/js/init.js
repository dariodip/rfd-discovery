(function ($) {
    $(function () {
        $('.button-collapse').sideNav();
        $('.parallax').parallax();
    });
})(jQuery);

var Core = {

    attachHandlers: function () {
        $('#semantic').change(function () {
            console.log($(this).is(":checked"))
            _csv.semantic = $(this).is(":checked")
        });
        $('#separator').change(function () {
            _csv.separator = $(this).val()
            printTable()
        });
        $('#delimiter').bind("propertychange change click keyup input paste", function () {
            _csv.delimiter = $(this).val() || '"'
            printTable()
        });
        $('#header').click(function () {
            _csv.header = $(this).is(":checked")
            printTable()
        });
        $('input[type=radio][name=selectcol]').change(function () {
            var $ths = $('#table thead th');
            _csv.selection = this.value;
            switch (this.value) {
                case '0':
                    $.each($ths, function (i, v) {
                        var _id = $(this).data('id');
                        $('.columnselection_wrapper', $(this)).html(Core.addRHS(_id))
                        $('#selectcolinfo').show()
                    });
                    break;
                case '1':
                    $.each($ths, function (i, v) {
                        var _id = $(this).data('id')
                        $('.columnselection_wrapper', $(this)).html(Core.addRHS(_id) + Core.addLHS(_id))
                        $('#selectcolinfo').show()
                    });
                    break;
                default:
                    $.each($ths, function (i, v) {
                        $('.columnselection_wrapper', $(this)).html('')
                        $('#selectcolinfo').hide()
                    })
            }
            _csv.sides.lhs = [];
            _csv.sides.rhs = [];
            Core.attachTableHandlers()

        });
    },
    attachTableHandlers: function () {
        $('.lhs').click(function () {
            var id = $(this).data('id');
            if ($(this).data('active')) {
                $(this).data('active', false);
                $(this).addClass("unchecked");
                _csv.sides.lhs.remove(id)
            } else {
                $(this).data('active', true)
                $(this).removeClass("unchecked");

                $(this).siblings(".rhs").data('active', false);
                $(this).siblings(".rhs").addClass("unchecked");
                _csv.sides.lhs.push(id)
            }
        });
        $('.rhs').click(function () {
            var id = $(this).data('id');
            if ($(this).data('active')) {
                $(this).data('active', false);
                $(this).addClass("unchecked");
                _csv.sides.rhs = []
            } else {
                $('.rhs').data('active', false)
                $('.rhs').addClass("unchecked");

                $(this).data('active', true)
                $(this).removeClass("unchecked");
                $(this).siblings(".lhs").data('active', false);
                $(this).siblings(".lhs").addClass("unchecked");
                _csv.sides.rhs = []
                _csv.sides.rhs.push(id)
            }
            console.log(_csv.sides)
        });

    },
    printResult: function(data,el) {
        var res = '';
        $.each(data, function (c, csv) {
            var lines = csv.split('\n');
            var comb = JSON.parse(c);
            $.each(comb, function (k, v) {
                res += '<p><span class="' + k + '">' + k + '</span> ' + v.join(' ') + '</p>';
            });
            res += "<table class='striped'>";
            lines.forEach(function (line) {
                res += ("<tr>" + $.map(line.split(_csv.separator), function (c) {
                    return "<td>" + c + "</td>";
                }).join("") + "</tr>\r\n");
            });
            res += "</table><br>";
        });
        $(el).html(res);
    },
    validate: function() {
        if (_csv.selection == 0 && _csv.sides.rhs.length == 0) {
            $('#message', '#error').html('Please select a valid RHS')
            $('#error').fadeIn()
            return false;
        }
        if (_csv.selection == 1 && (_csv.sides.rhs.length == 0 || _csv.sides.lhs.length == 0)) {
            $('#message', '#error').html('Please select valids RHS and LHS')
            $('#error').fadeIn();
            return false;
        }
        $('#error').hide();
        return true;
    },
    addLHS: function (id) {
            return "<a class='waves-effect waves-light btn lhs unchecked'data-id='" + id + "' data-side='lhs'>lhs</a>"
        },
    addRHS: function(id) {
            return "<a class='waves-effect waves-light btn rhs unchecked'data-id='" + id + "' data-side='rhs'>rhs</a>"
        }
};

    function scrollTo(el) {
        $('html, body').animate({
            scrollTop: $(el).offset().top
        }, 1000);
    }
    if (!Array.prototype.remove) {
        Array.prototype.remove = function (val) {
            var i = this.indexOf(val);
            return i > -1 ? this.splice(i, 1) : [];
        };
    }