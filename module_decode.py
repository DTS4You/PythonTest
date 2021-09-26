
class Decoder:

    def __init__(self):
        
        self.data = ""

    def send_data(self, data):
        self.data = data

    def get_result(self):
        return self.data


def main():

    test_string = "set,0,0,1"

    dec_cmd = Decoder()

    dec_cmd.send_data(test_string)

    print(dec_cmd.get_result())


if __name__ == "__main__":
    main()
