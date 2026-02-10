import struct
from enum import IntEnum


class GGUFValueType(IntEnum):
    UINT8 = 0
    INT8 = 1
    UINT16 = 2
    INT16 = 3
    UINT32 = 4
    INT32 = 5
    FLOAT32 = 6
    BOOL = 7
    STRING = 8
    ARRAY = 9
    UINT64 = 10
    INT64 = 11
    FLOAT64 = 12


_simple_value_packing = {
    GGUFValueType.UINT8: "<B",
    GGUFValueType.INT8: "<b",
    GGUFValueType.UINT16: "<H",
    GGUFValueType.INT16: "<h",
    GGUFValueType.UINT32: "<I",
    GGUFValueType.INT32: "<i",
    GGUFValueType.FLOAT32: "<f",
    GGUFValueType.UINT64: "<Q",
    GGUFValueType.INT64: "<q",
    GGUFValueType.FLOAT64: "<d",
    GGUFValueType.BOOL: "?",
}

value_type_info = {
    GGUFValueType.UINT8: 1,
    GGUFValueType.INT8: 1,
    GGUFValueType.UINT16: 2,
    GGUFValueType.INT16: 2,
    GGUFValueType.UINT32: 4,
    GGUFValueType.INT32: 4,
    GGUFValueType.FLOAT32: 4,
    GGUFValueType.UINT64: 8,
    GGUFValueType.INT64: 8,
    GGUFValueType.FLOAT64: 8,
    GGUFValueType.BOOL: 1,
}


def get_single(value_type, file):
    if value_type == GGUFValueType.STRING:
        value_length = struct.unpack("<Q", file.read(8))[0]
        value = file.read(value_length)
        try:
            value = value.decode('utf-8')
        except:
            pass
    else:
        type_str = _simple_value_packing.get(value_type)
        bytes_length = value_type_info.get(value_type)
        value = struct.unpack(type_str, file.read(bytes_length))[0]

    return value


def load_metadata(model_file):
    """Load GGUF metadata with file validation."""
    from pathlib import Path
    
    # CRITICAL: Validate file before reading
    model_file = Path(model_file)
    
    # Check file exists
    if not model_file.exists():
        logger.warning(f"Model file not found: {model_file}")
        return None
    
    # Check file size (minimum 1KB for valid GGUF)
    file_size = model_file.stat().st_size
    MIN_VALID_SIZE = 1024  # 1KB minimum
    
    if file_size < MIN_VALID_SIZE:
        logger.warning(f"Model file too small ({file_size} bytes): {model_file.name}")
        logger.warning(f"Expected minimum: {MIN_VALID_SIZE} bytes")
        
        # Auto-delete corrupt files
        try:
            model_file.unlink()
            logger.info(f"Deleted corrupt file: {model_file.name}")
        except Exception as e:
            logger.error(f"Could not delete corrupt file: {e}")
        
        return None
    
    # Now safe to read
    try:
        with open(model_file, 'rb') as file:
            # Read magic number
            magic_bytes = file.read(4)
            if len(magic_bytes) < 4:
                logger.error(f"Could not read GGUF header: {model_file.name}")
                return None
            
            GGUF_MAGIC = struct.unpack("<I", magic_bytes)[0]
            
            # Verify GGUF magic number (0x46554747 = "GGUF")
            EXPECTED_MAGIC = 0x46554747
            if GGUF_MAGIC != EXPECTED_MAGIC:
                logger.error(f"Invalid GGUF magic number in {model_file.name}")
                logger.error(f"Expected: 0x{EXPECTED_MAGIC:08X}, Got: 0x{GGUF_MAGIC:08X}")
                return None
            
            
    return metadata
