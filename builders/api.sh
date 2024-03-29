#!__bash__

function main {
    export PATH
    export PYTHONPATH
    local tempDir

    export AWS_ACCESS_KEY_ID="testKey"
    export AWS_SECRET_ACCESS_KEY="secretKey"
    export AWS_DEFAULT_REGION="us-east-1"
    export JWE_ENCRYPTION_KEY='{"k":"ila0UViizq2Aqk7H4Duai-9sYTHbUXkKp0elOFbYTkE","kty":"oct"}'
    export JWT_SIGNING_KEY="c10c5cde58a9e4396b00f824673bebd5cb9686b4f6ceba197f1d4dbf61e585be5ac366d484831fd60114f95093fc4d76c53bc97035e25cfe31eec20f2d0a8527"
    export OAUTH_GOOGLE_CLIENT_ID="960572939057-p40kke46pr4acakcnpil52igbtl875h1.apps.googleusercontent.com"
    export OAUTH_GOOGLE_SECRET="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"
    export SESSION_SECRET_KEY="596454d2-d3b6-4323-a07b-709e7c78016d"

    PATH="__PATH__" \
    PYTHONPATH="__PYTHONPATH" \
    && tempDir=$(mktemp -d) \
    && cp -r --no-preserve=mode,ownership "__projectSrc__"/* "${tempDir}" \
    && pushd "${tempDir}" \
      && PYTHONPATH="${tempDir}/src:${PYTHONPATH}" \
      && { dynamodb & } \
      && sleep 10 \
      && uvicorn --host 0.0.0.0 --no-access-log src.app.main:APP

}

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
main "${@}"
