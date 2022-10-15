function main {
    export PATH
    export PYTHONPATH
    local executablePath="/bin/test-python"

    for input in ${buildInputs[@]}; do
        PATH="${input}/bin:${PATH}"
        if [ -d "${input}/lib/python3.10" ]; then
            PYTHONPATH="${input}/lib/python3.10/site-packages:${PYTHONPATH}"
        fi
    done

    mkdir -p "${out}/bin" \
    && sed \
        -e "s#__bash__#${bash}#g" \
        -e "s#__PATH__#${PATH}#g" \
        -e "s#__PYTHONPATH__#${PYTHONPATH}#g" \
        "${entrypoint}" \
    > "${out}${executablePath}" \
    && chmod 755 "${out}${executablePath}"
}

main "${@}"
