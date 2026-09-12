cmake_minimum_required(VERSION 3.16)
project(retrom_gbe_pokemini LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXECUTABLE_SUFFIX ".mjs")
file(GLOB MIN_SOURCES ../min/*.cpp)
file(GLOB COMMON_SOURCES ../common/*.cpp)
add_executable(gbe-pokemini host.cpp ${MIN_SOURCES} ${COMMON_SOURCES})
target_include_directories(gbe-pokemini PRIVATE ..)
target_compile_options(gbe-pokemini PRIVATE -O2 -sUSE_SDL=2)
target_link_options(gbe-pokemini PRIVATE -O2 -sUSE_SDL=2 -sMODULARIZE=1 -sEXPORT_ES6=1
  -sEXPORT_NAME=createGBEPokeMini -sALLOW_MEMORY_GROWTH=1 -sMAXIMUM_MEMORY=268435456
  -sFORCE_FILESYSTEM=1 -sENVIRONMENT=web -sEXIT_RUNTIME=0 --no-entry
  "-sEXPORTED_RUNTIME_METHODS=['FS']")
