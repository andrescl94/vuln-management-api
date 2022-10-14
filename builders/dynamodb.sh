function main {
    export PATH
    local executablePath="/bin/dynamodb-local"

    for input in ${buildInputs[@]}; do
        PATH="${input}/bin:${PATH}"
    done

    mkdir -p "${out}/bin" \
    && sed \
        -e "s#__bash__#${bash}#g" \
        -e "s#__dynamoDbZip__#${dynamoDbZip}#g" \
        -e "s#__src__#${src}#g" \
        -e "s#__PATH__#${PATH}#g" \
        "${entrypoint}" \
    > "${out}${executablePath}" \
    && chmod 755 "${out}${executablePath}"
}

main "${@}"
