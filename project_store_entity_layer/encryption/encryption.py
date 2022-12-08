import sys
import os
from cryptography.fernet import Fernet
import yaml
from dotenv import load_dotenv
from project_store_utils_layer.utils import CommonUtils
from project_store_exception_layer.exception import CustomException as EncyptException

class EncryptData:

    def __init__(self):
        try:
            self.configs = CommonUtils().read_yaml('config.yaml')

        except Exception as e:
            encrypt_exception = EncyptException(
                "Failed during loading init file in module [{0}] class [{1}] method [{2}]"
                    .format(self.__module__, EncryptData.__name__,
                            self.__init__.__name__))
            raise Exception(encrypt_exception.error_message_detail(str(e), sys)) from e


   
    def pass_generate_key(self):
        """
        Generates a key and save it into a file
        """
        try:
            key = Fernet.generate_key()
            load_dotenv()
            os.environ['DATABASE_KEY_1'] = key
            return key
        except Exception as e:
            pass_generate_key_encryption = EncyptException(
                "Failed during Generating Key in module [{0}] class [{1}] method [{2}]"
                    .format(self.__module__, EncryptData.__name__,
                            self.pass_generate_key.__name__))
            raise Exception(pass_generate_key_encryption.error_message_detail(str(e), sys))\
                                             from e


    def load_key(self):
        """
        Return secret key from environment variable:
        """
        try:
            if os.environ.get('DB_KEY') is None:
                load_dotenv()
                # environment_variable= os.getenv('.env')
                # print(environment_variable)
                # key = environment_variable['DATABASE_KEY']
                key = os.getenv('DATABASE_KEY')
            else:
                key = os.environ.get('DB_KEY')
            return key
        except Exception as e:
            load_key_encryption = EncyptException(
                "Failed during loading Key file in module [{0}] class [{1}] method [{2}]"
                    .format(self.__module__, EncryptData.__name__,
                            self.load_key.__name__))
            raise Exception(load_key_encryption.error_message_detail(str(e), sys))\
                                             from e


    def encrypt_message(self,message,key=None):
        """
        Encrypts a message
        """
        try:
            encoded_message = message.encode()
            if key is None:
                key=self.load_key()
            f = Fernet(key)
            encrypted_message = f.encrypt(encoded_message)

            return encrypted_message

        except Exception as e:
            encrypt_message_encryption = EncyptException(
                "Failed during Encrypting Message in module [{0}] class [{1}] method [{2}]"
                    .format(self.__module__, EncryptData.__name__,
                            self.encrypt_message.__name__))
            raise Exception(encrypt_message_encryption.error_message_detail(str(e), sys))\
                                             from e



    def decrypt_message(self,encrypted_message,key=None):
        """
        Decrypts an encrypted message
        """
        try:
            if key is None:
                key=self.load_key()

            f = Fernet(key)
            print(key, encrypted_message)
            decrypted_message = f.decrypt(encrypted_message).decode("utf-8")
            return decrypted_message

        except Exception as e:
            decrypt_message_encryption = EncyptException(
                "Failed during Decrypting Message in module [{0}] class [{1}] method [{2}]"
                    .format(self.__module__, EncryptData.__name__,
                            self.decrypt_message.__name__))
            raise Exception(decrypt_message_encryption.error_message_detail(str(e), sys))\
                                             from e


    
    def generate_your_encrypted_database_password(self):
        """
        Generates a password for email and encrypt it
        """
        try:
            password = input("Enter your database password: ")
            # Get password from environment variable
            load_dotenv()
            os.environ['DATABASE_PASSWORD'] = password
            key = self.load_key()
            encrypted_password = self.encrypt_message(password,key)

            self.configs['DATABASE']['PASSWORD'] = encrypted_password

            with open('config.yaml', 'w') as f:
                    yaml.dump(self.configs, f)
            
            print("Your encrypted password is saved")
        
        except Exception as e:
            raise Exception(e) from e
    
    def save_credentials_to_env(self, password):
        """
        Saves credentials to environment variable
        """
        try:
            load_dotenv()
            # os.environ['DATABASE_KEY'] = self.load_key()
            os.environ['DATABASE_PASSWORD'] = password


            print("Your credentials are saved")
        except Exception as e:
            raise Exception(e) from e


# if __name__ == "__main__":
#     encrypt_data = EncryptData()
#     encrypt_data.encrypt_message()