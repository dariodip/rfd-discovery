var app = angular.module("rfdApp", ['ui.materialize', 'ngSanitize', 'ngFileUpload'])
    .config(['$interpolateProvider', function ($interpolateProvider) {
        //flask Jinja's templating conflict fix
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    }]);

Object.map = function (o, f, ctx) {
    ctx = ctx || this;
    var result = {};
    Object.keys(o).forEach(function (k) {
        result[k] = f.call(ctx, o[k], k, o);
    });
    return result;
}
Array.prototype.remove = function (from, to) {
    var rest = this.slice((to || from) + 1 || this.length);
    this.length = from < 0 ? this.length + from : from;
    return this.push.apply(this, rest);
};
Array.prototype.get = function (i) {
    return this[i];
};