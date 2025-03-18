from os import makedirs, remove, path
from os.path import join
from typing import List, Union

from firehose.backends import Backend
from firehose.backends.aspn.utils import (
    ASPN_PREFIX,
    INDENT,
    format_and_write_py_file,
    is_length_field,
    pascal_to_snake,
    snake_to_pascal,
)

ASPN_MODULE = ASPN_PREFIX.lower()


class Struct:
    def __init__(self, pascal_struct_name: str, to_lcm: bool = True):
        self.struct_name = pascal_struct_name
        # this field allows us to define whether we are going to or from lcm.
        # defaults to true
        self.to_lcm = to_lcm
        self.assignments: list[str] = []
        self.imports_aspn = []
        self.to_lcm_template = f"""
def {pascal_to_snake(pascal_struct_name)}_to_lcm(old: {pascal_struct_name}) -> Lcm{pascal_struct_name}:
{INDENT}msg = Lcm{pascal_struct_name}()
{{assignments}}

{INDENT}return msg
"""
        self.from_lcm_template = f"""
def lcm_to_{pascal_to_snake(pascal_struct_name)}(old: Lcm{pascal_struct_name}) -> {pascal_struct_name}:
{INDENT}return {pascal_struct_name}({{fields}})
"""


PRIMITIVES = ["float", "int", "bool", "str"]


