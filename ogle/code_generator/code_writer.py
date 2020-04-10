class CodeWriter(object):
    tag_width = 15
    operation_width = 7

    def __init__(self, output_file):
        self.output_file = output_file

    def write_operation(self, operation, *operands, tag=None):
        to_write = ''
        if tag:
            to_write += str(tag).ljust(CodeWriter.tag_width)
        to_write += str(operation).ljust(CodeWriter.operation_width)
        to_write += ', '.join(operands)
        self.output_file.write(f'{to_write}\n')

    def load_word(self, ri, k, rj):
        to_write = ''.ljust(CodeWriter.tag_width)
        to_write += 'lw'.ljust(CodeWriter.operation_width)
        to_write += f'{ri}, {k}({rj})'
        self.output_file.write(f'{to_write}\n')

    def store_word(self, k, rj, ri):
        to_write = ''.ljust(CodeWriter.tag_width)
        to_write += 'sw'.ljust(CodeWriter.operation_width)
        to_write += f'{k}({rj}), {ri}'
        self.output_file.write(f'{to_write}\n')
