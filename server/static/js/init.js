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
            Core.printTable()
        });
        $('#delimiter').bind("propertychange change click keyup input paste", function () {
            _csv.delimiter = $(this).val() || '"'
            Core.printTable()
        });
        $('#header').click(function () {
            _csv.header = $(this).is(":checked")
            Core.printTable()
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
    printTable: function () {
        var navigator = new LineNavigator(_csv.data);
        $('#dateSelect').html('<option value="" disabled selected>Choose your options</option>');
        navigator.readLines(0, 10, function (err, index, lines, isEof, progress) {
            var html = '<table class="striped">';
            if (_csv.header) {
                var h = lines[0].split(_csv.separator);
                html += ("<thead><tr>" + $.map(h, function (c, i) {
                    return "<th data-id='" + i + "'>" + c + "<div class='columnselection_wrapper'>" + Core.addRHS(i) + "</div>"
                }).join("") + "</tr></thead>");
                //fill the dateSelect
                $.each(h, function (k, v) {
                    $('#dateSelect')
                        .append($("<option></option>")
                            .attr("value", k)
                            .text(v));
                });

                lines.shift()
            }
            else {
                var l = lines[0].split(_csv.separator).length;

                html += ("<thead><tr>");
                for (var i = 0; i < l; i++) {
                    html += ("<th data-id='" + i + "'>" + i + "<div class='columnselection_wrapper'>" + Core.addRHS(i) + "</div></th>")

                    //fill the dateSelect
                    $('#dateSelect')
                        .append($("<option></option>")
                            .attr("value", i)
                            .text(i));
                }
                html += ("<thead><tr>");
            }
            if (lines && lines.length > 0) {
                html += '<tbody>';
                lines.forEach(function (line) {
                    html += ("<tr>" + $.map(line.split(_csv.separator), function (c) {
                        return "<td class=" + (c == _csv.separator ? 'missing' : '') + ">" + c + "</td>";
                    }).join("") + "</tr>\r\n");
                });
                html += '</tbody>';
            }
            html += '</table>';
            $('#table').html(html);
            _csv.sides.lhs = [];
            _csv.sides.rhs = [];
            Core.attachTableHandlers()
            $('select').material_select();
        });
    },
    printResult: function (data, el) {
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
    raiseError: function(msg, el){
        $(el).html( '<div class="card-panel red lighten-1 white-text"><div class="row"><div class="col s12 errormessage" id="message"><i class="material-icons">warning</i> '+msg+'</div></div></div>')
    },
    validate: function () {
        if (_csv.selection == 0 && _csv.sides.rhs.length == 0) {
            Core.raiseError('Please select a valid RHS',"#result");
            $('#error').fadeIn()
            return false;
        }
        if (_csv.selection == 1 && (_csv.sides.rhs.length == 0 || _csv.sides.lhs.length == 0)) {
            Core.raiseError('Please select valids RHS and LHS',"#result");
            $('#error').fadeIn()
            return false;
        }
        $('#error').hide();
        return true;
    },
    addLHS: function (id) {
        return "<a class='waves-effect waves-light btn lhs unchecked'data-id='" + id + "' data-side='lhs'>lhs</a>"
    },
    addRHS: function (id) {
        return "<a class='waves-effect waves-light btn rhs unchecked'data-id='" + id + "' data-side='rhs'>rhs</a>"
    },
    loader: function(el){
        console.log('loading')
        console.log(el)

        $(el).html('    <div class="preloader-wrapper big active"><div class="spinner-layer spinner-red"><div class="circle-clipper left"><div class="circle"></div></div><div class="gap-patch"><div class="circle"></div></div><div class="circle-clipper right"><div class="circle"></div></div></div></div>')
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
