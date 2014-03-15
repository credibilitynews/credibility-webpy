angular.module('app', [])
.controller('NewLinkCtrl', function($scope, $http) {
    $scope.suggestTitle = function() {
        if($scope.url.length>11 && $scope.url.match(/http(s)?:\/\/.*/)){
          $scope.status = true;
          $http.get('/suggest/title?url='+$scope.url)
            .success(function (data) {
              if(data['title'] && !$scope.title)
                $scope.title = data['title'];
              $scope.status = false;})
            .error(function(data, status, headers, config) {
              $scope.status = false;
            });
        }
    }});
