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
        $scope.success = true;
        $scope.error = null;
        $scope.loading = true;

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
            $scope.loading = false;

            console.log($scope.classes);
        }, 
        function errorCallback(response) {

            $scope.success = false;
            $scope.error = response;
            $scope.loading = false;
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

    $scope.openModal = function(class_name, class_id) {

        // Set the class name
        $('#viewCodeModalLabel').text(class_name);

        // Show the loading gif
        $('#viewCodeBody').html('<div class="text-center"><img src="/static/images/loading.gif" alt="Loading" /></div>');

        // Launch the modal
        $('#viewCodeModal').modal('show');

        $http({
            method: 'GET',
            url: '/apexclass/' + class_id + '/'
        })
        .then(function successCallback(response) {

            // Insert the content and init the syntax highlighter
            var $content = $('<pre class="highlight">' + response.data + '</pre>');
            $content.syntaxHighlight();
            $('#viewCodeBody').html($content);
            $.SyntaxHighlighter.init();
        }, 
        function errorCallback(response) {

            $('#viewCodeBody').html(
                '<div class="alert alert-danger" role="alert">Error loading Apex Class: ' + response + '</div>'
            );
        });
    };

});