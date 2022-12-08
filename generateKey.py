from project_store_entity_layer.encryption.encryption import EncryptData

def secure_credentials():
    obj = EncryptData()
    key = input("Do you want to generate a new key? (y/n)")
    if key == 'y':
        obj.pass_generate_key()
        print("Key has been generated! Save this key into your environment variable: DATABASE_KEY & run this file again")
        return
    else:
        obj.generate_your_encrypted_database_password()

def secure_credentials_env():
    obj = EncryptData()
    # key = input("Do you want to generate a new key? (y/n)")

    obj.pass_generate_key()
    print("Key has been generated! Save this key into your environment variable: DATABASE_KEY & run this file again")

    # Save these keys to the env variables
    # obj.save_credentials_to_env()

    obj.generate_your_encrypted_database_password()

if __name__ == '__main__':
    secure_credentials()