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

            console.log(response.data);

            let classesReferencedBy = {};

            // First, get a map of all external references for each class
            // The Tooling API returns for each class, what classes and method IT calls
            // But not what external methods call IT. So I won't to build that
            angular.forEach(response.data, function(apexClass, apexClassKey) {

                if (apexClass.SymbolTable != null && 'externalReferences' in apexClass.SymbolTable) {

                    angular.forEach(apexClass.SymbolTable.externalReferences, function(extReference, extReferenceKey) {

                        // Get the children occurrences for the reference
                        children_lines = [];
                        angular.forEach(extReference.references, function(lineReference, lineReferenceKey) {
                            children_lines.push({
                                name: 'Line ' + lineReference.line + ' Column ' + lineReference.column
                            });
                        });

                        // Build the reference object to store against the obkect
                        reference_object = {
                            name: apexClass.Name,
                            children: children_lines
                        }

                        if (extReference.name in classesReferencedBy) {

                            // If list exists, add the occurence to the existing lsit
                            classesReferencedBy[extReference.name].push(reference_object);
                        }
                        else {

                            // Otherwise, create a new list
                            classesReferencedBy[extReference.name] = [reference_object];
                        }
                    });
                }
            });

            console.log(classesReferencedBy);

            // Clear the data
            $scope.root.children.length = 0;

            // Iterate over the response
            angular.forEach(response.data, function(apexClass, apexClassKey) {

                // Push each class into the table
                $scope.root.children.push({
                    name: apexClass.Name,
                    IsReferenced: (apexClass.Name in classesReferencedBy),
                    Id: apexClass.Id,
                    AppId: apexClass.AppId,
                    TopLevel: true,
                    children: [
                        {
                            name: 'Referenced By',
                            children: apexClass.Name in classesReferencedBy ? classesReferencedBy[apexClass.Name] : []
                        },
                        {
                            name: 'External References',
                            children: $scope.getChildren(apexClass, 'externalReferences')
                        },
                        {
                            name: 'Methods',
                            children: $scope.getChildren(apexClass, 'methods')
                        },
                        {
                            name: 'Properties',
                            children: $scope.getChildren(apexClass, 'properties')
                        },
                        {
                            name: 'Variables',
                            children: $scope.getChildren(apexClass, 'variables')
                        },
                    ]
                });
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

    $scope.getChildren = function(apexClass, child_name) {

        let children = [];

        // Build the list of methods
        if (apexClass.SymbolTable != null && child_name in apexClass.SymbolTable) {
            angular.forEach(apexClass.SymbolTable[child_name], function(child, childKey) {
                children.push({
                    name: child.name
                });
            });
        }

        return children;
    };

});