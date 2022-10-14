#!__bash__/bin/bash

function kill_dynamoDb {
    local pid

    pid="$(mktemp)" \
    && if ! lsof -t -i:8022 > "${pid}"; then
        echo "DynamoDB instance is not currently running"
    fi \
    && while read -r process; do
        if kill -9 "${process}"; then
            echo "Killing running DynamoDB instance"
        else
            echo "Unable to terminate DynamoDB instance" \
            && return 1
        fi \
        && sleep 1
    done < "${pid}"
}

function main {
    export AWS_ACCESS_KEY_ID="testKey"
    export AWS_SECRET_ACCESS_KEY="testSecretKey"
    export PATH
    local infraSrc
    local tempDir

    PATH="__PATH__" \
    && infraSrc="__src__" \
    && tempDir="$(mktemp -d)" \
    && cp -r --no-preserve=mode,ownership "${infraSrc}" "${tempDir}/terraform" \
    && echo "${tempDir}" \
    && pushd "${tempDir}" \
        && echo "Terminating existing instances of DynamoDb..." \
        && kill_dynamoDb \
        && echo "Unpacking DynamoDb..." \
        && unzip -u "__dynamoDbZip__" \
        && echo "Launching DynamoDb..." \
        && {
            java \
                -Djava.library.path=./DynamoDBLocal_lib \
                -jar DynamoDBLocal.jar \
                -inMemory \
                --port 8022 \
                -sharedDb &
        } \
    && popd \
    && pushd "${tempDir}/terraform" \
        && terraform init \
        && terraform apply -auto-approve \
    && popd \
    && wait
}

trap kill_dynamoDb EXIT
main "${@}"
