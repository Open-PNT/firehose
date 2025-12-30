from typing import List, Union, Dict
from cxxheaderparser.types import (
    PQName,
    FundamentalSpecifier,
    NameSpecifier,
    Type,
    Pointer,
    Array,
    Value,
    Token,
    FunctionType,
    DecoratedType,
    Parameter,
    Typedef,
)


# Returns type name of pointer (without *) if type_ is a pointer; otherwise None.
# Will filter on types listed in match_types such that only pointers with
# types in match_types will return the type name. All others will return None.
def is_pointer(
    type_: DecoratedType, match_types: List[str] = None
) -> Union[str, None]:
    if isinstance(type_, Pointer):
        if isinstance(type_.ptr_to, Type):
            first_segment = type_.ptr_to.typename.segments[0]
            first_segment_name = None

            if isinstance(first_segment, NameSpecifier):
                first_segment_name = first_segment.name
            elif isinstance(first_segment, FundamentalSpecifier):
                first_segment_name = first_segment.name

            if match_types is None or first_segment_name in match_types:
                return first_segment_name

    return None


# Returns type name of pointer-to-a-pointer (without **) if type_ is a
# pointer-to-a-pointer; otherwise will return None.
# Will filter on types listed in match_types such that only pointers-to-pointers with
# types in match_types will return the type name. All others will return None.
def is_pointer_to_pointer(
    type_: DecoratedType, match_types: List[str] = None
) -> Union[str, None]:
    if isinstance(type_, Pointer):
        if isinstance(type_.ptr_to, Pointer):
            return is_pointer(type_.ptr_to, match_types)

    return None


# Returns "char" if type_ is a "char *".  Otherwise will return None.
def is_char_pointer(type_: DecoratedType):
    return is_pointer(type_, ["char"])


# Returns "char" if type_ is a "char **".  Otherwise will return None.
def is_string_array(type_: DecoratedType):
    return is_pointer_to_pointer(type_, ["char"])


# Returns type name if type_ is a simple value type (not a pointer); otherwise None.
# Will filter on types listed in match_types such that only types with the names
# in match_types will return the type name. All others will return None.
#
# Note: cxxheaderparser does not substitude typedefs, so if the class contains
# a typedef'd parameter it will always appear as a value, even if the typdef
# is a function.  Checking for typedef'd functions should be done before
# calling this function to rule that out.
def is_value(
    type_: DecoratedType, match_types: List[str] = None
) -> Union[str, None]:
    if isinstance(type_, Type):
        first_segment = type_.typename.segments[0]
        first_segment_name = None

        if isinstance(first_segment, NameSpecifier):
            first_segment_name = first_segment.name
        elif isinstance(first_segment, FundamentalSpecifier):
            first_segment_name = first_segment.name

        if match_types is None or first_segment_name in match_types:
            return first_segment_name

    return None


# Returns "void" if type_ is a "void" type (like a function return); otherwise None.
def is_void(type_: DecoratedType):
    return is_value(type_, "void")


# Returns "AspnTypeTimestamp" if type_ is a "AspnTypeTimestamp"; otherwise None.
def is_aspn_time(type_: DecoratedType):
    out = is_value(type_, "AspnTypeTimestamp")
    if out is None:
        out = is_value(type_, "Aspn23TypeTimestamp")
    return out


# Returns function arguments and return type if type_ is a function pointer;
# otherwise None.
def is_function_pointer(type_: DecoratedType):
    if isinstance(type_, Pointer):
        if isinstance(type_.ptr_to, FunctionType):
            params = type_.ptr_to.parameters
            return_t: DecoratedType = type_.ptr_to.return_type
            return params, return_t

    return None


# Returns function arguments and return type if type_ is a function pointer
# with "class_name* self" (or "void* self") as the first argument;
# otherwise None.
def is_function_pointer_with_self(type_: DecoratedType, class_name: str):
    if not (func_type := is_function_pointer(type_)):
        return None
    params = func_type[0]
    if len(params) == 0 or params[0].name != "self":
        return None

    if first_parameter_type_name := is_pointer(params[0].type):
        if (first_parameter_type_name == class_name) or (
            first_parameter_type_name == "void"
        ):
            return func_type

    return None


# Returns function arguments and return type if type_ is a typdef to a
# function pointer with "class_name* self" (or "void* self") as the first
# argument; otherwise None.
def is_function_typedef_with_self(
    type_: DecoratedType, class_name: str, known_typedefs: Dict[str, Typedef]
):
    if isinstance(type_, Type):
        type_name = type_.typename.segments[0].name
        if type_name in known_typedefs:
            typedef_type = known_typedefs[type_name].type
            return is_function_pointer_with_self(typedef_type, class_name)

    return None


# Returns array length `N` if type_ matches "double foo[N]" ; otherwise None
def is_double_array(type_: DecoratedType):
    if isinstance(type_, Array):
        if is_value(type_.array_of, ["double"]):
            return type_.size.tokens[0].value

    return None


# Returns array length `N` if type_ matches "float foo[N]"; otherwise None
def is_float_array(type_: DecoratedType):
    if isinstance(type_, Array):
        if is_value(type_.array_of, ["float"]):
            return type_.size.tokens[0].value

    return None


# Returns type and array length `N` if type_ matches "<int> foo[N]" for
# various types of <int>; otherwise None
def is_int_array(type_: DecoratedType):
    if isinstance(type_, Array):
        if type_name := is_value(
            type_.array_of, ["int8_t", "int16_t", "int32_t", "int64_t"]
        ):
            return type_name, type_.size.tokens[0].value

    return None


# Returns array length `N` if type_ matches "double* foo[N]"; otherwise None
def is_pointer_to_double_array(type_: DecoratedType):
    if isinstance(type_, Pointer):
        if is_double_array(type_.ptr_to):
            return type_.ptr_to.size.tokens[0].value

    return None
