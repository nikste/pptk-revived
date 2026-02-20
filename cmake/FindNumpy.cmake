include(FindPackageHandleStandardArgs)

if(NOT Numpy_INCLUDE_DIR)
  execute_process(
    COMMAND ${Python3_EXECUTABLE} -c "import numpy; print(numpy.get_include())"
    OUTPUT_VARIABLE Numpy_INCLUDE_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    ERROR_QUIET)
endif()

find_package_handle_standard_args(Numpy REQUIRED_VARS Numpy_INCLUDE_DIR)
