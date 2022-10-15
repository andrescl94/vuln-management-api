function main {
    export PATH
    export EXECUTABLE_PATH
    export PYTHONPATH
    local varName
    local varValue
    local varNames=($envNames)
    local varValues=($envValues)
    local executablePath="${out}/${executable}"

    for input in ${buildInputs[@]}; do
        PATH="${input}/bin:${PATH}"
    done

    for library in ${pathLibraries[@]}; do
        EXECUTABLE_PATH="${library}/bin:${EXECUTABLE_PATH}" \
        && if [ -d "${library}/lib/python3.10" ]; then
            PYTHONPATH="${library}/lib/python3.10/site-packages:${PYTHONPATH}"
        fi
    done

    mkdir -p "${out}/bin" \
    && cp "${entrypoint}" "${executablePath}" \
    && for varIndex in ${!varNames[@]}; do
        varName="${varNames[$varIndex]}" \
        && varValue="${varValues[$varIndex]}" \
        && sed -i "s#__${varName}__#${varValue}#g" "${executablePath}"
    done \
    && sed -i \
      -e "s#__bash__#${builder}#g" \
      -e "s#__PATH__#${EXECUTABLE_PATH}#g" \
      -e "s#__PYTHONPATH__#${PYTHONPATH}#g" \
      "${executablePath}" \
    && chmod 755 "${executablePath}"
}

main "${@}"
