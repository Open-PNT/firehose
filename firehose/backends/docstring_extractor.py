from typing import List, Union
from cxxheaderparser.types import Parameter, DecoratedType

from .backend import Backend


class DocstringExtractor(Backend):
    def __init__(self, class_name: str):
        self.class_name = class_name
        self.out_buf: List[str] = []

    def set_output_root_folder(self, output_root_folder: str):
        pass

    def begin_struct(self, struct_name: str):
        pass

    def _process_docstring(self, field_name: str, doc_string: str):
        self.out_buf += [
            f"""const char *_docstring_class_{self.class_name}_{field_name} ="""
        ]

        if doc_string:
            self.out_buf += ["""R"(   """ + doc_string + """)";"""]
        else:
            self.out_buf += ["""R"(<Missing C Docstring>)";"""]

    def generate(self) -> str:
        return "\n".join(self.out_buf)

    def process_func_ptr_field_with_self(
        self,
        field_name: str,
        params: List[Parameter],
        return_t: DecoratedType,
        doc_string: str,
        nullable: bool = False,
    ):
        self._process_docstring(field_name, doc_string)

    def process_data_pointer_field(
        self,
        field_name: str,
        type_name: str,
        data_len: Union[str, int],
        doc_string: str,
        deref="",
        nullable: bool = False,
    ):
        self._process_docstring(field_name, doc_string)

    def process_matrix_field(
        self,
        field_name: str,
        type_name: str,
        x: Union[str, int],
        y: Union[str, int],
        doc_string: str,
        nullable: bool = False,
    ):
        pass

    def process_outer_managed_pointer_field(
        self,
        field_name: str,
        type_name: str,
        doc_string: str,
        nullable: bool = False,
    ):
        self._process_docstring(field_name, doc_string)

    def process_outer_managed_pointer_array_field(
        self,
        field_name: str,
        field_type_name: str,
        data_len: Union[str, int],
        doc_string: str,
        deref="",
        nullable: bool = False,
    ):
        self._process_docstring(field_name, doc_string)

    def process_string_field(
        self, field_name: str, doc_string: str, nullable: bool = False
    ):
        self._process_docstring(field_name, doc_string)

    def process_string_array_field(
        self, field_name: str, doc_string: str, nullable: bool = False
    ):
        self._process_docstring(field_name, doc_string)

    def process_simple_field(
        self,
        field_name: str,
        field_type_name: str,
        doc_string: str,
        nullable: bool = False,
    ):
        self._process_docstring(field_name, doc_string)

    def process_inheritance_field(
        self,
        field_name: str,
        field_type_name: str,
        doc_string: str,
        nullable: bool = False,
    ):
        self._process_docstring(field_name, doc_string)

    def process_class_docstring(self, doc_string: str, nullable: bool = False):
        self._process_docstring("main_class", doc_string)
