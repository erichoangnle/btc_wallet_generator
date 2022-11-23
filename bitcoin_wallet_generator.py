import datetime, os, binascii, hashlib, base58, ecdsa, sys, qrcode
from tabulate import tabulate

def privateKey(): # Generates random 256 bit private key in hex format
    return binascii.hexlify(os.urandom(32)).decode('utf-8')

def publicKey(privatekey): # Private Key -> Public Key
    privatekey = binascii.unhexlify(privatekey)
    s = ecdsa.SigningKey.from_string(privatekey, curve = ecdsa.SECP256k1)
    return '04' + binascii.hexlify(s.verifying_key.to_string()).decode('utf-8')

def address(publickey): # Public Key -> Wallet Address
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    c = '0'; byte = '00'; zero = 0
    var = hashlib.new('ripemd160')
    var.update(hashlib.sha256(binascii.unhexlify(publickey.encode())).digest())
    a = (byte + var.hexdigest())
    doublehash = hashlib.sha256(hashlib.sha256(binascii.unhexlify(a.encode())).digest()).hexdigest()
    address = a + doublehash[0:8]
    for char in address:
        if (char != c):
            break
        zero += 1
    zero = zero // 2
    n = int(address, 16)
    output = []
    while (n > 0):
        n, remainder = divmod (n, 58)
        output.append(alphabet[remainder])
    count = 0
    while (count < zero):
        output.append(alphabet[0])
        count += 1
    return ''.join(output[::-1])

def toWIF(privatekey): # Hex Private Key -> WIF format
    var80 = "80" + str(privatekey) 
    var = hashlib.sha256(binascii.unhexlify(hashlib.sha256(binascii.unhexlify(var80)).hexdigest())).hexdigest()
    return base58.b58encode(binascii.unhexlify(str(var80) + str(var[0:8])))

def main():

    while(True):

        try:

            # Prompt user for input
            wallet_name = input('Enter wallet name: ')
            print("")

            # Generate key pair
            priv = privateKey()
            pub = publicKey(priv)
            add = address(pub)
            wif = toWIF(priv).decode()

            # get timestamp
            time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Create table for output
            header = ["Name", wallet_name]
            table = [["Address", add], ["Key", wif], ["Created on", time]]

            # Print table
            output = tabulate(table, header, tablefmt = "grid")
            print(output)

            # Write wallet to file
            f = open(f"wallets/{wallet_name}.txt",'a')
            f.write(output)
            f.write("\n\n")
            f.close()

            # Generate Address QR code
            a = qrcode.make(add)
            a.save(f"wallets/{wallet_name}_address.png")

            # Generate Key QR code
            k = qrcode.make(wif)
            k.save(f"wallets/{wallet_name}_key.png")

            # Wallet created
            print('\n')
            print('Your wallet has been created.')
            question = input("Do you want to create another wallet? (Y/N): ")

            if question == "y" or question == "Y":
                print("")
                pass
            else:
                raise ValueError

        except ValueError:
            sys.exit("Good luck!")


if __name__ == '__main__':
	main()
