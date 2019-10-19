import ctypes


lib = ctypes.CDLL('./libgojsonnet.so')

lib.jsonnet_evaluate_snippet.argtypes = [
    ctypes.c_void_p,
    ctypes.c_char_p,
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_int),
]
lib.jsonnet_evaluate_snippet.restype = ctypes.POINTER(ctypes.c_char)

lib.jsonnet_make.argtypes = []
lib.jsonnet_make.restype = ctypes.c_void_p

lib.jsonnet_string_output.argtypes = [
    ctypes.c_void_p,
    ctypes.c_int,
]

lib.jsonnet_realloc.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_char),
    ctypes.c_ulong,
]
lib.jsonnet_realloc.restype = ctypes.POINTER(ctypes.c_char)

t = [
    ctypes.c_void_p,
    ctypes.c_char_p,
    ctypes.c_char_p,
]
lib.jsonnet_ext_var.argtypes = t

lib.jsonnet_evaluate_file.argtypes = [
    ctypes.c_void_p,
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_int),
]
lib.jsonnet_evaluate_file.restype = ctypes.POINTER(ctypes.c_char)

lib.jsonnet_destroy.argtypes = [
    ctypes.c_void_p
]
lib.jsonnet_destroy.restype = None

NATIVE_CALLBACK = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p,
                                   ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_int))

lib.jsonnet_native_callback.argtypes = [
    ctypes.c_void_p,
    ctypes.c_char_p,
    NATIVE_CALLBACK,
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_char_p),
]
lib.jsonnet_native_callback.restype = None

IMPORT_CALLBACK = ctypes.CFUNCTYPE(
    ctypes.c_char_p,
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_char),
    ctypes.POINTER(ctypes.c_char),
    # we use *int instead of **char to pass the real C allocated pointer, that we have to free
    ctypes.POINTER(ctypes.c_uint64),
    ctypes.POINTER(ctypes.c_int)
)

lib.jsonnet_import_callback.argtypes = [
    ctypes.c_void_p,
    IMPORT_CALLBACK,
    ctypes.c_void_p,
]
lib.jsonnet_import_callback.restype = None


def free_buffer(vm, buf):
    assert not lib.jsonnet_realloc(vm, buf, 0)


def to_bytes(buf):
    return ctypes.cast(buf, ctypes.c_char_p).value


def jsonnet_evaluate_file(vm, path):
    err = ctypes.c_int()
    err_ref = ctypes.byref(err)
    res = lib.jsonnet_evaluate_file(vm, path.encode(), err_ref)
    # res_decoded = to_bytes(res).decode()
    res_decoded = to_bytes(res)
    print(":result:", res_decoded)
    print(":err:", err)
    print(":err_ref:", err_ref)
    free_buffer(vm, res)
    return res_decoded


def jsonnet_ext_vars(vm, ext_vars_dict):
    for k, v in ext_vars_dict.items():
        lib.jsonnet_ext_var(vm, k.encode(), v.encode())


if __name__ == "__main__":
    err = ctypes.c_int()
    err_ref = ctypes.byref(err)
    vm = lib.jsonnet_make()

    print("\n\n==jsonnet_evaluate_file()==")
    result = jsonnet_evaluate_file(vm, "jsonnet_import_test/foo.jsonnet")

    print("\n\n==jsonnet_evaluate_file() with ext_vars==")
    ext_vars = {"key1": "val1", "key2": "val2"}
    jsonnet_ext_vars(vm, ext_vars)
    result = jsonnet_evaluate_file(vm, "jsonnet_import_test/ext_vars.jsonnet")
