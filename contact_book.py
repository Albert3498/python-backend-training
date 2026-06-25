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

def add(contacts):
    Name =input("Name: ")
    Number =input("Number: ")
    contacts.append({"name":Name,"phone":Number})
    save(contacts)
    print("Contacts saved.")
def list_all(contacts):
    if len(contacts)==0:
        print("No Contacts.")
        return
    for c in contacts:
        print(c["name"]," ",c["phone"])
def search(contacts):
    name=input("Search Name")
    results=[c for c in contacts if name.lower() in c["name"].lower()]
    if len(results)==0:
        print("No matches")
    for c in results:
        print(c["name"],"-",c["phone"])
def delete(contacts):
    name=input("Delete name: ")
    new_list=[c for c in contacts if c["name"].lower() != name.lower()]
    if len(new_list)==len(contacts):
        print("Contact not found.")
    else:
        save(new_list)
        contacts.clear()
        contacts.extend(new_list)
        print("Deleted.")
      

while True:
    print("\n1.Add Contact")
    print("2.List all")
    print("3.Exit")
    print("4.Search")
    print("5.Delete")
    choice=input("Choice: ")
    if choice=="1":
        add(contacts)
    elif choice=="2":
        list_all(contacts)
    elif choice=="3":
        break
    elif choice =="4":
        search(contacts)
    elif choice =="5":
        delete(contacts)
    else:
        print("Invalid Choice. ")
