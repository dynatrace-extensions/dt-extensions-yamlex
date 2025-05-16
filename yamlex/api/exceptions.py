class YamlexError(Exception):
    """Base class for all Yamlex errors."""
    code = 10


class YamlexWarning(UserWarning):
    """Base class for all Yamlex warnings."""
    pass


class InvalidItemWithinArrayDirectoryError(YamlexError):
    code = 11


class UnintendedIndexFileWarning(UserWarning):
    code = 12


class NonTextFileError(YamlexError):
    code = 13


class FailedToParseYamlError(YamlexError):
    code = 14


class WrongExtensionStructureError(YamlexError):
    code = 15


class EmptyAssembledExtensionError(YamlexError):
    code = 16


class OverwritingManuallyCreatedFileError(YamlexError):
    code = 17


class IndexFileIsArray(YamlexError):
    code = 18


class InvalidSourcePath(YamlexError):
    code = 19


class InvalidTargetPath(YamlexError):
    code = 20
