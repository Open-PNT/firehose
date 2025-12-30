from abc import ABC, abstractmethod
from typing import List, Union
from cxxheaderparser.types import Parameter, DecoratedType


class Backend(ABC):
    @abstractmethod
    def set_output_root_folder(self, output_root_folder: str):
        """
        output_root_folder contains the path to the folder that generated files
        should be written to upon calls to `generate()`. It is up to the
        Backend to determine the folder structure for the output files.
        """
        pass

    @abstractmethod
    def begin_struct(self, struct_name: str):
        """
        This should be called before any process_* functions are called.
        When this is called, any information stored from any process_* or
        generate() calls before should be reset for new input for a different
        type.
        """
        pass

    @abstractmethod
    def process_func_ptr_field_with_self(
        self,
        field_name: str,
        params: List[Parameter],
        return_t: DecoratedType,
        doc_string: str,
        nullable: bool = False,
    ):
        pass

    @abstractmethod
    def process_data_pointer_field(
        self,
        field_name: str,
        type_name: str,
        data_len: Union[str, int],
        doc_string: str,
        deref="",
        nullable: bool = False,
    ):
        pass

    @abstractmethod
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

    @abstractmethod
    def process_outer_managed_pointer_field(
        self,
        field_name: str,
        field_type_name: str,
        doc_string: str,
        nullable: bool = False,
    ):
        pass

    @abstractmethod
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

    @abstractmethod
    def process_string_field(
        self, field_name: str, doc_string: str, nullable: bool = False
    ):
        pass

    @abstractmethod
    def process_string_array_field(
        self, field_name: str, doc_string: str, nullable: bool = False
    ):
        pass

    @abstractmethod
    def process_simple_field(
        self,
        field_name: str,
        field_type_name: str,
        doc_string: str,
        nullable: bool = False,
    ):
        pass

    @abstractmethod
    def process_inheritance_field(
        self,
        field_name: str,
        field_type_name: str,
        doc_string: str,
        nullable: bool = False,
    ):
        pass

    @abstractmethod
    def process_class_docstring(self, doc_string: str, nullable: bool = False):
        pass

    @abstractmethod
    def generate(self):
        """
        Generate output for a single struct based on the process_* functions
        that have been called since the last time begin_struct() was
        called. The backend will determine where to write the file based
        on set_output_root_folder().
        """
        pass
