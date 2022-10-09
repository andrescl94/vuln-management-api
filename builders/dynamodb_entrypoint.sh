#!__bash__/bin/bash

function main {
    export PATH
    local infraSrc
    local tempDir

    PATH="__PATH__" \
    && infraSrc="__src__" \
    && tempDir="$(mktemp -d)" \
    && cp "${infraSrc}"/* "${tempDir}/" \
    && echo "TMPDIR: ${tempDir}" \
    && pushd "${tempDir}" \
        && terraform init \
    && popd
}

main "${@}"