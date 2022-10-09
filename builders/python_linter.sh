function main {
    export PATH
    export PYTHONPATH

    for input in ${buildInputs[@]}; do
        PATH="${input}/bin:${PATH}"
        if [ -d "${input}/lib/python3.10" ]; then
            PYTHONPATH="${input}/lib/python3.10/site-packages:${PYTHONPATH}"
        fi
    done

    pushd "${projectSrc}" \
        && mypy \
            --config-file .mypy.ini \
            --python-executable "${pythonExecutable}" \
            "src/" \
        && prospector \
            --full-pep8 \
            --strictness veryhigh \
            --test-warnings \
            "src/" \
    && popd \
    && touch "${out}"
}


main ${@}