class AspnYamlToLCMTranslations(Backend):
    current_struct: Struct | None = None
    structs: List[Struct] = []
    output_folder = None

    def set_output_root_folder(self, output_root_folder: str):
        self.output_folder = output_root_folder
        makedirs(self.output_folder, exist_ok=True)
        if self.output_folder is not None:
            filename = f'{self.output_folder}/lcm_translations.py'
            if path.exists(filename):
                remove(filename)

    def begin_struct(self, snake_case_struct_name, to_lcm: bool = False):
        if self.current_struct is not None:
            self.structs += [self.current_struct]
        self.current_struct = Struct(
            f"{snake_to_pascal(snake_case_struct_name)}", to_lcm
        )

    def _generate_lcm_function(self, struct: Struct):
        if struct.to_lcm:
            assignments = [f"{INDENT}msg.{it}" for it in struct.assignments]
            function = struct.to_lcm_template.format(
                assignments='\n'.join(assignments)
            )
        else:
            assignments = [
                f"{INDENT}{INDENT}{it}" for it in struct.assignments
            ]
            function = struct.from_lcm_template.format(
                fields=', '.join(struct.assignments)
            )

        return function

    def generate(self):
        self.structs += [self.current_struct]

        all_aspn_imports = []
        for struct in self.structs:
            all_aspn_imports += struct.imports_aspn

        all_aspn_imports += [
            f"from aspn23.{pascal_to_snake(it.struct_name)} import {it.struct_name}"
            for it in self.structs
        ]

        imports_lcm = [
            f"from .{pascal_to_snake(it.struct_name)} import {pascal_to_snake(it.struct_name)} as Lcm{it.struct_name}"
            for it in self.structs
        ]
        imports = all_aspn_imports + imports_lcm
        imports = "\n".join(imports)

        functions = "\n".join(
            [self._generate_lcm_function(it) for it in self.structs]
        )

        template = """
import numpy as np
{imports}

{functions}
        """

        output_file_content = template.format(
            imports=imports, functions=functions
        )

        output_translations = join(self.output_folder, "lcm_translations.py")
        format_and_write_py_file(output_file_content, output_translations)

        exports = '''\
# Follow Python export conventions:
# https://typing.readthedocs.io/en/latest/spec/distributing.html#import-conventions
from .lcm_translations import (
        '''
        function_base_names = [
            pascal_to_snake(struct.struct_name) for struct in self.structs
        ]
        for name in function_base_names:
            exports += f'\nlcm_to_{name} as lcm_to_{name}\n{name}_to_lcm as {name}_to_lcm'
        exports += '\n)'
        output_init = join(self.output_folder, '__init__.py')
        format_and_write_py_file(exports, output_init)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # Backend Methods # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def process_func_ptr_field_with_self(
        self, field_name: str, params, return_t, doc_string: str, nullable=None
    ):
        raise NotImplementedError

    def process_data_pointer_field(
        self,
        field_name: str,
        type_name: str,
        data_len: Union[str, int],
        doc_string: str,
        deref="",
        nullable=None,
    ):
        if self.current_struct is None:
            return

        # bounded v unbounded ndarrays.
        if isinstance(data_len, int):
            self.current_struct.assignments.append(
                f"{field_name} = old.{field_name}"
            )

            # covariance has a custom extra field that we need to add for counting.
            if field_name == "covariance":
                self.current_struct.assignments.append(
                    f"num_meas = len(old.{field_name})"
                )
            return
        elif type_name in ["float", "int"]:
            self.current_struct.assignments.append(
                f"{field_name} = old.{field_name}"
            )

            # these fields have a custom extra field that needs to be added for
            # counting them.
            if field_name == "image_data":
                self.current_struct.assignments.append(
                    f"{field_name}_length = len(old.{field_name})"
                )
            elif field_name == "descriptor":
                self.current_struct.assignments.append(
                    f"{field_name}_size = len(old.{field_name})"
                )
            elif field_name in ["error_model_params"]:
                if self.current_struct.to_lcm:
                    self.current_struct.assignments.append(
                        f"num_{field_name} = len(old.{field_name})"
                    )
            elif field_name in ["integrity", "model_coefficients"]:
                self.current_struct.assignments.append(
                    f"num_{field_name} = len(old.{field_name})"
                )
            elif field_name == "clock_id":
                self.current_struct.assignments.append(
                    f"num_obs = len(old.{field_name})"
                )
            elif field_name == "b":
                self.current_struct.assignments.append(
                    f"num_meas = len(old.{field_name})"
                )
            elif field_name == "data_vector":
                self.current_struct.assignments.append(
                    f"num_bytes = len(old.{field_name})"
                )
            return

        # We use ndarrays for primitives, and List for nonprimitives.
        # At this point we know we must be a list.
        self.current_struct.assignments.append(
            f"{field_name} = [{pascal_to_snake(type_name)}_to_lcm(x) for x in old.{field_name}]"
        )

    def process_matrix_field(
        self,
        field_name: str,
        type_name: str,
        x: int | str,
        y: int | str,
        doc_string: str,
        nullable=None,
    ):
        if self.current_struct is None:
            return

        self.current_struct.assignments.append(
            f"{field_name} = old.{field_name}"
        )

    def process_outer_managed_pointer_field(
        self,
        field_name: str,
        field_type_name: str,
        doc_string: str,
        nullable: bool = False,
    ):
        raise NotImplementedError

    def process_outer_managed_pointer_array_field(
        self,
        field_name: str,
        field_type_name: str,
        data_len: Union[str, int],
        doc_string: str,
        deref="",
        nullable=None,
    ):
        raise NotImplementedError

    def process_string_field(
        self, field_name: str, doc_string: str, nullable=None
    ):
        self.process_simple_field(
            field_name, "str", doc_string, nullable=nullable
        )

    def process_string_array_field(
        self, field_name: str, doc_string: str, nullable=None
    ):
        raise NotImplementedError

    def process_simple_field(
        self,
        field_name: str,
        field_type_name: str,
        doc_string: str,
        nullable=None,
    ):
        if self.current_struct is None:
            return
        if is_length_field(field_name):
            return

        # If it is not a primitive, we need to call the generation for that class.
        # We can use `in` here because we rooted out all the other ones.
        if not any(field_type_name in it for it in PRIMITIVES):
            self.current_struct.assignments.append(
                f"{field_name} = {pascal_to_snake(field_type_name)}_to_lcm(old.{field_name})"
            )
            return

        self.current_struct.assignments.append(
            f"{field_name} = old.{field_name}"
        )

    def process_class_docstring(self, doc_string: str, nullable=None):
        pass

    def process_inheritance_field(
        self,
        field_name: str,
        field_type_name: str,
        doc_string: str,
        nullable=None,
    ):
        raise NotImplementedError

    def process_enum(
        self,
        field_name: str,
        field_type_name: str,
        enum_values: List[str],
        doc_string: str,
        enum_values_doc_strs: List[str],
    ):
        if self.current_struct is None:
            return

        if self.current_struct.to_lcm:
            self.current_struct.assignments.append(
                f"{field_name} = old.{field_name}.value"
            )
        else:
            struct_name = pascal_to_snake(self.current_struct.struct_name)
            field_type_name = f"{self.current_struct.struct_name}{snake_to_pascal(field_type_name)}"
            import_string = (
                f"from aspn23.{struct_name} import {field_type_name}"
            )
            if import_string not in self.current_struct.imports_aspn:
                self.current_struct.imports_aspn.append(import_string)
            self.current_struct.assignments.append(
                f"{field_name} = {field_type_name}(old.{field_name})"
            )
