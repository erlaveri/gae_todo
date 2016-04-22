(function (angular) {
    var app = angular.module('app', [
        'ui.router',
        //'ui.router.util',
        //'ui.bootstrap',
        'ngResource',
        'ngMaterial'
        ////'ui.select',
        //'ngSanitize',
        //'cgNotify',
        //'ngStorage',
        //'file-model',
        //
        // 'app.factories',
        //'app.filters',
        // 'app.directives',
        //'app.services',
        // 'app.controllers'
    ]);
    window.app = app;


    app.config(['$stateProvider', '$locationProvider', '$urlRouterProvider', '$urlMatcherFactoryProvider',
        '$resourceProvider', '$httpProvider',
        function ($stateProvider, $locationProvider, $urlRouterProvider,
                  $urlMatcherFactoryProvider, $resourceProvider, $httpProvider) {

            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

            $locationProvider.html5Mode({
                enabled: true,
                requireBase: false
            });

            $resourceProvider.defaults.stripTrailingSlashes = false;
            $urlMatcherFactoryProvider.strictMode(false); //??

            $urlRouterProvider.rule(function ($injector, $location) {
                var path = $location.url();
                // check to see if the path already has a slash where it should be
                if (path[path.length - 1] === '/' || path.indexOf('/?') > -1) {
                    return;
                }
                if (path.indexOf('?') > -1) {
                    return path.replace('?', '/?');
                }
                return path + '/';
            });
        }]);

    app.controller('MainController', MainController);
    app.factory('Todo', TodoFactory);


    TodoFactory.$inject = ['$resource'];
    function TodoFactory($resource) {
        return $resource('/api/todo/:id/', null, {
            'patch': {method: 'PATCH'}
        });
    }

    MainController.$inject = ['$scope', 'Todo', '$state', '$window'];
    function MainController($scope, Todo, $state, $window) {
        $scope.gotolink = function (url) {
            $window.open(url, '_self');
        };

        $scope.addNewTodoState = true;
        $scope.newTodo = null;
        $scope.todos = Todo.query();


        $scope.SaveTodo = function () {
            Todo.save({text: $scope.newTodo}, function (data) {
                $scope.todos.push(data);
                $scope.newTodo = '';
            });

        };

        $scope.AddNewTodo = function () {
            $scope.addNewTodoState = false;
        };
        $scope.Cancel = function () {
            $scope.addNewTodoState = true;
        };
        $scope.DeleteTodo = function (todo) {
            Todo.delete(todo, function () {
                $scope.todos.splice($scope.todos.indexOf(todo), 1)
            });
        };

        $scope.ChangeTodo = function (todo) {
            if (!todo.disabled) {
                todo.disabled = true;
                Todo.patch({id: todo.id}, todo, function () {
                    todo.disabled = false;
                });
            }
        }
    }


    angular.bootstrap(document, ['app']);
})(angular);