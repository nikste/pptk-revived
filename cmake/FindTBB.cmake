include(FindPackageHandleStandardArgs)

find_path(TBB_INCLUDE_DIR
  NAMES tbb/tbb.h oneapi/tbb/tbb.h
  PATHS /usr/include /usr/local/include)

find_library(TBB_tbb_LIBRARY tbb
  PATHS /usr/lib /usr/local/lib /usr/lib/x86_64-linux-gnu)

find_library(TBB_tbbmalloc_LIBRARY tbbmalloc
  PATHS /usr/lib /usr/local/lib /usr/lib/x86_64-linux-gnu)

# On Linux/Mac the runtime library is the same as the link library
if(WIN32)
  find_file(TBB_tbb_RUNTIME tbb.dll)
  find_file(TBB_tbbmalloc_RUNTIME tbbmalloc.dll)
else()
  set(TBB_tbb_RUNTIME ${TBB_tbb_LIBRARY} CACHE FILEPATH "Path to tbb runtime library")
  set(TBB_tbbmalloc_RUNTIME ${TBB_tbbmalloc_LIBRARY} CACHE FILEPATH "Path to tbbmalloc runtime library")
endif()

find_package_handle_standard_args(TBB
  REQUIRED_VARS
    TBB_INCLUDE_DIR
    TBB_tbb_LIBRARY
    TBB_tbbmalloc_LIBRARY
    TBB_tbb_RUNTIME
    TBB_tbbmalloc_RUNTIME
)
