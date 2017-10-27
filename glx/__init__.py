import OpenGL
OpenGL.SIZE_1_ARRAY_UNPACK = False
# ERROR_CHECKING = True
# ERROR_LOGGING = False
# ERROR_ON_COPY = False
# ARRAY_SIZE_CHECKING = True
# STORE_POINTERS = True
# WARN_ON_FORMAT_UNAVAILABLE = False
# FORWARD_COMPATIBLE_ONLY = False
# SIZE_1_ARRAY_UNPACK = True
# USE_ACCELERATE = True
# CONTEXT_CHECKING = False
#
# FULL_LOGGING = False
# ALLOW_NUMPY_SCALARS = False
# UNSIGNED_BYTE_IMAGES_AS_STRING = True
# MODULE_ANNOTATIONS = False

import OpenGL.GL as gl

from .ortho_projection import *
from .ortho_view import *
from .shader_program import *
from .shader_programs import *
from .tools import next_power_of_two
from .transformations import *
from .viewport import *
from .wrappers import *
from .font import *


