
#include <pybind11/pybind11.h>

#define FORCE_IMPORT_ARRAY
#include <xtensor-python/pyarray.hpp>

#include "xtensor_bindings.hpp"

PYBIND11_MODULE(aspn23_xtensor, m) {
	xt::import_numpy();
	add_bindings(m);
}
