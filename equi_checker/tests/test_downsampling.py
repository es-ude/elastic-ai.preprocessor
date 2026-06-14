from src.loader import CompileLoader
from dataclasses import dataclass
import numpy as np

@dataclass
class SettingsDownSampling:
    sampling_rate: float
    dsr:           int

DefaultSettingsDownSampling = SettingsDownSampling(
        sampling_rate = 1000.0,
        dsr           = 10,
)

class DownSampling:
    def __init__(self, settings: SettingsDownSampling):
        self._settings = settings

    @property
    def sampling_rate_out(self) -> float:
        return self._settings.sampling_rate / self._settings.dsr
    
    def do_simple(self, uin: np.ndarray) -> np.ndarray:
        n = uin.size // self._settings.dsr
        data = uin[:n * self._settings.dsr]
        return data.reshape(-1, self._settings.dsr).mean(axis=1)

loader = CompileLoader(
    headers="./c_funcs/downsampling/downsampling_cdef.h",
    sources=["./c_funcs/downsampling/downsampling.c"],
    build_dir="build_test_downsampling",
    module_name="c_downsampling",
)
loader.load()
c_do_simple = loader.get("do_simple")
ffi = loader.ffi()

def _call_c_do_simple(settings: SettingsDownSampling, uin: np.ndarray) -> np.ndarray:
    """Wrapper: np-Array -> C-Pointer -> np-Array"""
    in_arr = np.ascontiguousarray(uin, dtype=np.float32)
    out_size = len(in_arr) // settings.dsr
    out_arr = np.zeros(out_size, dtype=np.float32)
    c_s = ffi.new("SettingsDownSampling *", {"sampling_rate": settings.sampling_rate, "dsr": settings.dsr})
    c_in = ffi.cast("const float *", in_arr.ctypes.data)
    c_out = ffi.cast("float *", out_arr.ctypes.data)

    c_do_simple(c_s, c_in, len(in_arr), c_out)
    return out_arr

def _py_do_simple(settings: SettingsDownSampling, uin: np.ndarray) -> np.ndarray:
    return DownSampling(settings).do_simple(uin)

# Basistest
def test_do_simple_basic():
    settings = DefaultSettingsDownSampling
    uin = np.arange(100, dtype=np.float32)
    assert np.allclose(_py_do_simple(settings, uin), _call_c_do_simple(settings, uin))

def test_do_simple_edge_cases():
    for dsr in [1, 2, 5, 10, 20, 50]:
        settings = SettingsDownSampling(sampling_rate=1000.0, dsr=dsr)
        uin = np.arange(dsr * 5, dtype=np.float32)
        py_result = _py_do_simple(settings, uin)
        c_result  = _call_c_do_simple(settings, uin)
        assert np.allclose(py_result, c_result, atol= 1e-5), (
            f"Fehler bei dsr={dsr}: py={py_result}, c={c_result}"
        )
