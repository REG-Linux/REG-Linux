#! /bin/bash
# requires curl and jq on PATH: https://stedolan.github.io/jq/

# create a new release 
# user: user's name 
# repo: the repo's name
# token: github api user token
# tag: name of the tag pushed 
create_release() {
    user=$1
    repo=$2
    token=$3
    tag=$4

    command="curl -s -o release.json -w '%{http_code}' \
         --request POST \
         --header 'authorization: Bearer ${token}' \
         --header 'content-type: application/json' \
         --data '{\"tag_name\": \"${tag}\"}' \
         https://api.github.com/repos/$user/$repo/releases"
    http_code=`eval $command`
    if [ $http_code == "201" ]; then
        echo "created release:"
        cat release.json
    else
        echo "create release failed with code '$http_code':"
        cat release.json
        echo "command:"
        echo $command
        return 1
    fi
}

token=$(<~/gh_token)
version=$1
create_release "REG-Linux" "REG-Linux" $token $version
