import ast
import importlib.util
import os
import sys
from typing import Dict, List, Optional

from boa3 import constants
from boa3.analyser.astanalyser import IAstAnalyser
from boa3.model import imports
from boa3.model.symbol import ISymbol
from boa3.model.type.type import Type


class ImportAnalyser(IAstAnalyser):

    def __init__(self, import_target: str, root_folder: str,
                 importer_file: Optional[str] = None,
                 import_stack: List[str] = None,
                 already_imported_modules: dict = None,
                 log: bool = False):

        self.can_be_imported: bool = False
        self.is_builtin_import: bool = False
        self.recursive_import: bool = False
        self._import_identifier: str = import_target

        from boa3.analyser.analyser import Analyser
        self._imported_files: Dict[str, Analyser] = (already_imported_modules
                                                     if isinstance(already_imported_modules, dict)
                                                     else {})
        self._import_stack: List[str] = import_stack if isinstance(import_stack, list) else []
        self.analyser: Analyser = None  # set if the import is successful

        if isinstance(root_folder, str):
            if os.path.isfile(root_folder):
                root = os.path.dirname(root_folder)
            elif os.path.isdir(root_folder):
                root = root_folder
            else:
                root = os.path.dirname(importer_file)
        else:
            root = os.path.dirname(importer_file)

        super().__init__(ast.Module(body=[]), root_folder=root, log=log)

        sys.path.append(self.root_folder)
        try:
            import_spec = importlib.util.find_spec(import_target)
            module_origin: str = import_spec.origin
        except BaseException as e:
            return
        finally:
            sys.path.remove(self.root_folder)

        path: List[str] = module_origin.split(os.sep)
        self.filename = path[-1]
        self._submodule_search_locations = import_spec.submodule_search_locations
        self._importer_file = importer_file
        self.path: str = module_origin.replace(os.sep, constants.PATH_SEPARATOR)

        self._find_package(module_origin, importer_file)

    @property
    def tree(self) -> ast.AST:
        return self._tree

    def export_symbols(self, identifiers: List[str] = None) -> Dict[str, ISymbol]:
        """
        Gets a dictionary that maps each exported symbol with its identifier

        :param identifiers: list of identifiers of the imported symbols
        :return:
        """
        if identifiers is None:
            identifiers = list([name for name, symbol in self.symbols.items() if symbol is not None])
        if not self.can_be_imported or not isinstance(identifiers, (list, str)):
            return {}

        if isinstance(identifiers, str):
            identifiers = [identifiers]

        if constants.IMPORT_WILDCARD in identifiers:
            symbols = self.symbols.copy()
        else:
            symbols = {symbol_id: symbol for symbol_id, symbol in self.symbols.items()
                       if symbol_id in identifiers and symbol is not None}
        return symbols

    def _find_package(self, module_origin: str, origin_file: Optional[str] = None):
        path: List[str] = module_origin.split(os.sep)

        package = imports.builtin.get_package(self._import_identifier)
        if hasattr(package, 'symbols'):
            if hasattr(package, 'inner_packages'):
                # when have symbol and packages with the same id, prioritize symbol
                self.symbols: Dict[str, ISymbol] = package.inner_packages
                self.symbols.update(package.symbols)
            else:
                self.symbols = package.symbols

            self.can_be_imported = True
            self.is_builtin_import = True
            return

        if not ('boa3' in path and constants.PATH_SEPARATOR.join(path[path.index('boa3'):]).startswith('boa3/builtin')):
            # doesn't analyse boa3.builtin packages that aren't included in the imports.builtin as an user module
            # TODO: refactor when importing from user modules is accepted
            import re

            inside_python_folder = any(re.search(r'python(\d\.?)*', folder.lower()) for folder in path)
            updated_tree = None

            if not (inside_python_folder and 'lib' in path):
                # check circular imports to avoid recursions inside the compiler
                if self.path in self._import_stack:
                    self.recursive_import = True
                    return

                # TODO: only user modules and typing lib imports are implemented
                try:
                    if self.path in self._imported_files:
                        analyser = self._imported_files[self.path]
                    else:
                        from boa3.analyser.analyser import Analyser
                        origin = origin_file.replace(os.sep, constants.PATH_SEPARATOR)
                        files = self._import_stack
                        files.append(origin)
                        analyser = Analyser.analyse(module_origin, root=self.root_folder,
                                                    imported_files=self._imported_files,
                                                    import_stack=files, log=self._log)

                        self._include_inner_packages(analyser)

                    # include only imported symbols
                    if analyser.is_analysed:
                        for symbol_id, symbol in analyser.symbol_table.items():
                            if symbol_id not in Type.all_types():
                                symbol.defined_by_entry = False
                                self.symbols[symbol_id] = symbol

                    self.errors.extend(analyser.errors)
                    self.warnings.extend(analyser.warnings)

                    updated_tree = analyser.ast_tree
                    self.analyser = analyser
                    self.can_be_imported = analyser.is_analysed
                except FileNotFoundError:
                    self.can_be_imported = False

                if updated_tree is not None:
                    self._tree = updated_tree

    def _include_inner_packages(self, analyser):
        if self.filename != f'{constants.INIT_METHOD_ID}.py':
            return

        import pkgutil
        from boa3.model.imports.importsymbol import Import
        from boa3.model.imports.package import Package

        modules = {}
        for importer, modname, is_pkg in pkgutil.iter_modules(self._submodule_search_locations):
            mod_target = self._import_identifier + constants.ATTRIBUTE_NAME_SEPARATOR + modname
            import_analyser = ImportAnalyser(mod_target, self.root_folder,
                                             importer_file=self._importer_file,
                                             import_stack=self._import_stack,
                                             already_imported_modules=self._imported_files,
                                             log=self._log)

            imported = Package(identifier=modname,
                               other_symbols=import_analyser.symbols,
                               import_origin=Import(import_analyser.path,
                                                    import_analyser._tree,
                                                    import_analyser))
            modules[modname] = imported

        if len(modules) > 0 and hasattr(analyser, 'symbol_table') and isinstance(analyser.symbol_table, dict):
            analyser.symbol_table.update(modules)
