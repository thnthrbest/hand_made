using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net.Sockets;
using System.Text;

public class UDPSender : MonoBehaviour
{
    public manange manange;
    UdpClient udpClient;
    public string ip = "127.0.0.1";
    public int port = 5051;

    void Awake()
    {
        udpClient = new UdpClient();
    }

    // Update is called once per frame
    public void Sender(string value)
    {
            byte[] data = Encoding.UTF8.GetBytes(value);
            udpClient.Send(data, data.Length, ip, port);
            Debug.Log("Sent: " + value);
    }
    
    void Exits()
    {
        byte[] data = Encoding.UTF8.GetBytes("stop");
        udpClient.Send(data, data.Length, ip, port);
        Debug.Log("Quit");
    }
    void OnApplicationQuit()
    {
        Exits();
    }

    void OnDestroy()
    {
        Exits();

    }
}
