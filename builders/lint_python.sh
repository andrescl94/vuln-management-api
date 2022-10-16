function main {
    export PATH
    export PYTHONPATH

    for input in ${buildInputs[@]}; do
        PATH="${input}/bin:${PATH}"
        if [ -d "${input}/lib/python3.10" ]; then
            PYTHONPATH="${input}/lib/python3.10/site-packages:${PYTHONPATH}"
        fi
    done

    PYTHONPATH="${projectSrc}/src:${PYTHONPATH}" \
    && pushd "${projectSrc}" \
        && for dir in "src/" "test/"; do
            echo "Running linters over ${dir} directory" \
            && mypy \
                --config-file .mypy.ini \
                --python-executable "${pythonExecutable}" \
                "${dir}" \
            && prospector \
                --full-pep8 \
                --strictness veryhigh \
                --test-warnings \
                "${dir}" \
            || return 1
        done \
    && popd \
    && touch "${out}"

}

main "${@}"
