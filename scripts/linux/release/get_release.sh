#! /bin/bash
# requires curl and jq on PATH: https://stedolan.github.io/jq/

# get release 
# user: user's name 
# repo: the repo's name
# token: github api user token
# tag: name of the tag pushed 
get_release() {
    user=$1
    repo=$2
    token=$3
    tag=$4

    command="curl -s -o release.json -w '%{http_code}' \
         --request GET \
         --header 'authorization: Bearer ${token}' \
         --header 'content-type: application/json' \
         https://api.github.com/repos/$user/$repo/releases/tags/$tag"
    http_code=`eval $command`
    if [ $http_code == "201" ]; then
        echo "get release:"
        cat release.json
    else
        echo "get release failed with code '$http_code':"
        cat release.json
        echo "command:"
        echo $command
        return 1
    fi
}

token=$(<~/gh_token)
version=$1
get_release "REG-Linux" "REG-Linux" $token $version
