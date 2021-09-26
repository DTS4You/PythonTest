
class Decoder:

    def __init__(self):
        
        self.data = ""
        self.array = []

    def send_data(self, data):
        self.data = data
        self.data_split()

    def data_split(self):
        self.array = self.data.split(",")
        self.cmd_decode()

    def get_data(self):
        return self.data

    def get_array(self):
        return self.array

    def cmd_decode(self):
        if self.array[0] == "set":
            print("Command -> Set")
            if self.array[1] == "on":
                print("Parameter -> On")
            if self.array[1] == "off":
                print("Parameter -> Off")
            if self.array[1] == "def":
                print("Parameter -> Default")
            if self.array[1] == "bri":
                print("Parameter -> Brightness")
        if self.array[0] == "do":
            print("Command -> do")
            if self.array[1] == "led":
                print("Parameter -> led")
                print(self.array[2] + " " + self.array[3] + " " + self.array[4])


def main():

    test_string = "do,led,10,20,30"

    cmd_dec = Decoder()

    cmd_dec.send_data(test_string)





if __name__ == "__main__":
    main()
