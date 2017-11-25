/*
    Angular controller for all the Job page logic
*/

var codeResultsApp = angular.module("codeResultsApp", ['ngResource']);

codeResultsApp.controller("CodeResultsController", function($scope, $http, $q) {

    // On initation of controller
    $scope.init = function(slug) {

        // Job ID passed through from view
        $scope.slug = slug;
        $scope.classes = [];
        $scope.success = false;
        $scope.error = null;

        $scope.loadClasses(slug);
    };

    $scope.loadClasses = function(slug) {

        // Get list of profiles for the page
        $http({
            method: 'GET',
            url: '/job/json/' + $scope.slug + '/',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(function successCallback(response) {

            $scope.classes = response.data;
            $scope.success = true;

            console.log($scope.classes);
        }, 
        function errorCallback(response) {

            $scope.success = false;
            $scope.error = response;
        });
    };

    $scope.toggleIcons = function(class_id) {

        let $element = $(class_id);

        if ($($element).hasClass('in')) {

            $element.prev('tr').find(".fa-minus").removeClass("fa-minus").addClass("fa-plus");
        }
        else {
            $element.prev('tr').find(".fa-plus").removeClass("fa-plus").addClass("fa-minus");
        }
    };

});