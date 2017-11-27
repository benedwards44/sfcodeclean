/*
    Angular controller for all the Job page logic
*/

var codeResultsApp = angular.module("codeResultsApp", ['ngResource','ngSanitize', 'adaptv.adaptStrap']);

codeResultsApp.controller("CodeResultsController", function($scope, $http, $q) {

    // On initation of controller
    $scope.init = function(slug) {

        // Job ID passed through from view
        $scope.slug = slug;
        $scope.classes = [];
        $scope.success = true;
        $scope.error = null;
        $scope.loading = true;  

        // Set an empty array for the table
        // Gets populated later
        $scope.root = {children: []}; 

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

            // Clear the data
            $scope.root.children.length = 0;

            // Iterate over the response
            angular.forEach(response.data, function(apexClass, apexClassKey) {

                // Build the child for methods and variables
                let class_object = {
                    name: apexClass.Name,
                    IsReferenced: apexClass.IsReferenced,
                    Id: apexClass.ApexClassId,
                    DatabaseId: apexClass.DatabaseId,
                    TopLevel: true
                };

                let childrenForClass = [];

                // If the class has class references
                if (apexClass.ReferencedBy.class) {

                    childrenForClass.push({
                        name: 'Class References',
                        children: $scope.getChildrenFromArray(apexClass.ReferencedBy.class)
                    });
                }

                // IF there are method references
                if (apexClass.ReferencedBy.methods && Object.keys(apexClass.ReferencedBy.methods).length > 0) {

                    childrenForClass.push({
                        name: 'Methods',
                        children: $scope.getChildrenFromObject(apexClass.ReferencedBy.methods)
                    });
                }

                if (apexClass.ReferencedBy.variables && Object.keys(apexClass.ReferencedBy.variables).length > 0) {

                    childrenForClass.push({
                        name: 'Variables',
                        children: $scope.getChildrenFromObject(apexClass.ReferencedBy.variables)
                    });
                }

                class_object.children = childrenForClass;

                $scope.root.children.push(class_object);
            });

            //$scope.classes = response.data;
            $scope.success = true;
            $scope.loading = false; 
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

    $scope.getChildrenFromArray = function(childRows) {

        let children = [];

        if (childRows) {

            for (var i = 0; i < childRows.length; i++) {
                children.push({name: childRows[i]});
            }
        }

        return children;
    };

    $scope.getChildrenFromObject = function(childRows) {

        let children = [];

        // Build the child object for the dictionary
        for (var name in childRows) {

            // Build the list of children for the given key
            children_for_object = [];

            let childLinesForProperty = childRows[name];

            for (var i = 0; i < childLinesForProperty.length; i++) {

                children_for_object.push({name: childLinesForProperty[i]});
            }

            children.push({
                name: name,
                children: children_for_object
            });
        }
        return children;
    };

});