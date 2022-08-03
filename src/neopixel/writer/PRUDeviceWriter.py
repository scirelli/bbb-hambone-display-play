from .FileWriter import FileWriter


class PRUDeviceWriter(FileWriter):
    def __init__(
        self, dev_file_path: str = "/dev/rpmsg_pru30"
    ):  # pylint: disable=useless-super-delegation
        super().__init__(dev_file_path)
