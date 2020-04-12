class CodeWriter(object):
    tag_width = 20
    operation_width = 7

    def __init__(self, output_file):
        self.output_file = output_file

    def operation(self, operation, *operands, tag=None):
        to_write = str(tag) if tag else ''
        to_write = to_write.ljust(CodeWriter.tag_width)
        to_write += str(operation).ljust(CodeWriter.operation_width)
        to_write += ', '.join([str(op) for op in operands])
        self.output_file.write(f'{to_write}\n')

    def load_word(self, ri, k, rj):
        to_write = ''.ljust(CodeWriter.tag_width)
        to_write += 'lw'.ljust(CodeWriter.operation_width)
        to_write += f'{ri}, {str(k)}({rj})'
        self.output_file.write(f'{to_write}\n')

    def store_word(self, k, rj, ri):
        to_write = ''.ljust(CodeWriter.tag_width)
        to_write += 'sw'.ljust(CodeWriter.operation_width)
        to_write += f'{str(k)}({rj}), {ri}'
        self.output_file.write(f'{to_write}\n')

    def empty_line(self, no_of_empty_lines=1):
        for i in range(no_of_empty_lines):
            self.output_file.write('\n')

    def comment(self, comment_string):
        self.output_file.write(f'{"".ljust(CodeWriter.tag_width)}% {comment_string}\n')
