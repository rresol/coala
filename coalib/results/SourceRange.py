from coalib.misc.Decorators import enforce_signature
from coalib.results.SourcePosition import SourcePosition
from coalib.results.TextRange import TextRange


class SourceRange(TextRange):

    @enforce_signature
    def __init__(self,
                 start: SourcePosition,
                 end: (SourcePosition, None)=None):
        """
        Creates a new SourceRange.

        :param start:       A SourcePosition indicating the start of the range.
        :param end:         A SourcePosition indicating the end of the range.
                            If `None` is given, the start object will be used
                            here. end must be in the same file and be greater
                            than start as negative ranges are not allowed.
        :raises TypeError:  Raised when
                            - start is no SourcePosition or None.
                            - end is no SourcePosition.
        :raises ValueError: Raised when file of start and end mismatch.
        """
        TextRange.__init__(self, start, end)

        if self.start.file != self.end.file:
            raise ValueError("File of start and end position do not match.")

    @classmethod
    def from_values(cls,
                    file,
                    start_line=None,
                    start_column=None,
                    end_line=None,
                    end_column=None):
        start = SourcePosition(file, start_line, start_column)
        if not end_line:
            end = None
        else:
            end = SourcePosition(file, end_line, end_column)

        return cls(start, end)

    @classmethod
    def from_clang_range(cls, range):
        """
        Creates a SourceRange from a clang SourceRange object.

        :param range: A cindex.SourceRange object.
        """
        return cls.from_values(range.start.file.name,
                               range.start.line,
                               range.start.column,
                               range.end.line,
                               range.end.column)

    @property
    def file(self):
        return self.start.file

    def expand(self, file_contents):
        """
        Passes a new SourceRange that covers the same area of a file as this
        one would. All values of None get replaced with absolute values.

        values of None will be interpreted as follows:
        self.start.line is None:   -> 1
        self.start.column is None: -> 1
        self.end.line is None:     -> last line of file
        self.end.column is None:   -> last column of self.end.line

        :param file_contents: File contents of the applicable file
        :return:              TextRange with absolute values
        """
        end_line = self.end.line or len(file_contents)

        return self.__class__.from_values(
            self.file,
            self.start.line or 1,
            self.start.column or 1,
            end_line,
            self.end.column or len(file_contents[end_line - 1]))
