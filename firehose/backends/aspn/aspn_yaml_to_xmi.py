from typing import List, Union
from typing import Any
from firehose.backends import Backend


class AspnYamlToXMI(Backend):
    def __init__(self, struct_name):
        self.struct_name: str = struct_name

    def generate(self) -> str:
        raise NotImplementedError

    def process_func_ptr_field_with_self(
        self,
        field_name: str,
        params,
        return_t,
        doc_string: str,
        nullable: bool = False,
    ):
        pass

    def process_data_pointer_field(
        self,
        field_name: str,
        type_name: str,
        data_len: Union[str, int],
        doc_string: str,
        deref="",
        nullable: bool = False,
    ):
        raise NotImplementedError

    def process_matrix_field(
        self,
        field_name: str,
        type_name: str,
        x: Union[str, int],
        y: Union[str, int],
        doc_string: str,
        nullable: bool = False,
    ):
        raise NotImplementedError

    def process_outer_managed_pointer_field(
        self,
        field_name: str,
        field_type_name: str,
        doc_string: str,
        nullable: bool = False,
    ):
        pass

    def process_outer_managed_pointer_array_field(
        self,
        field_name: str,
        field_type_name: str,
        data_len: Union[str, int],
        doc_string: str,
        deref="",
        nullable: bool = False,
    ):
        pass

    def process_string_field(
        self, field_name: str, doc_string: str, nullable: bool = False
    ):
        raise NotImplementedError

    def process_string_array_field(
        self, field_name: str, doc_string: str, nullable: bool = False
    ):
        pass

    def process_simple_field(
        self,
        field_name: str,
        field_type_name: str,
        doc_string: str,
        nullable: bool = False,
    ):
        raise NotImplementedError

    def process_inheritance_field(
        self,
        field_name: str,
        field_type_name: str,
        doc_string: str,
        nullable: bool = False,
    ):
        pass

    def process_class_docstring(self, doc_string: str, nullable: bool = False):
        raise NotImplementedError
