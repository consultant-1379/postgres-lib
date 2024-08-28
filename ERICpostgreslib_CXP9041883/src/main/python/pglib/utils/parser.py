from pyu.tools.parsers import TableParser


class BorderedTitleTableParser(TableParser):
    """ Parses a table in the following format:
    + Cluster: postgres (6992537990930645040) ----+---------+----+-----------+
    | Member     | Host            | Role         | State   | TL | Lag in MB |
    +------------+-----------------+--------------+---------+----+-----------+
    | postgres-0 | 192.168.159.166 | Sync Standby | running |  7 |         0 |
    | postgres-1 | 192.168.253.231 | Leader       | running |  7 |           |
    +------------+-----------------+--------------+---------+----+-----------+
    footer 1
    footer 2
    """

    header_index = 1
    body_starts = 3
    split_char = '|'
    vertical_border = split_char
    border_type = '+'

    def validate(self):
        """ Make sure that all rows of the table has the same size as the
        header. It also checks the format of the bordered table.
        The attribute "self._body_ends" is also set to make the parser able
        to identify the body of the table properly.
        It throws AssertionError in case the table is not in the expected
        format.
        :exception: AssertionError
        :return:
        """
        lines = self.non_empty_lines
        assert len(lines), "Cannot parse empty lines"
        assert lines[0].startswith(self.border_type), "Expected start with " \
                                                      "%s, but got: %s. " \
                                                      "Output: %s" % \
                                                      (self.border_type,
                                                       lines[0], self.output)
        if self.vertical_border:
            assert lines[1].startswith(self.vertical_border), \
                "Expected start with %s, but got: %s. Output: %s" % \
                (self.split_char, lines[1], self.output)
        assert lines[2].startswith(self.border_type), "Expected start with " \
                                                      "%s, but got: %s. " \
                                                      "Output: %s" \
                                                      % (self.border_type,
                                                         lines[2], self.output)
        count = 2
        for line in lines[3:]:
            count += 1
            if line.startswith(self.border_type):
                break
        else:
            assert False, "Expected end of the table with %s, but got " \
                          "nothing. Output: %s" % (self.border_type,
                                                   self.output)
        self._body_ends = count
