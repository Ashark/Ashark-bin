const clients = workspace.clientList();
for (var i = 0; i < clients.length; i++) {
  print(clients[i].caption);
}
