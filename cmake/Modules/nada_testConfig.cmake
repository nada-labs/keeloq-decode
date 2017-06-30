INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_NADA_TEST nada_test)

FIND_PATH(
    NADA_TEST_INCLUDE_DIRS
    NAMES nada_test/api.h
    HINTS $ENV{NADA_TEST_DIR}/include
        ${PC_NADA_TEST_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    NADA_TEST_LIBRARIES
    NAMES gnuradio-nada_test
    HINTS $ENV{NADA_TEST_DIR}/lib
        ${PC_NADA_TEST_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(NADA_TEST DEFAULT_MSG NADA_TEST_LIBRARIES NADA_TEST_INCLUDE_DIRS)
MARK_AS_ADVANCED(NADA_TEST_LIBRARIES NADA_TEST_INCLUDE_DIRS)

