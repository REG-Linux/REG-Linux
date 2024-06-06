#! /bin/bash
# requires curl and jq on PATH: https://stedolan.github.io/jq/

# upload a release file. 
# this must be called only after a successful create_release, as create_release saves 
# the json response in release.json. 
# token: github api user token
# file: path to the asset file to upload 
# name: name to use for the uploaded asset
upload_release_file() {
    token=$1
    file=$2
    name=$3

    url=`jq -r .upload_url release.json | cut -d{ -f'1'`
    command="\
      curl -s -o upload.json -w '%{http_code}' \
           --request POST \
           --header 'authorization: Bearer ${token}' \
           --header 'Content-Type: application/octet-stream' \
           -T ${file}
           ${url}?name=${name}"
    http_code=`eval $command`
    if [ $http_code == "201" ]; then
        echo "asset $name uploaded:"
        jq -r .browser_download_url upload.json
    else
        echo "upload failed with code '$http_code':"
        cat upload.json
        echo "command:"
        echo $command
        return 1
    fi
}

token=$(<~/gh_token)
arch=$1

# Upload boot-$BOARD.tar.zst file(s)
for FILE in "output/$arch/images/reglinux/images"*"/boot-"*".tar.zst"
do
    if [ -f $FILE ]; then
        echo "Upload $FILE to GitHub..."
        upload_release_file "$token" "${FILE}" "${FILE##*/}"
    fi
done

# Upload reglinux-$BOARD-$VERSION.img.gz file(s)
for FILE in "output/$arch/images/reglinux/images/"*"/reglinux-"*".img.gz"
do
    if [ -f $FILE ]; then
        echo "Upload $FILE to GitHub..."
        upload_release_file "$token" "${FILE}" "${FILE##*/}"
    fi
done
