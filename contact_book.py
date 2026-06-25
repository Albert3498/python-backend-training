#Contact_book
import json
def load():
    try:
        with open("contacts.json","r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
def save(contacts):
    with open("contacts.json","w") as f:
        json.dump(contacts, f)
contacts=load()
print(contacts)
def add(contacts):
    Name : str =input("Name: ")
    Number: int =input("Number: ")
    contacts.append({"name":Name,"phone":Number})
    save(contacts)
    print("Contacts saved.")
add(contacts)
print(contacts)
