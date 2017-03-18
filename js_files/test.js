System.register([], function(exports_1, context_1) {
    "use strict";
    var __moduleName = context_1 && context_1.id;
    var Test;
    return {
        setters:[],
        execute: function() {
            Test = (function () {
                function Test(t) {
                    this.t = t;
                }
                Test.prototype.getT = function () {
                    return this.t;
                };
                return Test;
            }());
            exports_1("Test", Test);
        }
    }
});
