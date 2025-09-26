using System;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class PythonMessageReceiver : MonoBehaviour
{
    TcpListener server;
    Thread serverThread;
    string receivedMessage = "";

    void Start()
    {
        serverThread = new Thread(StartServer);
        serverThread.Start();
    }

    void StartServer()
    {
        server = new TcpListener(System.Net.IPAddress.Any, 5052);
        server.Start();
        Debug.Log("Waiting for Python...");

        TcpClient client = server.AcceptTcpClient();
        NetworkStream stream = client.GetStream();

        byte[] buffer = new byte[1024];
        int bytesRead = stream.Read(buffer, 0, buffer.Length);
        receivedMessage = Encoding.UTF8.GetString(buffer, 0, bytesRead);

        Debug.Log("Received from Python: " + receivedMessage);

        client.Close();
    }

    void OnApplicationQuit()
    {
        if (server != null) server.Stop();
        if (serverThread != null) serverThread.Abort();
    }
}
