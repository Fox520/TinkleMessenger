web_file = "web_file"
print("Format")
print("http://example.com/")
data = input("Enter web server address: ")
with open(web_file,"w") as f:
	f.write(data)