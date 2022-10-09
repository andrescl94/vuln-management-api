function main {
    export PATH

    for input in ${buildInputs[@]}; do
        PATH="${input}/bin:${PATH}"
    done

    mkdir "${out}" \
    && sed \
        -e "s#__bash__#${bash}#g" \
        -e "s#__src__#${src}#g" \
        -e "s#__PATH__#${PATH}#g" \
        "${entrypoint}" \
    > "${out}/run.sh" \
    && chmod 755 "${out}/run.sh"
}

main "${@}"