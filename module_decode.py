
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
                print("SubCommand -> On")
                print("Parameter -> " + self.array[2] + " " + self.array[3] + " " + self.array[4])
            elif self.array[1] == "off":
                print("SubCommand -> Off")
                print("Parameter -> " + self.array[2] + " " + self.array[3] + " " + self.array[4])
            elif self.array[1] == "def":
                print("SubCommand -> Default")
                print("Parameter -> " + self.array[2] + " " + self.array[3] + " " + self.array[4])
            elif self.array[1] == "bri":
                print("SubCommand -> Brightness")
                print("Parameter -> " + self.array[2] + " " + self.array[3] + " " + self.array[4])
            else:
                print("No Command")
        
        if self.array[0] == "do":
            print("Command -> do")
            if self.array[1] == "led":
                print("SubCommand -> led")
                print("Parameter -> " + self.array[2] + " " + self.array[3] + " " + self.array[4])
            elif self.array[1] == "all":
                print("SubCommand -> all")
                if self.array[2] == "on":
                    print("Parameter -> on")
                elif self.array[2] == "def":
                    print("Parameter -> def")
                elif self.array[2] == "off":
                    print("Parameter -> off")
                else:
                    print("No Command")
            else:
                print("No Command")
        else:
            print("No Command")


def main():

    test_string = "do,all,on"

    cmd_dec = Decoder()

    cmd_dec.send_data(test_string)





if __name__ == "__main__":
    main()
