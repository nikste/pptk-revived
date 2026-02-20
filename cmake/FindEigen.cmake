include(FindPackageHandleStandardArgs)

find_path(Eigen_INCLUDE_DIR Eigen/Core
  PATHS /usr/include/eigen3 /usr/local/include/eigen3 /usr/include /usr/local/include)

find_package_handle_standard_args(Eigen REQUIRED_VARS Eigen_INCLUDE_DIR)
