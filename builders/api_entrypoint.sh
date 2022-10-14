#!__bash__/bin/bash

function main {
    export PATH
    export PYTHONPATH
    local outPath

    export AWS_ACCESS_KEY_ID="testKey"
    export AWS_SECRET_ACCESS_KEY="secretKey"
    export AWS_DEFAULT_REGION="us-east-1"
    export JWE_ENCRYPTION_KEY='{"k":"ila0UViizq2Aqk7H4Duai-9sYTHbUXkKp0elOFbYTkE","kty":"oct"}'
    export JWT_SIGNING_KEY="c10c5cde58a9e4396b00f824673bebd5cb9686b4f6ceba197f1d4dbf61e585be5ac366d484831fd60114f95093fc4d76c53bc97035e25cfe31eec20f2d0a8527"
    export OAUTH_GOOGLE_CLIENT_ID="960572939057-p40kke46pr4acakcnpil52igbtl875h1.apps.googleusercontent.com"
    export OAUTH_GOOGLE_SECRET="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"

    PATH="__PATH__" \
    && outPath="__outPath__" \
    && PYTHONPATH="${outPath}/src:__PYTHONPATH__" \
    && pushd "${outPath}" \
      && { dynamodb-local & } \
      && sleep 10 \
      && uvicorn --host 0.0.0.0 src.app.main:APP

}

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
main "${@}"
