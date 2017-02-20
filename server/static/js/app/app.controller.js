app.controller('appController', ["$scope", "$sce", 'Upload', '$timeout', function ($scope, $sce, Upload, $timeout) {

    $scope.model = ($scope.initModel = function() {
        return {
            separator: ';',
            missing: '?',
            semantic: false,
            header: true,
            selection: '0',
            datetime: '',
            sides: {
                lhs: [],
                rhs: []
            }
        };
    })();
    $scope.preview = {};

    $scope.upload = function (file) {
        $scope.loading = true;
        $scope.model.file = file;
        file.upload = Upload.upload({
            url: '/api/upload',
            data: $scope.model
        });

        file.upload.then(function (res) {
            if (res.data.error) {
                $scope.error = res.data.error;
            } else {
                $scope.result = {
                    mtxtime: res.data.mtxtime,
                    total: res.data.total,
                    timing: res.data.timing
                };
                $scope.result.data = Object.map(res.data.result, function (v, k, o) {
                    var line = v.split('\n');
                    return line.map(function (vv) {
                        return vv.split($scope.model.separator)
                    })
                });
            }
            $scope.loading = false;
        }, function (response) {
            if (response.status > 0)
                $scope.errorMsg = response.status + ': ' + response.data;
        }, function (evt) {
            file.progress = Math.min(100, parseInt(100.0 * evt.loaded / evt.total));
        });
    };
    $scope.resetComb = function () {
        $scope.model.sides.lhs = [];
        $scope.model.sides.rhs = [];
    };

    $scope.submit = function () {

        if ($scope.format_and_validation()) {
            $scope.upload($scope.file);
        }
    };
    $scope.range = function (start, end) {
        var r = [];
        for (var i = start; i < end; i++) {
            r.push(i)
        }
        return r;
    };
    $scope.getComb = function (comb) {
        var c = JSON.parse(comb);
        return Object.map(c, function (k, v) {
            return k.join(', ');
        });
    };
    $scope.parseInt = parseInt;
    $scope.setTableData = function () {
        if ($scope.model.header) {
            $scope.preview.ths = $scope._preview[0].split($scope.model.separator);
            $scope.preview.trs = $scope._preview.slice(1).map(function (line) {
                return line.split($scope.model.separator);
            })
        } else {
            var l = $scope._preview[0].split($scope.model.separator).length;
            $scope.preview.ths = $scope.range(0, l);
            $scope.preview.trs = $scope._preview.map(function (line) {
                return line.split($scope.model.separator);
            })
        }

    };
    $scope.toggleLhs = function (i) {
        var t = $scope.model.sides.lhs.indexOf(i);
        if (t > -1) {
            $scope.model.sides.lhs.splice(t, 1);
        } else {
            $scope.model.sides.lhs.push(i);
            var r = $scope.model.sides.rhs.indexOf(i);
            if (r > -1) {
                $scope.model.sides.rhs = [];
            }
        }
    };
    $scope.setRhs = function (i) {
        var r = $scope.model.sides.rhs.indexOf(i);
        $scope.model.sides.rhs = [];
        if (r === -1) {
            $scope.model.sides.rhs.push(i);
            var t = $scope.model.sides.lhs.indexOf(i);
            if (t > -1) {
                $scope.model.sides.lhs.splice(t, 1);
            }
        }
    };

    $scope.format_and_validation = function () {
        $scope.model.lhs = $scope.model.sides.lhs.join(',');
        $scope.model.rhs = $scope.model.sides.rhs.join(',');
        if ($scope.model.selection == 0 && !$scope.model.rhs) {
            $scope.error = "Please select valids RHS";
            return false;
        }
        else if ($scope.model.selection == 1 && (!$scope.model.rhs || !$scope.model.lhs)) {
            $scope.error = "Please select valids RHS and LHS";
            return false;
        }
        $scope.error = false;
        return true
    };

    $('#fileupload').bind('change', function (e) {
        var files = e.target.files;
        var file = files[0];
        var navigator = new LineNavigator(file);
        //file metadata
        $scope.details = 'FileType: ' + (file.type || 'n/a') + '<br />\n'
            + ' FileSize: ' + file.size + ' bytes<br />\n'
            + ' LastModified: ' + (file.lastModifiedDate ? file.lastModifiedDate.toLocaleDateString() : 'n/a') + '<br />\n';
        navigator.readLines(0, 10, function (err, index, lines, isEof, progress) {
            $scope._preview = lines;
            $scope.setTableData();
            $scope.$apply();
        });
        $scope.model = $scope.initModel();
    });
}]);