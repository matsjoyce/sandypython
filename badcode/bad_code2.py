load()
print("Starting tests")

for msg, func in func_dict.items():
    print(colorfy(msg + ": ", color="yellow"), end="")
    if func():
        print(colorfy("SUCCEEDED", color="red"))
    else:
        print(colorfy("FAILED", color="green"))

print("Finished tests")
