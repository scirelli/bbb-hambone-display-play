from .FileWriter import FileWriter


class PRUDeviceWriter(FileWriter):
    def __init__(self, dev_file_path: str = "/dev/rpmsg_pru30"):  # pylint: disable=useless-super-delegation
        super().__init__(dev_file_path)

    def write(self, b: bytearray) -> None:
        for i in range(0, len(b), 3):
            # print("%d %d %d %d\n".encode("utf-8") % (index, item.r, item.g, item.b))
            self.file.write(b"%d %d %d %d\n" % (i, b[i], b[i + 1], b[i + 2]))
        self.file.write(b"%d %d %d %d\n" % (-1, 0, 0, 0))
